from flask import Flask, Response, abort
import os
import json

# Robust imports for both local development and Vercel deployment
try:
    from .scraper import Scraper
    from .calendar_gen import CalendarGenerator
except ImportError:
    try:
        from scraper import Scraper
        from calendar_gen import CalendarGenerator
    except ImportError:
        import sys
        sys.path.append(os.path.dirname(__file__))
        from scraper import Scraper
        from calendar_gen import CalendarGenerator

# Resolve the absolute path to the 'public' directory
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PUBLIC_DIR = os.path.join(os.path.dirname(CURRENT_DIR), 'public')

# Local development via Flask static_folder
app = Flask(__name__, static_folder=PUBLIC_DIR, static_url_path='')

# Vercel handles the home page (index.html) and static assets via vercel.json.
# This Flask function serves the API and webcal routes.

# API: Only handle the calendar generation
@app.route('/std/<std_id>')
def get_calendar(std_id):
    # Only allow numeric IDs
    if not std_id.isdigit():
        abort(404)
    
    scraper = Scraper(std_id)
    exams = scraper.get_exam_schedule()
    
    if exams is None:
        return Response("Error fetching data from university website. Please check Student ID.", status=500, mimetype='text/plain')
    
    if not exams:
        return Response(f"No exam schedule found for student ID: {std_id}.", status=404, mimetype='text/plain')
        
    generator = CalendarGenerator(exams)
    ical_data = generator.generate()
    
    return Response(
        ical_data,
        mimetype='text/calendar',
        headers={
            "Content-Disposition": f"attachment; filename=exam_schedule_{std_id}.ics",
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Expires": "0"
        }
    )
    
@app.route('/api/preview/<std_id>')
def preview(std_id):
    if not std_id.isdigit():
        abort(404)
    
    scraper = Scraper(std_id)
    exams = scraper.get_exam_schedule()
    
    if exams is None:
        return Response(json.dumps({"error": "Fetch error"}), status=500, mimetype='application/json')
    
    return Response(
        json.dumps(exams, ensure_ascii=False),
        mimetype='application/json',
        headers={
            "Cache-Control": "no-cache, no-store, must-revalidate"
        }
    )

if __name__ == "__main__":
    # Local development support (Using 8080 to avoid macOS AirPlay conflict on 5000)
    app.run(host='0.0.0.0', port=8080, debug=True)
