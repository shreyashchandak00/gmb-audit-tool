# Scoring thresholds
THRESHOLDS = {
    'min_reviews_excellent': 50,
    'min_reviews_good': 25,
    'min_reviews_ok': 10,
    'min_photos_excellent': 10,
    'min_photos_good': 5,
    'min_rating_excellent': 4.5,
    'min_rating_good': 4.0,
    'min_owner_response_rate': 0.5,
    'expected_hours_days': 7,
}

# Brand colors
COLORS = {
    'primary': '#1a56db',
    'primary_light': '#3b82f6',
    'secondary': '#6366f1',
    'accent': '#0ea5e9',
    'success': '#22c55e',
    'warning': '#f97316',
    'danger': '#ef4444',
    'info': '#3b82f6',
    'bg': '#f8fafc',
    'card_bg': '#ffffff',
    'text': '#1e293b',
    'text_muted': '#64748b',
    'border': '#e2e8f0',
}

# Grade scale
GRADES = {
    'A': {'min': 90, 'label': 'Excellent', 'color': '#22c55e'},
    'B': {'min': 80, 'label': 'Good', 'color': '#84cc16'},
    'C': {'min': 70, 'label': 'Average', 'color': '#eab308'},
    'D': {'min': 60, 'label': 'Below Average', 'color': '#f97316'},
    'F': {'min': 0, 'label': 'Needs Work', 'color': '#ef4444'},
}

# Flask config
REPORTS_DIR = 'reports'
HOST = '0.0.0.0'
PORT = 5000
