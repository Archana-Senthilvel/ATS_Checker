import PyPDF2 as pdf

def extract_text_from_pdf(file):
    """Extract text from uploaded PDF file."""
    reader = pdf.PdfReader(file)
    text = ""
    for page in range(len(reader.pages)):
        text += reader.pages[page].extract_text() or ""
    return text

def extract_profile_fields(resume_text):
    """Extract profile information from resume text."""
    import re
    profile = {}
    
    # Extract name (assumed to be at the start of the resume)
    lines = resume_text.split('\n')
    profile['name'] = lines[0].strip() if lines else "Not found"
    
    # Extract email
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    emails = re.findall(email_pattern, resume_text)
    profile['email'] = emails[0] if emails else "Not found"
    
    # Extract phone number
    phone_pattern = r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'
    phones = re.findall(phone_pattern, resume_text)
    profile['phone'] = phones[0] if phones else "Not found"
    
    return profile