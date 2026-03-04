# All Google Maps CSS/XPath selectors in one place.
# When Google changes their DOM, update only this file.

SELECTORS = {
    'business_name': {
        'css': 'h1.DUwDvf',
        'fallback_css': 'div[role="main"] h1',
    },

    'address': {
        'css': 'button[data-item-id="address"] .Io6YTe.fontBodyMedium',
        'fallback_xpath': '//button[contains(@data-item-id, "address")]//div[contains(@class, "fontBodyMedium")]',
        'fallback_css': 'button[data-item-id="address"]',
    },

    'phone': {
        'css': 'button[data-item-id*="phone:tel"] .Io6YTe.fontBodyMedium',
        'fallback_xpath': '//button[contains(@data-item-id, "phone")]//div[contains(@class, "fontBodyMedium")]',
        'fallback_css': 'button[data-item-id*="phone"]',
    },

    'website': {
        'css': 'a[data-item-id="authority"] .Io6YTe.fontBodyMedium',
        'fallback_xpath': '//a[contains(@data-item-id, "authority")]//div[contains(@class, "fontBodyMedium")]',
        'fallback_css': 'a[data-item-id="authority"]',
    },

    'category': {
        'css': 'button[jsaction*="category"] .DkEaL',
        'fallback_css': 'button.DkEaL',
        'fallback_xpath': '//button[contains(@jsaction, "category")]',
    },

    'rating': {
        'css': 'div.F7nice span[aria-hidden="true"]',
        'fallback_css': 'span.ceNzKf[role="img"]',
    },

    'review_count': {
        # Primary: aria-label on the reviews button/link near rating
        'css': 'div.F7nice span[aria-label*="reviews"]',
        'fallback_css': 'span[aria-label*="reviews"]',
        # Also try the parenthesized count text near rating
        'fallback_css2': 'div.F7nice span:last-child',
    },

    'photos_button': {
        'css': 'button[aria-label*="Photo"]',
        'fallback_css': 'button[aria-label*="photo"]',
        'fallback_xpath': '//button[contains(@aria-label, "Photo")]',
    },

    'hours_trigger': {
        # Primary: aria-label based trigger (works on most pages)
        'css': 'button[aria-label*="open hours"]',
        'fallback_css': 'div[data-item-id="oh"] button',
        'fallback_css2': '[data-item-id="oh"]',
        'fallback_xpath': '//button[contains(@aria-label, "open hours") or contains(@aria-label, "Open hours")]',
        'fallback_xpath2': '//div[@data-item-id="oh"]//button',
        # Also try the hours section with clock icon
        'fallback_css3': 'img[src*="schedule"]',
    },

    'hours_table': {
        'css': 'table.eK4R0e tbody tr',
        'fallback_css': 'table.WgFkxc tbody tr',
        'fallback_css2': 'table tbody tr',
        'fallback_xpath': '//table[contains(@class, "eK4R0e")]//tr',
    },

    'hours_row_day': {
        'css': 'td.ylH6lf',
        'fallback_css': 'td:first-child',
    },

    'hours_row_time': {
        'css': 'td.mxowUb',
        'fallback_css': 'td:last-child li',
    },

    'description': {
        'xpath': '//div[contains(@class, "PYvSYb")]',
        'fallback_css': 'div.WeS02d.fontBodyMedium',
        'fallback_xpath': '//div[@role="region"]//div[contains(@class, "WeS02d")]',
    },

    'reviews_tab': {
        'css': 'button[aria-label*="Reviews"]',
        'fallback_css': 'button[aria-label*="review"]',
    },

    'review_items': {
        'css': 'div[data-review-id]',
        'fallback_css': 'div.jftiEf',
    },

    'owner_response': {
        'css': 'div.CDe7pd',
        'fallback_css': 'span.CDe7pd',
    },

    # Consent / cookie banner
    'consent_accept': {
        'css': 'button[aria-label="Accept all"]',
        'fallback_css': 'form[action*="consent"] button',
        'fallback_xpath': '//button[contains(text(), "Accept all")]',
    },
}
