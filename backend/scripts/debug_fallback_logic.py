
def fallback_categorization(subject, description):
    text = f"{subject} {description}".lower()
    print(f"Analyzing text: '{text}'")
    
    non_complaint_keywords = ["holiday", "calendar", "question", "inquiry", "greeting", "thanks", "checking"]
    is_complaint = True
    
    # Logic from gemini_service.py
    if any(k in text for k in non_complaint_keywords) and not any(k in text for k in ["fail", "error", "broken", "down", "bug"]):
         print("  -> Met heuristic criteria for Non-Complaint")
         is_complaint = False
    else:
         print("  -> Did NOT meet heuristic criteria")
         matched_positive = [k for k in non_complaint_keywords if k in text]
         matched_negative = [k for k in ["fail", "error", "broken", "down", "bug"] if k in text]
         print(f"     Positive matches: {matched_positive}")
         print(f"     Negative matches: {matched_negative}")

    return is_complaint

s = "Holiday Calendar Question"
d = "Hi team, just wanted to check if we have next Friday off for the local holiday? Thanks, John."
result = fallback_categorization(s, d)
print(f"Result: {result}")
