import sys
import os

# Add current directory to path
sys.path.append(os.getcwd())

from api.index import get_calendar_response

def test_logic(std_id):
    print(f"[*] Testing Logic for ID: {std_id}")
    
    status, data = get_calendar_response(std_id)
    
    print(f"[+] Response Status: {status}")
    
    if status == 200:
        print(f"[+] Success! Generated {len(data)} bytes of .ics data.")
        if len(data) > 100:
            print("[+] Data sample: " + data[:100].decode('utf-8', errors='ignore').replace('\n', ' '))
    else:
        print(f"[!] Failed with status: {status}")
        print(f"[!] Message: {data.decode('utf-8', errors='ignore')}")

if __name__ == "__main__":
    sid = sys.argv[1] if len(sys.argv) > 1 else "67160072"
    test_logic(sid)
