import re

class Redactor:
    EMAIL_PATTERN = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
    PHONE_PATTERN = re.compile(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b')
    BEARER_PATTERN = re.compile(r'Bearer\s+[a-zA-Z0-9\-\._~\+\/]+=*')
    
    @classmethod
    def redact(cls, text: str) -> str:
        if not isinstance(text, str):
            return text
            
        redacted = cls.EMAIL_PATTERN.sub('[EMAIL]', text)
        redacted = cls.PHONE_PATTERN.sub('[PHONE]', redacted)
        redacted = cls.BEARER_PATTERN.sub('Bearer [REDACTED]', redacted)
        return redacted

def redact_log_data(data: dict) -> dict:
    cleaned = {}
    for k, v in data.items():
        if isinstance(v, str):
            cleaned[k] = Redactor.redact(v)
        elif isinstance(v, dict):
            cleaned[k] = redact_log_data(v)
        else:
            cleaned[k] = v
    return cleaned
