import re
import spacy
from typing import Dict, Any

class LogEntityExtractor:
    """Parses unstructured text logs to extract actionable entities using spaCy and Regex."""
    
    def __init__(self):
        # Load the small spaCy English pipeline
        self.nlp = spacy.load("en_core_web_sm")
        
    def parse_log(self, log_message: str) -> Dict[str, Any]:
        """Extracts log severity level, IP address, status codes, and API routes."""
        doc = self.nlp(log_message)
        
        # Regex patterns for infrastructure identifiers
        ip_pattern = r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'
        status_pattern = r'\b[1-5][0-9]{2}\b'
        route_pattern = r'/(?:[a-zA-Base0-9_]+/)*[a-zA-Base0-9_]*'
        
        # Extract matches
        ip_match = re.search(ip_pattern, log_message)
        status_match = re.search(status_pattern, log_message)
        route_match = re.search(route_pattern, log_message)
        
        # Determine log severity level from text
        level = "UNKNOWN"
        for token in doc:
            if token.text in ["INFO", "WARN", "ERROR", "CRITICAL"]:
                level = token.text
                break
                
        return {
            "raw_log": log_message,
            "severity": level,
            "ip_address": ip_match.group(0) if ip_match else None,
            "status_code": status_match.group(0) if status_match else None,
            "failing_route": route_match.group(0) if route_match else None
        }

if __name__ == "__main__":
    parser = LogEntityExtractor()
    
    sample_log = "ERROR [service=gateway] HTTP 500 failure from IP: 10.0.0.45 route /api/v1/checkout"
    parsed_output = parser.parse_log(sample_log)
    
    print("\n--- Parsed Log Entity Output ---")
    for key, value in parsed_output.items():
        print(f"{key.capitalize()}: {value}")