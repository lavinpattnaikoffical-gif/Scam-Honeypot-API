import re

SCAM_KEYWORDS = ["verify", "block", "suspend", "kyc", "pan", "upi", "credit card", "urgent", "refund", "winner"]

def detect_scam(text: str) -> bool:
    return any(word in text.lower() for word in SCAM_KEYWORDS)

def extract_intelligence(text: str) -> dict:
    intel = {
        "bankAccounts": [],
        "upiIds": [],
        "phishingLinks": [],
        "phoneNumbers": [],
        "suspiciousKeywords": []
    }
    
    upi_pattern = r'[a-zA-Z0-9.\-_]{2,256}@[a-zA-Z]{2,64}'
    phone_pattern = r'(?:\+91[\-\s]?)?[6-9]\d{9}'
    url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    
    intel["upiIds"] = re.findall(upi_pattern, text)
    intel["phoneNumbers"] = re.findall(phone_pattern, text)
    intel["phishingLinks"] = re.findall(url_pattern, text)
    intel["suspiciousKeywords"] = [w for w in SCAM_KEYWORDS if w in text.lower()]
    
    return intel
