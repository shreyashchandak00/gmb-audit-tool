import os
import re
import time
import shutil
import logging
from typing import Optional, Callable

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException, NoSuchElementException, ElementClickInterceptedException
)
from webdriver_manager.chrome import ChromeDriverManager

from scraper.selectors import SELECTORS
from scraper.data_models import BusinessProfile, BusinessHours

logger = logging.getLogger(__name__)

GMAPS_URL_PATTERNS = [
    re.compile(r'^https?://(www\.)?google\.[a-z.]+/maps/place/.+'),
    re.compile(r'^https?://(www\.)?google\.[a-z.]+/maps/search/.+'),
    re.compile(r'^https?://(www\.)?google\.[a-z.]+/maps\?.*cid=.+'),
    re.compile(r'^https?://maps\.app\.goo\.gl/.+'),
    re.compile(r'^https?://goo\.gl/maps/.+'),
]


def validate_url(url: str) -> bool:
    return any(p.match(url) for p in GMAPS_URL_PATTERNS)


def _is_docker() -> bool:
    """Detect if running inside a Docker container."""
    return os.path.exists('/.dockerenv') or os.environ.get('RENDER', '')


def create_driver() -> webdriver.Chrome:
    options = Options()
    options.add_argument('--headless=new')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--lang=en-US')
    options.add_argument('--disable-blink-features=AutomationControlled')

    # ── Memory-saving flags (critical for 512 MB Render free tier) ──
    options.add_argument('--window-size=1280,720')
    options.add_argument('--single-process')
    options.add_argument('--no-zygote')
    options.add_argument('--no-first-run')
    options.add_argument('--disable-extensions')
    options.add_argument('--disable-software-rasterizer')
    options.add_argument('--disable-setuid-sandbox')
    options.add_argument('--disable-crash-reporter')
    options.add_argument('--disable-background-networking')
    options.add_argument('--dns-prefetch-disable')
    options.add_argument('--remote-debugging-port=0')

    # Aggressive memory reduction
    options.add_argument('--disable-features=VizDisplayCompositor,TranslateUI')
    options.add_argument('--disable-default-apps')
    options.add_argument('--disable-hang-monitor')
    options.add_argument('--disable-popup-blocking')
    options.add_argument('--disable-prompt-on-repost')
    options.add_argument('--disable-sync')
    options.add_argument('--disable-translate')
    options.add_argument('--metrics-recording-only')
    options.add_argument('--safebrowsing-disable-auto-update')
    options.add_argument('--disable-component-update')
    options.add_argument('--disable-domain-reliability')
    options.add_argument('--disable-client-side-phishing-detection')
    options.add_argument('--disable-ipc-flooding-protection')
    options.add_argument('--disable-renderer-backgrounding')
    options.add_argument('--disable-backgrounding-occluded-windows')
    options.add_argument('--disable-breakpad')
    options.add_argument('--disable-logging')
    options.add_argument('--js-flags=--max-old-space-size=128')
    options.add_argument('--renderer-process-limit=1')
    options.add_argument('--memory-pressure-off')

    # Disable loading images to save bandwidth + memory
    prefs = {
        'profile.managed_default_content_settings.images': 2,
        'profile.default_content_setting_values.notifications': 2,
        'profile.managed_default_content_settings.stylesheets': 1,
        'profile.managed_default_content_settings.plugins': 2,
    }
    options.add_experimental_option('prefs', prefs)
    options.add_experimental_option('excludeSwitches', ['enable-automation', 'enable-logging'])
    options.add_experimental_option('useAutomationExtension', False)

    # In Docker, use system-installed Chrome binary
    if _is_docker():
        chrome_path = shutil.which('google-chrome') or shutil.which('google-chrome-stable')
        if chrome_path:
            options.binary_location = chrome_path
            logger.info(f"Using system Chrome at: {chrome_path}")

    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
    except Exception as e:
        logger.warning(f"ChromeDriverManager failed ({e}), trying system chromedriver...")
        chromedriver_path = shutil.which('chromedriver')
        if chromedriver_path:
            service = Service(chromedriver_path)
            driver = webdriver.Chrome(service=service, options=options)
        else:
            driver = webdriver.Chrome(options=options)

    driver.implicitly_wait(3)
    driver.set_page_load_timeout(60)
    return driver


class GoogleMapsScraper:

    def __init__(self):
        self.driver = None

    def scrape(self, url: str, progress_callback: Optional[Callable] = None) -> BusinessProfile:
        if not progress_callback:
            progress_callback = lambda msg, pct: None

        self.driver = create_driver()
        try:
            # Load page
            progress_callback("Loading Google Maps page...", 10)
            self.driver.get(url)
            time.sleep(3)

            # Wait for main content
            try:
                WebDriverWait(self.driver, 15).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'div[role="main"] h1'))
                )
            except TimeoutException:
                # Try alternate wait
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'h1'))
                )

            # Dismiss consent banner if present
            self._dismiss_consent()
            time.sleep(1)

            # Extract basic info
            progress_callback("Extracting business information...", 25)
            name = self._extract_text('business_name')
            address = self._extract_text('address')
            phone = self._extract_text('phone')
            website = self._extract_text('website')
            category = self._extract_text('category')

            # Extract rating and reviews
            progress_callback("Reading ratings and reviews...", 40)
            rating = self._extract_rating()
            review_count = self._extract_review_count()

            # Extract photos count
            progress_callback("Checking photos...", 50)
            photos_count = self._extract_photos_count()

            # Extract business hours
            progress_callback("Extracting business hours...", 60)
            hours = self._extract_hours()

            # Extract description
            progress_callback("Reading business description...", 70)
            description = self._extract_description()

            # Check owner responses
            progress_callback("Analyzing review responses...", 80)
            owner_response_ratio = self._check_owner_responses()

            progress_callback("Data extraction complete!", 100)

            return BusinessProfile(
                url=url,
                name=name,
                address=address,
                phone=phone,
                website=website,
                category=category,
                rating=rating,
                review_count=review_count,
                photos_count=photos_count,
                hours=hours,
                description=description,
                owner_response_ratio=owner_response_ratio,
            )
        finally:
            self.driver.quit()
            self.driver = None

    def _dismiss_consent(self):
        """Dismiss cookie consent banner if present."""
        sel = SELECTORS['consent_accept']
        for key in ['css', 'fallback_css']:
            try:
                btn = self.driver.find_element(By.CSS_SELECTOR, sel[key])
                btn.click()
                time.sleep(1)
                return
            except (NoSuchElementException, ElementClickInterceptedException):
                continue
        # Try xpath fallback
        try:
            btn = self.driver.find_element(By.XPATH, sel['fallback_xpath'])
            btn.click()
            time.sleep(1)
        except (NoSuchElementException, ElementClickInterceptedException):
            pass  # No consent banner

    def _extract_text(self, selector_key: str) -> Optional[str]:
        """Extract text using primary and fallback selectors."""
        sel = SELECTORS[selector_key]

        # Try CSS selectors
        for key in ['css', 'fallback_css']:
            if key not in sel:
                continue
            try:
                element = self.driver.find_element(By.CSS_SELECTOR, sel[key])
                text = element.text.strip()
                if text:
                    return text
            except NoSuchElementException:
                continue

        # Try XPath selectors
        for key in ['fallback_xpath', 'xpath']:
            if key not in sel:
                continue
            try:
                element = self.driver.find_element(By.XPATH, sel[key])
                text = element.text.strip()
                if text:
                    return text
            except NoSuchElementException:
                continue

        logger.warning(f"Could not extract: {selector_key}")
        return None

    def _extract_rating(self) -> Optional[float]:
        """Extract the star rating."""
        text = self._extract_text('rating')
        if text:
            try:
                # Rating text is usually like "4.5" or "4,5"
                return float(text.replace(',', '.'))
            except ValueError:
                pass

        # Try aria-label approach on the role=img span
        sel = SELECTORS['rating']
        if 'fallback_css' in sel:
            try:
                element = self.driver.find_element(By.CSS_SELECTOR, sel['fallback_css'])
                label = element.get_attribute('aria-label') or ''
                match = re.search(r'([\d.,]+)\s*star', label)
                if match:
                    return float(match.group(1).replace(',', '.'))
            except NoSuchElementException:
                pass

        # Try JavaScript to find rating from the page
        try:
            rating_text = self.driver.execute_script("""
                // Look for the rating span near h1
                var nice = document.querySelector('div.F7nice');
                if (nice) {
                    var spans = nice.querySelectorAll('span[aria-hidden="true"]');
                    for (var i = 0; i < spans.length; i++) {
                        var t = spans[i].textContent.trim();
                        if (/^[\\d.,]+$/.test(t)) return t;
                    }
                }
                // Try role=img with star label
                var imgs = document.querySelectorAll('span[role="img"]');
                for (var i = 0; i < imgs.length; i++) {
                    var label = imgs[i].getAttribute('aria-label') || '';
                    var m = label.match(/([\\d.,]+)\\s*star/);
                    if (m) return m[1];
                }
                return null;
            """)
            if rating_text:
                return float(rating_text.replace(',', '.'))
        except Exception:
            pass

        return None

    def _extract_review_count(self) -> Optional[int]:
        """Extract total number of reviews using multiple strategies."""
        # Strategy 1: aria-label based selectors
        sel = SELECTORS['review_count']
        for key in ['css', 'fallback_css']:
            if key not in sel:
                continue
            try:
                element = self.driver.find_element(By.CSS_SELECTOR, sel[key])
                label = element.get_attribute('aria-label') or ''
                match = re.search(r'([\d,]+)\s*review', label)
                if match:
                    return int(match.group(1).replace(',', ''))
                text = element.text.strip()
                nums = re.findall(r'[\d,]+', text)
                if nums:
                    return int(nums[0].replace(',', ''))
            except NoSuchElementException:
                continue

        # Strategy 2: JavaScript to find review count in various DOM locations
        try:
            count = self.driver.execute_script("""
                // Check aria-labels containing "reviews"
                var allElements = document.querySelectorAll('[aria-label*="review"]');
                for (var i = 0; i < allElements.length; i++) {
                    var label = allElements[i].getAttribute('aria-label');
                    var m = label.match(/([\d,]+)\\s*review/);
                    if (m) return parseInt(m[1].replace(',', ''));
                }

                // Check for parenthesized count near rating: "(10)"
                var nice = document.querySelector('div.F7nice');
                if (nice) {
                    var text = nice.textContent;
                    var m = text.match(/\\(([\d,]+)\\)/);
                    if (m) return parseInt(m[1].replace(',', ''));
                    // Also try just extracting all numbers after the rating
                    var spans = nice.querySelectorAll('span');
                    for (var i = 0; i < spans.length; i++) {
                        var t = spans[i].textContent.trim();
                        var m2 = t.match(/\\(([\d,]+)\\)/);
                        if (m2) return parseInt(m2[1].replace(',', ''));
                    }
                }

                // Check buttons with review count
                var buttons = document.querySelectorAll('button');
                for (var i = 0; i < buttons.length; i++) {
                    var label = buttons[i].getAttribute('aria-label') || '';
                    var m = label.match(/([\d,]+)\\s*review/i);
                    if (m) return parseInt(m[1].replace(',', ''));
                    var t = buttons[i].textContent;
                    var m2 = t.match(/([\d,]+)\\s*review/i);
                    if (m2) return parseInt(m2[1].replace(',', ''));
                }

                // Check role="img" spans that may have review info
                var imgs = document.querySelectorAll('span[role="img"]');
                for (var i = 0; i < imgs.length; i++) {
                    var label = imgs[i].getAttribute('aria-label') || '';
                    var m = label.match(/([\d,]+)\\s*review/i);
                    if (m) return parseInt(m[1].replace(',', ''));
                }

                return null;
            """)
            if count is not None:
                return int(count)
        except Exception:
            pass

        # Strategy 3: Try to find review count from the page source
        try:
            source = self.driver.page_source
            # Look for patterns like "10 reviews" or "(10)" near rating context
            match = re.search(r'"userRatingCount":\s*(\d+)', source)
            if match:
                return int(match.group(1))
            match = re.search(r'(\d+)\s+reviews?', source)
            if match:
                return int(match.group(1))
        except Exception:
            pass

        return None

    def _extract_photos_count(self) -> Optional[int]:
        """Extract number of photos from the Photos button label or image count."""
        sel = SELECTORS['photos_button']

        for key in ['css', 'fallback_css']:
            if key not in sel:
                continue
            try:
                element = self.driver.find_element(By.CSS_SELECTOR, sel[key])
                label = element.get_attribute('aria-label') or element.text
                # "Photos (42)" or "42 photos"
                match = re.search(r'(\d+)', label)
                if match:
                    return int(match.group(1))
            except NoSuchElementException:
                continue

        # Try xpath
        if 'fallback_xpath' in sel:
            try:
                element = self.driver.find_element(By.XPATH, sel['fallback_xpath'])
                label = element.get_attribute('aria-label') or element.text
                match = re.search(r'(\d+)', label)
                if match:
                    return int(match.group(1))
            except NoSuchElementException:
                pass

        # Strategy 2: Use JavaScript to search broadly
        try:
            count = self.driver.execute_script("""
                // Check all buttons/links with photo-related text
                var allEls = document.querySelectorAll('button, a');
                for (var i = 0; i < allEls.length; i++) {
                    var label = (allEls[i].getAttribute('aria-label') || '') +
                                ' ' + allEls[i].textContent;
                    var m = label.match(/(\\d+)\\s*photo/i);
                    if (m) return parseInt(m[1]);
                }
                // Check for the cover photo section - count visible images
                var imgs = document.querySelectorAll('button[jsaction] img[src*="googleusercontent"]');
                if (imgs.length > 0) return imgs.length;
                return null;
            """)
            if count is not None:
                return int(count)
        except Exception:
            pass

        # Strategy 3: Check page source for photo count
        try:
            source = self.driver.page_source
            match = re.search(r'"photoCount":\s*(\d+)', source)
            if match:
                return int(match.group(1))
        except Exception:
            pass

        return None

    def _extract_hours(self) -> list[BusinessHours]:
        """Click to expand hours and extract the schedule."""
        hours = []
        sel_trigger = SELECTORS['hours_trigger']

        # Click to expand hours - try all CSS selectors
        expanded = False
        css_keys = [k for k in sel_trigger if k.startswith('css') or k.startswith('fallback_css')]
        for key in css_keys:
            try:
                trigger = self.driver.find_element(By.CSS_SELECTOR, sel_trigger[key])
                self.driver.execute_script("arguments[0].scrollIntoView(true);", trigger)
                time.sleep(0.5)
                self.driver.execute_script("arguments[0].click();", trigger)
                time.sleep(1.5)
                expanded = True
                break
            except (NoSuchElementException, ElementClickInterceptedException):
                continue

        # Try XPath selectors
        if not expanded:
            xpath_keys = [k for k in sel_trigger if 'xpath' in k]
            for key in xpath_keys:
                try:
                    trigger = self.driver.find_element(By.XPATH, sel_trigger[key])
                    self.driver.execute_script("arguments[0].click();", trigger)
                    time.sleep(1.5)
                    expanded = True
                    break
                except (NoSuchElementException, ElementClickInterceptedException):
                    continue

        # Last resort: try finding any element with hours-related aria-label via JS
        if not expanded:
            try:
                expanded = self.driver.execute_script("""
                    var el = document.querySelector('[aria-label*="open hours"]') ||
                             document.querySelector('[aria-label*="Open hours"]') ||
                             document.querySelector('[data-item-id="oh"] button') ||
                             document.querySelector('[data-item-id="oh"]');
                    if (el) { el.click(); return true; }
                    return false;
                """)
                if expanded:
                    time.sleep(1.5)
            except Exception:
                pass

        if not expanded:
            logger.warning("Could not expand hours section")
            return hours

        # Strategy 1: Extract hours from table rows
        sel_table = SELECTORS['hours_table']
        rows = []
        for key in ['css', 'fallback_css', 'fallback_css2']:
            if key not in sel_table:
                continue
            try:
                rows = self.driver.find_elements(By.CSS_SELECTOR, sel_table[key])
                if rows:
                    break
            except NoSuchElementException:
                continue

        if not rows:
            try:
                rows = self.driver.find_elements(By.XPATH, sel_table.get('fallback_xpath', '//table//tr'))
            except NoSuchElementException:
                pass

        for row in rows:
            try:
                cells = row.find_elements(By.TAG_NAME, 'td')
                if len(cells) >= 2:
                    day = cells[0].text.strip()
                    time_text = cells[1].text.strip()
                    if day:
                        hours.append(BusinessHours(day=day, hours=time_text))
            except Exception:
                continue

        # Strategy 2: If no table rows found, try extracting from aria-labels
        # Hours often appear as aria-labels like "Wednesday, 9 am to 5:30 pm, Copy open hours"
        if not hours:
            try:
                hour_elements = self.driver.execute_script("""
                    var results = [];
                    var allEls = document.querySelectorAll('[aria-label*="Copy open hours"]');
                    for (var i = 0; i < allEls.length; i++) {
                        results.push(allEls[i].getAttribute('aria-label'));
                    }
                    // Also try table rows with aria-label
                    var rows = document.querySelectorAll('tr[role="row"]');
                    for (var i = 0; i < rows.length; i++) {
                        var label = rows[i].getAttribute('aria-label');
                        if (label && (label.includes('am') || label.includes('pm') || label.includes('Closed'))) {
                            results.push(label);
                        }
                    }
                    return results;
                """)
                if hour_elements:
                    for label in hour_elements:
                        if not label:
                            continue
                        # Parse: "Wednesday, 9 am to 5:30 pm, Copy open hours"
                        # or "Sunday, Closed, Copy open hours"
                        clean = label.replace(', Copy open hours', '').replace(',Copy open hours', '')
                        parts = clean.split(',', 1)
                        if len(parts) == 2:
                            day = parts[0].strip()
                            time_text = parts[1].strip()
                            if day:
                                hours.append(BusinessHours(day=day, hours=time_text))
                        elif len(parts) == 1:
                            # Try to split on first space that follows a day name
                            text = parts[0].strip()
                            for day_name in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']:
                                if text.startswith(day_name):
                                    time_text = text[len(day_name):].strip()
                                    hours.append(BusinessHours(day=day_name, hours=time_text or 'Not specified'))
                                    break
            except Exception as e:
                logger.warning(f"Failed to extract hours from aria-labels: {e}")

        # Strategy 3: Extract from any visible text that looks like hours
        if not hours:
            try:
                hour_data = self.driver.execute_script("""
                    var results = [];
                    var days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];
                    // Look through all table cells
                    var tables = document.querySelectorAll('table');
                    for (var t = 0; t < tables.length; t++) {
                        var trs = tables[t].querySelectorAll('tr');
                        for (var i = 0; i < trs.length; i++) {
                            var text = trs[i].textContent.trim();
                            for (var d = 0; d < days.length; d++) {
                                if (text.indexOf(days[d]) !== -1) {
                                    var timeText = text.replace(days[d], '').trim();
                                    results.push({day: days[d], hours: timeText});
                                    break;
                                }
                            }
                        }
                    }
                    return results;
                """)
                if hour_data:
                    for item in hour_data:
                        if item.get('day'):
                            hours.append(BusinessHours(day=item['day'], hours=item.get('hours', '')))
            except Exception:
                pass

        return hours

    def _extract_description(self) -> Optional[str]:
        """Extract the business description/about section."""
        sel = SELECTORS['description']

        # Try xpath first (primary for description)
        for key in ['xpath', 'fallback_xpath']:
            if key not in sel:
                continue
            try:
                element = self.driver.find_element(By.XPATH, sel[key])
                text = element.text.strip()
                if text:
                    return text
            except NoSuchElementException:
                continue

        # Try CSS
        if 'fallback_css' in sel:
            try:
                element = self.driver.find_element(By.CSS_SELECTOR, sel['fallback_css'])
                text = element.text.strip()
                if text:
                    return text
            except NoSuchElementException:
                pass

        # Try clicking the "About" tab to find description there
        try:
            about_tab = self.driver.find_element(
                By.XPATH, '//button[contains(@aria-label, "About")]'
            )
            self.driver.execute_script("arguments[0].click();", about_tab)
            time.sleep(1.5)

            # After clicking About, look for description text
            for key in ['xpath', 'fallback_xpath', 'fallback_css']:
                if key not in sel:
                    continue
                try:
                    if 'xpath' in key:
                        element = self.driver.find_element(By.XPATH, sel[key])
                    else:
                        element = self.driver.find_element(By.CSS_SELECTOR, sel[key])
                    text = element.text.strip()
                    if text:
                        # Navigate back to Overview tab
                        try:
                            overview = self.driver.find_element(
                                By.XPATH, '//button[contains(@aria-label, "Overview")]'
                            )
                            self.driver.execute_script("arguments[0].click();", overview)
                            time.sleep(0.5)
                        except NoSuchElementException:
                            pass
                        return text
                except NoSuchElementException:
                    continue

            # Navigate back
            try:
                overview = self.driver.find_element(
                    By.XPATH, '//button[contains(@aria-label, "Overview")]'
                )
                self.driver.execute_script("arguments[0].click();", overview)
                time.sleep(0.5)
            except NoSuchElementException:
                pass

        except (NoSuchElementException, ElementClickInterceptedException):
            pass

        return None

    def _check_owner_responses(self) -> Optional[float]:
        """Navigate to reviews tab and check owner response rate."""
        sel_tab = SELECTORS['reviews_tab']

        # First check if Reviews tab exists at all
        has_reviews_tab = False
        for key in ['css', 'fallback_css']:
            if key not in sel_tab:
                continue
            try:
                self.driver.find_element(By.CSS_SELECTOR, sel_tab[key])
                has_reviews_tab = True
                break
            except NoSuchElementException:
                continue

        # Also check via JS
        if not has_reviews_tab:
            try:
                has_reviews_tab = self.driver.execute_script("""
                    var tabs = document.querySelectorAll('button[role="tab"]');
                    for (var i = 0; i < tabs.length; i++) {
                        var label = (tabs[i].getAttribute('aria-label') || '') + tabs[i].textContent;
                        if (/review/i.test(label)) return true;
                    }
                    return false;
                """)
            except Exception:
                pass

        if not has_reviews_tab:
            logger.info("No Reviews tab found - business may be unclaimed or have no reviews")
            return None

        # Click reviews tab
        clicked = False
        for key in ['css', 'fallback_css']:
            if key not in sel_tab:
                continue
            try:
                tab = self.driver.find_element(By.CSS_SELECTOR, sel_tab[key])
                self.driver.execute_script("arguments[0].scrollIntoView(true);", tab)
                time.sleep(0.5)
                self.driver.execute_script("arguments[0].click();", tab)
                time.sleep(2)
                clicked = True
                break
            except (NoSuchElementException, ElementClickInterceptedException):
                continue

        if not clicked:
            return None

        # Wait for reviews to load
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, SELECTORS['review_items']['css'])
                )
            )
        except TimeoutException:
            return None

        # Count reviews and owner responses
        sel_reviews = SELECTORS['review_items']
        sel_response = SELECTORS['owner_response']

        reviews = []
        for key in ['css', 'fallback_css']:
            if key not in sel_reviews:
                continue
            try:
                reviews = self.driver.find_elements(By.CSS_SELECTOR, sel_reviews[key])
                if reviews:
                    break
            except NoSuchElementException:
                continue

        if not reviews:
            return None

        # Scroll to load more reviews (load up to ~10 for sampling)
        scrollable = None
        try:
            scrollable = self.driver.find_element(
                By.CSS_SELECTOR, 'div.m6QErb.DxyBCb'
            )
        except NoSuchElementException:
            # Try alternate scrollable container
            try:
                scrollable = self.driver.find_element(
                    By.CSS_SELECTOR, 'div.m6QErb.WNBkOb.XiKgde'
                )
            except NoSuchElementException:
                pass

        if scrollable:
            for _ in range(3):
                self.driver.execute_script(
                    "arguments[0].scrollTop = arguments[0].scrollHeight", scrollable
                )
                time.sleep(1)

        # Re-fetch reviews after scrolling
        for key in ['css', 'fallback_css']:
            if key not in sel_reviews:
                continue
            try:
                reviews = self.driver.find_elements(By.CSS_SELECTOR, sel_reviews[key])
                if reviews:
                    break
            except NoSuchElementException:
                continue

        total = len(reviews)
        if total == 0:
            return 0.0

        responded = 0
        for review in reviews:
            for key in ['css', 'fallback_css']:
                if key not in sel_response:
                    continue
                try:
                    review.find_element(By.CSS_SELECTOR, sel_response[key])
                    responded += 1
                    break
                except NoSuchElementException:
                    continue

        return responded / total
