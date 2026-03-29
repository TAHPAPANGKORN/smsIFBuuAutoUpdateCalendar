import requests
from bs4 import BeautifulSoup
import re
import json

class Scraper:
    def __init__(self, student_id):
        self.student_id = student_id
        self.base_url = "https://sms.informatics.buu.ac.th"
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        })

    def get_token(self):
        """Fetch the CSRF token from the homepage."""
        response = self.session.get(self.base_url)
        soup = BeautifulSoup(response.text, 'html.parser')
        token_input = soup.find('input', {'name': '_token'})
        if token_input:
            return token_input['value']
        return None

    def get_exam_schedule(self):
        """Fetch and parse the exam schedule."""
        token = self.get_token()
        if not token:
            print("Error: Could not find CSRF token.")
            return []
        
        print(f"[*] Found CSRF token: {token[:10]}...")

        payload = {
            '_token': token,
            'std_id': self.student_id
        }

        response = self.session.post(f"{self.base_url}/student-data", data=payload)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # New approach: Parse from the JSON embedded in the script tag
        scripts = soup.find_all('script')
        for script in scripts:
            if not script.string:
                continue
            if 'std_data: JSON.parse(JSON.stringify([' in script.string:
                try:
                    # Extract the JSON array string
                    start_marker = 'std_data: JSON.parse(JSON.stringify('
                    end_marker = '))'
                    start_idx = script.string.find(start_marker) + len(start_marker)
                    end_idx = script.string.find(end_marker, start_idx)
                    json_str = script.string[start_idx:end_idx].strip()
                    
                    data = json.loads(json_str)
                    exams = []
                    for item in data:
                        exams.append({
                            'date': item.get('date'), # "2026-03-30"
                            'subject': f"{item.get('sub_name')} ({item.get('sub_code')})",
                            'time': f"{item.get('exam_time_start')} - {item.get('exam_time_end')}",
                            'room': item.get('room_name'),
                            'seat': item.get('exs_seat')
                        })
                    return exams
                except Exception as e:
                    print(f"Error parsing JSON from script: {e}")
                    break
        
        # Fallback to HTML parsing if script method fails
        exams = []
        date_divs = soup.find_all('strong', string=re.compile(r'วันที่'))
        
        for date_div in date_divs:
            # Extract date text, e.g., "30 มี.ค. 2569"
            date_text = date_div.get_text(strip=True)
            
            # Find the table right after this div or within its parent's next sibling
            # Based on common Laravel/Bootstrap patterns, it might be the next sibling
            table = date_div.find_next('table', class_='table-striped')
            if not table:
                continue
                
            rows = table.find_all('tr')[1:] # Skip header
            for row in rows:
                cols = row.find_all('td')
                if len(cols) < 4:
                    continue
                
                # Column structure: Subject, Time, Room, Seat
                subject = cols[0].get_text(strip=True)
                time_range = cols[1].get_text(strip=True) # e.g., "13:00 - 16:00"
                room = cols[2].get_text(strip=True)
                seat = cols[3].get_text(strip=True)
                
                exams.append({
                    'date': date_text,
                    'subject': subject,
                    'time': time_range,
                    'room': room,
                    'seat': seat
                })
                
        return exams

if __name__ == "__main__":
    import json
    scraper = Scraper("67160072")
    data = scraper.get_exam_schedule()
    print(json.dumps(data, indent=2, ensure_ascii=False))
