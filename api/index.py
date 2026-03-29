from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from scraper import Scraper
from calendar_gen import CalendarGenerator

def get_calendar_response(std_id):
    """Core logic to fetch data and return ICS data or error."""
    try:
        # 1. Scrape data
        scraper = Scraper(std_id)
        exams = scraper.get_exam_schedule()

        if not exams:
            return 404, f"ไม่พบข้อมูลตารางสอบสำหรับรหัส {std_id}".encode()

        # 2. Generate Calendar bytes
        gen = CalendarGenerator(exams)
        return 200, gen.generate()
    except Exception as e:
        return 500, f"Server Error: {str(e)}".encode()

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Extract std_id from query params (remapped by vercel.json)
        query = parse_qs(urlparse(self.path).query)
        std_id = query.get('std_id', [None])[0]

        if not std_id:
            self.send_response(400)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write("Missing Student ID.".encode())
            return

        status, data = get_calendar_response(std_id)
        
        self.send_response(status)
        if status == 200:
            self.send_header('Content-type', 'text/calendar; charset=utf-8')
            self.send_header('Content-Disposition', f'attachment; filename="exam_{std_id}.ics"')
        else:
            self.send_header('Content-type', 'text/plain; charset=utf-8')
        self.end_headers()
        self.wfile.write(data)
