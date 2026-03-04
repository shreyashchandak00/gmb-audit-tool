const form = document.getElementById('audit-form');
const urlInput = document.getElementById('url-input');
const submitBtn = document.getElementById('submit-btn');
const btnText = submitBtn.querySelector('.btn-text');
const btnLoader = submitBtn.querySelector('.btn-loader');
const errorMessage = document.getElementById('error-message');
const progressSection = document.getElementById('progress-section');
const progressBar = document.getElementById('progress-bar');
const progressText = document.getElementById('progress-text');
const progressSteps = document.getElementById('progress-steps');
const resultsSection = document.getElementById('results-section');
const downloadBtn = document.getElementById('download-btn');

let currentTaskId = null;

// URL validation
function isValidGoogleMapsUrl(url) {
    return /google\.[a-z.]+\/maps\/(place|search)\//i.test(url) ||
           /google\.[a-z.]+\/maps\?.*cid=/i.test(url) ||
           /maps\.app\.goo\.gl\//i.test(url) ||
           /goo\.gl\/maps\//i.test(url);
}

function normalizeGoogleMapsUrl(url) {
    try {
        const u = new URL(url);
        const placeId =
            u.searchParams.get('query_place_id') ||
            u.searchParams.get('q_place_id') ||
            u.searchParams.get('cid');

        if (placeId) {
            return `https://www.google.com/maps/place/?q=place_id:${placeId}`;
        }
    } catch (_) {
        // Keep original URL if parsing fails
    }
    return url;
}

// Show/hide helpers
function showError(msg) {
    errorMessage.textContent = msg;
    errorMessage.style.display = 'block';
    setTimeout(() => { errorMessage.style.display = 'none'; }, 5000);
}

function setLoading(loading) {
    submitBtn.disabled = loading;
    btnText.style.display = loading ? 'none' : 'inline';
    btnLoader.style.display = loading ? 'inline-flex' : 'none';
    urlInput.disabled = loading;
}

function addProgressStep(message, active = false) {
    // Remove "active" class from previous steps
    const existing = progressSteps.querySelectorAll('.progress-step');
    existing.forEach(el => el.classList.remove('active'));

    const step = document.createElement('div');
    step.className = 'progress-step' + (active ? ' active' : '');
    step.textContent = message;
    progressSteps.appendChild(step);
}

function updateProgress(percent, message) {
    progressBar.style.width = percent + '%';
    progressText.textContent = message;
}

// Render results
function renderResults(result) {
    // Business name and category
    document.getElementById('business-name').textContent = result.business_name;
    document.getElementById('business-category').textContent = result.category;

    // Score circle animation
    const scoreCircle = document.getElementById('score-circle');
    const circumference = 2 * Math.PI * 52; // r=52
    const offset = circumference - (result.score / 100) * circumference;
    scoreCircle.style.strokeDashoffset = offset;

    // Score number animation
    const scoreNumber = document.getElementById('score-number');
    animateNumber(scoreNumber, 0, result.score, 1200);

    // Grade badge
    const gradeBadge = document.getElementById('grade-badge');
    gradeBadge.textContent = result.grade + ' - ' + result.grade_label;

    // Stats
    const ratingValue = document.getElementById('stat-rating-value');
    const reviewsValue = document.getElementById('stat-reviews-value');
    const photosValue = document.getElementById('stat-photos-value');
    const websiteValue = document.getElementById('stat-website-value');

    ratingValue.textContent = result.rating ? result.rating.toFixed(1) : 'N/A';
    reviewsValue.textContent = result.review_count;
    photosValue.textContent = result.photos_count;
    websiteValue.textContent = result.has_website ? 'Yes' : 'No';

    // Color coding stats
    const ratingCard = document.getElementById('stat-rating');
    if (result.rating && result.rating >= 4.0) ratingCard.className = 'stat-card good';
    else if (result.rating && result.rating >= 3.0) ratingCard.className = 'stat-card warning';
    else ratingCard.className = 'stat-card bad';

    const websiteCard = document.getElementById('stat-website');
    websiteCard.className = result.has_website ? 'stat-card good' : 'stat-card bad';

    // Issue count badge
    const issueCount = document.getElementById('issue-count');
    issueCount.textContent = result.total_issues;
    issueCount.className = result.total_issues === 0 ? 'issue-count zero' : 'issue-count';

    // Issues list
    const issuesList = document.getElementById('issues-list');
    issuesList.innerHTML = '';

    if (result.issues.length === 0) {
        issuesList.innerHTML = '<p style="color: var(--success); text-align: center; padding: 20px;">No issues found! Your profile looks great.</p>';
    } else {
        result.issues.forEach(issue => {
            const item = document.createElement('div');
            item.className = 'issue-item ' + issue.severity;
            item.innerHTML = `
                <div class="issue-header">
                    <span class="issue-title">${escapeHtml(issue.title)}</span>
                    <span class="severity-badge ${issue.severity}">${issue.severity}</span>
                </div>
                <p class="issue-description">${escapeHtml(issue.description)}</p>
                <div class="issue-recommendation">
                    <strong>Recommendation:</strong>
                    ${escapeHtml(issue.recommendation)}
                </div>
            `;
            issuesList.appendChild(item);
        });
    }

    // Show results section
    resultsSection.style.display = 'block';
    resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function animateNumber(element, start, end, duration) {
    const range = end - start;
    const startTime = performance.now();

    function step(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);
        // Ease out cubic
        const eased = 1 - Math.pow(1 - progress, 3);
        element.textContent = Math.round(start + range * eased);
        if (progress < 1) requestAnimationFrame(step);
    }
    requestAnimationFrame(step);
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Form submission
form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const url = urlInput.value.trim();

    if (!url) {
        showError('Please enter a Google Maps URL');
        return;
    }

    if (!isValidGoogleMapsUrl(url)) {
        showError('Please enter a valid Google Maps business URL (e.g., https://www.google.com/maps/place/...)');
        return;
    }

    const normalizedUrl = normalizeGoogleMapsUrl(url);
    if (normalizedUrl !== url) {
        // Show users the exact URL shape being used for a more stable scrape.
        urlInput.value = normalizedUrl;
    }

    // Reset state
    errorMessage.style.display = 'none';
    resultsSection.style.display = 'none';
    progressSteps.innerHTML = '';
    progressBar.style.width = '0%';

    setLoading(true);
    progressSection.style.display = 'block';
    progressSection.scrollIntoView({ behavior: 'smooth' });

    try {
        // Start audit
        const response = await fetch('/api/audit', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ url: normalizedUrl }),
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || 'Failed to start audit');
        }

        currentTaskId = data.task_id;

        // Connect to SSE for progress updates
        const eventSource = new EventSource('/api/progress/' + currentTaskId);
        let lastMessage = '';

        eventSource.onmessage = (event) => {
            const update = JSON.parse(event.data);
            updateProgress(update.percent, update.message);

            // Add step if message changed
            if (update.message !== lastMessage) {
                addProgressStep(update.message, update.status !== 'complete' && update.status !== 'error');
                lastMessage = update.message;
            }

            if (update.status === 'complete') {
                eventSource.close();
                setLoading(false);
                progressSection.style.display = 'none';
                renderResults(update.result);
            } else if (update.status === 'error') {
                eventSource.close();
                setLoading(false);
                progressSection.style.display = 'none';
                showError(update.message);
            }
        };

        eventSource.onerror = () => {
            eventSource.close();
            setLoading(false);
            progressSection.style.display = 'none';
            showError('Connection lost. Please try again.');
        };

    } catch (err) {
        setLoading(false);
        progressSection.style.display = 'none';
        showError(err.message);
    }
});

// Download button
downloadBtn.addEventListener('click', () => {
    if (currentTaskId) {
        window.location.href = '/api/download/' + currentTaskId;
    }
});
