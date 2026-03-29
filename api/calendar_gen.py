from icalendar import Calendar, Event
from datetime import datetime
import pytz

class CalendarGenerator:
    MONTH_MAP = {
        "ม.ค.": 1, "ก.พ.": 2, "มี.ค.": 3, "เม.ย.": 4,
        "พ.ค.": 5, "มิ.ย.": 6, "ก.ค.": 7, "ส.ค.": 8,
        "ก.ย.": 9, "ต.ค.": 10, "พ.ย.": 11, "ธ.ค.": 12
    }

    def __init__(self, exams):
        self.exams = exams
        self.timezone = pytz.timezone("Asia/Bangkok")

    def parse_date(self, date_str):
        """Parse '30 มี.ค. 2569' or '2026-03-30' to datetime date object."""
        if '-' in date_str:
            # Assume YYYY-MM-DD
            try:
                return datetime.strptime(date_str, "%Y-%m-%d")
            except ValueError:
                pass
                
        parts = date_str.split()
        if len(parts) >= 3:
            day = int(parts[0])
            month_str = parts[1]
            year = int(parts[2]) - 543 # Buddhist Era to CE
            month = self.MONTH_MAP.get(month_str, 1)
            return datetime(year, month, day)
        return None

    def parse_time(self, date_obj, time_str):
        """Parse '13:00 - 16:00' and combine with date_obj."""
        parts = time_str.split('-')
        if len(parts) < 2:
            return None, None
            
        start_time_str = parts[0].strip()
        end_time_str = parts[1].strip()
        
        start_dt = self.timezone.localize(datetime.combine(date_obj.date(), datetime.strptime(start_time_str, "%H:%M").time()))
        end_dt = self.timezone.localize(datetime.combine(date_obj.date(), datetime.strptime(end_time_str, "%H:%M").time()))
        
        return start_dt, end_dt

    def generate(self, output_file=None):
        cal = Calendar()
        cal.add('prodid', '-//Exam Schedule Scraper//BUU//')
        cal.add('version', '2.0')

        for exam in self.exams:
            date_obj = self.parse_date(exam['date'])
            if not date_obj:
                continue
                
            start_dt, end_dt = self.parse_time(date_obj, exam['time'])
            if not start_dt:
                continue
                
            event = Event()
            event.add('summary', f"Exam: {exam['subject']}")
            event.add('dtstart', start_dt)
            event.add('dtend', end_dt)
            event.add('location', f"Room: {exam['room']}, Seat: {exam['seat']}")
            event.add('description', f"Subject: {exam['subject']}\nRoom: {exam['room']}\nSeat: {exam['seat']}")
            
            # Add UID (Mandatory for Google Calendar and others)
            # Use student_id + date + subject info for absolute uniqueness
            sub_id = exam['subject'].split('(')[-1].strip(')') if '(' in exam['subject'] else 'sub'
            uid = f"{exam['date']}-{sub_id}@buu-exam-sync"
            event.add('uid', uid)
            
            cal.add_component(event)

        ical_data = cal.to_ical()
        
        if output_file:
            with open(output_file, 'wb') as f:
                f.write(ical_data)
        
        return ical_data

if __name__ == "__main__":
    # Test data
    test_exams = [{
        'date': '30 มี.ค. 2569',
        'subject': 'Algorithm Design',
        'time': '13:00 - 16:00',
        'room': 'IF-11M280',
        'seat': 'I9'
    }]
    gen = CalendarGenerator(test_exams)
    gen.generate("test.ics")
