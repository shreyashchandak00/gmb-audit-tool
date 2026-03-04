import os
import json
import uuid
import threading
import logging
from queue import Queue

from flask import Flask, request, jsonify, Response, send_file, render_template

from scraper.google_maps_scraper import GoogleMapsScraper, validate_url
from audit.analyzer import ProfileAuditor
from pdf_report.generator import AuditReportGenerator
from config import REPORTS_DIR, HOST, PORT

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# In-memory task store
tasks = {}

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/audit', methods=['POST'])
def start_audit():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Data is required'}), 400

    url = data.get('url', '').strip()
    apify_data = data.get('apify_data')

    if not url and not apify_data:
        return jsonify({'error': 'URL or Apify data is required'}), 400

    if url and not apify_data:
        if not validate_url(url):
            return jsonify({'error': 'Please enter a valid Google Maps business URL'}), 400

    task_id = str(uuid.uuid4())
    q = Queue()
    tasks[task_id] = {
        'queue': q,
        'status': 'running',
        'pdf_path': None,
        'result': None,
    }

    thread = threading.Thread(
        target=_run_audit_task, args=(task_id, url, apify_data, q), daemon=True
    )
    thread.start()

    return jsonify({'task_id': task_id})


@app.route('/api/progress/<task_id>')
def stream_progress(task_id):
    if task_id not in tasks:
        return jsonify({'error': 'Task not found'}), 404

    def generate():
        q = tasks[task_id]['queue']
        while True:
            msg = q.get()
            yield f"data: {msg}\n\n"
            parsed = json.loads(msg)
            if parsed['status'] in ('complete', 'error'):
                break

    return Response(
        generate(),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'X-Accel-Buffering': 'no',
        }
    )


@app.route('/api/download/<task_id>')
def download(task_id):
    if task_id not in tasks:
        return jsonify({'error': 'Task not found'}), 404

    pdf_path = tasks[task_id].get('pdf_path')
    if not pdf_path or not os.path.exists(pdf_path):
        return jsonify({'error': 'Report not ready'}), 404

    business_name = 'business'
    if tasks[task_id].get('result'):
        name = tasks[task_id]['result'].get('business_name', '')
        if name:
            # Sanitize filename
            business_name = "".join(c for c in name if c.isalnum() or c in (' ', '-', '_')).strip()
            business_name = business_name.replace(' ', '-')[:50]

    return send_file(
        pdf_path,
        as_attachment=True,
        download_name=f'{business_name}-audit-report.pdf'
    )


def _run_audit_task(task_id: str, url: str, apify_data: dict, queue: Queue):
    try:
        def progress_cb(message, percent):
            queue.put(json.dumps({
                'status': 'scraping',
                'message': message,
                'percent': int(percent * 0.7),  # Scraping = 0-70%
            }))

        if apify_data:
            # Bypass scraping, generate BusinessProfile directly from Apify JSON
            queue.put(json.dumps({
                'status': 'scraping',
                'message': 'Parsing Apify data...',
                'percent': 70,
            }))
            
            from scraper.data_models import BusinessProfile, BusinessHours
            
            # Accommodate typical Apify output schema (like compass/google-maps-scraper)
            img_urls = apify_data.get('imageUrls', [])
            photos_count = apify_data.get('photosCount')
            if photos_count is None and img_urls:
                photos_count = len(img_urls)
                
            profile = BusinessProfile(
                url=url or apify_data.get('url', 'https://google.com/maps'),
                name=apify_data.get('title') or apify_data.get('name'),
                address=apify_data.get('address'),
                phone=apify_data.get('phone') or apify_data.get('phoneUnformatted'),
                website=apify_data.get('website'),
                category=apify_data.get('categoryName') or apify_data.get('category'),
                rating=apify_data.get('totalScore') or apify_data.get('rating'),
                review_count=apify_data.get('reviewsCount'),
                photos_count=photos_count,
                description=apify_data.get('description'),
            )
            
            hours_data = apify_data.get('openingHours')
            if hours_data:
                if hasattr(hours_data, 'items'): # dict
                    for day, hours in hours_data.items():
                        profile.hours.append(BusinessHours(day=day, hours=hours))
                elif isinstance(hours_data, list):
                    for h in hours_data:
                        if isinstance(h, dict) and 'day' in h and 'hours' in h:
                            profile.hours.append(BusinessHours(day=h['day'], hours=h['hours']))

        else:
            # Step 1: Scrape
            scraper = GoogleMapsScraper()
            profile = scraper.scrape(url, progress_callback=progress_cb)

        # Step 2: Analyze
        queue.put(json.dumps({
            'status': 'analyzing',
            'message': 'Analyzing profile data...',
            'percent': 75,
        }))

        auditor = ProfileAuditor(profile)
        audit_result = auditor.run_audit()

        # Step 3: Generate PDF
        queue.put(json.dumps({
            'status': 'generating',
            'message': 'Generating PDF report...',
            'percent': 90,
        }))

        os.makedirs(REPORTS_DIR, exist_ok=True)
        pdf_path = os.path.join(REPORTS_DIR, f'{task_id}.pdf')
        generator = AuditReportGenerator()
        generator.generate(audit_result, pdf_path)

        tasks[task_id]['pdf_path'] = pdf_path

        # Build result summary for frontend
        result_data = {
            'business_name': profile.name or 'Unknown Business',
            'category': profile.category or 'Not specified',
            'score': audit_result.score,
            'grade': audit_result.grade,
            'grade_label': audit_result.grade_label,
            'grade_color': audit_result.grade_color,
            'total_issues': len(audit_result.issues),
            'critical_count': audit_result.critical_count,
            'warning_count': audit_result.warning_count,
            'info_count': audit_result.info_count,
            'rating': profile.rating,
            'review_count': profile.review_count,
            'photos_count': profile.photos_count,
            'has_website': bool(profile.website),
            'has_hours': bool(profile.hours),
            'has_description': bool(profile.description),
            'issues': [
                {
                    'title': i.title,
                    'severity': i.severity.value,
                    'description': i.description,
                    'recommendation': i.recommendation,
                    'points': i.points_deducted,
                }
                for i in audit_result.issues
            ],
        }
        tasks[task_id]['result'] = result_data
        tasks[task_id]['status'] = 'complete'

        queue.put(json.dumps({
            'status': 'complete',
            'message': 'Audit complete!',
            'percent': 100,
            'result': result_data,
        }))

    except Exception as e:
        logger.exception(f"Audit task {task_id} failed")
        tasks[task_id]['status'] = 'error'
        queue.put(json.dumps({
            'status': 'error',
            'message': f'Error: {str(e)}',
            'percent': 0,
        }))


if __name__ == '__main__':
    os.makedirs(REPORTS_DIR, exist_ok=True)
    app.run(host=HOST, port=PORT, debug=True, threaded=True)
