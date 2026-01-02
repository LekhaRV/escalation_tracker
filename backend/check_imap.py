
import os
import imaplib
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

host = os.getenv("EMAIL_HOST")
port = os.getenv("EMAIL_PORT")
username = os.getenv("EMAIL_USERNAME")
password = os.getenv("EMAIL_PASSWORD")

print(f"Checking IMAP for {username} at {host}:{port}...")

if not all([host, port, username, password]):
    print("❌ ERROR: Missing email configuration in .env")
    exit(1)

try:
    mail = imaplib.IMAP4_SSL(host, int(port))
    mail.login(username, password)
    mail.select("inbox")
    
    status, messages = mail.search(None, "UNSEEN")
    
    if status != "OK":
        print("❌ ERROR: Failed to search emails")
        exit(1)
        
    email_ids = messages[0].split()
    print(f"✅ SUCCESS: Connected to IMAP. Found {len(email_ids)} UNSEEN emails.")
    
    if len(email_ids) > 0:
        print("Latest 3 Unseen Email IDs:", [e.decode() for e in email_ids[-3:]])
        
    mail.logout()
    
except Exception as e:
    print(f"❌ ERROR: Connection failed: {str(e)}")
