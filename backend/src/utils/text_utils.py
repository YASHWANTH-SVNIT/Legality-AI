import re

def clean_text(text: str) -> str:

    text = text.replace('\x00', '')
    # Non-breaking space
    text = text.replace('\u200b', '')  
    # Collapse multiple spaces
    text = re.sub(r' {2,}', ' ', text)
    
    # Normalize newlines (max 2 consecutive)
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    # Remove lines with only whitespace
    lines = text.split('\n')
    lines = [line if line.strip() else '' for line in lines]
    text = '\n'.join(lines)
    
    return text.strip()

def sanitize_for_llm(text: str) -> str:
    dangerous_patterns = [
        r'\[SYSTEM[^\]]*\]',
        r'\[INSTRUCTION[^\]]*\]',
        r'IGNORE\s+PREVIOUS',
        r'DISREGARD\s+(?:ALL|PREVIOUS)',
        r'AI\s+REVIEWER:',
    ]
    
    sanitized = text
    for pattern in dangerous_patterns:
        sanitized = re.sub(pattern, '[REDACTED]', sanitized, flags=re.IGNORECASE)
    
    return sanitized

def truncate_for_context(text: str, max_tokens: int = 500) -> str:

    max_chars = max_tokens * 4
    if len(text) <= max_chars:
        return text
    
    truncated = text[:max_chars]
    last_period = truncated.rfind('.')
    
    if last_period > max_chars * 0.8:  
        return truncated[:last_period + 1] + "..."
    else:
        return truncated + "..."