import re
from sklearn.feature_extraction.text import CountVectorizer
import google.generativeai as genai
from django.conf import settings
import os

# Configure Google AI
genai.configure(api_key=settings.GOOGLE_API_KEY)

def extract_jd_sections(job_description):
    sections = {
        "skills": re.findall(r'\b(Skills|Qualifications):\s*(.*)', job_description, re.IGNORECASE),
        "experience": re.findall(r'\b(Experience|Requirements):\s*(.*)', job_description, re.IGNORECASE),
        "education": re.findall(r'\b(Education|Degree|Certification):\s*(.*)', job_description, re.IGNORECASE),
        "responsibilities": re.findall(r'\b(Responsibilities|Duties):\s*(.*)', job_description, re.IGNORECASE),
    }
    return {k: ' '.join([s[1] for s in v]).lower() for k, v in sections.items()}

# Function to check ATS compliance based on JD sections
def ats_rules_check(resume_text, job_description_sections):
    score = 0
    total_rules = 10  # Number of ATS rules specific to JD matching

    # 1. Skills match based on job description
    jd_skills = job_description_sections["skills"]
    if jd_skills:
        resume_skills = re.findall(r'\b(' + '|'.join(jd_skills.split()) + r')\b', resume_text, re.IGNORECASE)
        if len(resume_skills) >= len(jd_skills.split()) * 0.5:  # Match at least 50% of skills
            score += 10

    # 2. Experience section match
    jd_experience = job_description_sections["experience"]
    if jd_experience and jd_experience in resume_text.lower():
        score += 10

    # 3. Education section match
    jd_education = job_description_sections["education"]
    if jd_education and jd_education in resume_text.lower():
        score += 10

    # 4. Responsibilities or achievements
    jd_responsibilities = job_description_sections["responsibilities"]
    if jd_responsibilities:
        resume_responsibilities = re.findall(r'\b(' + '|'.join(jd_responsibilities.split()) + r')\b', resume_text, re.IGNORECASE)
        if len(resume_responsibilities) >= len(jd_responsibilities.split()) * 0.5:  # Match at least 50% of responsibilities
            score += 10

    # 5. Consistent date format
    if len(re.findall(r'\b(?:\d{2}/\d{4}|\b(?:January|February|March|April|May|June|July|August|September|October|November|December) \d{4})\b', resume_text)) > 1:
        score += 10

    # 6. Bullet points for readability
    if re.search(r'•|\u2022|\u25AA', resume_text):
        score += 10

    # 7. Avoid special characters
    if len(re.findall(r'[!@#%^&*()<>?/\|}{~:]', resume_text)) < 3:
        score += 10

    # 8. Avoids headers/footers - assume plain content check for top text
    header_footer_text = re.findall(r'\b(Phone|Email|LinkedIn)\b', resume_text, re.IGNORECASE)
    if len(header_footer_text) > 2:
        score += 10

    # 9. Use of action verbs and metrics
    if re.search(r'\b(Led|Developed|Improved|Increased|Decreased|Achieved)\b', resume_text, re.IGNORECASE):
        score += 10

    # 10. Basic contact information
    if re.search(r'\b(Name|Phone|Email|LinkedIn)\b', resume_text, re.IGNORECASE):
        score += 10

    return min(score, 100)

# Function to calculate JD match percentage based on keywords
def calculate_jd_match(resume_text, job_description):
    resume_text = re.sub(r'\W', ' ', resume_text.lower())
    job_description = re.sub(r'\W', ' ', job_description.lower())
    vectorizer = CountVectorizer()
    vectorizer.fit([job_description])
    jd_keywords = vectorizer.get_feature_names_out()
    resume_keywords_count = sum(1 for word in jd_keywords if word in resume_text)
    match_percentage = (resume_keywords_count / len(jd_keywords)) * 100 if len(jd_keywords) > 0 else 0
    return round(match_percentage, 2)

# Function to identify red flags
def identify_red_flags(resume_text, job_description_sections):
    red_flags = []
    
    # Extract critical skills from job description
    critical_skills = []
    if job_description_sections.get("preferred skills"):
        critical_skills = [skill.strip() for skill in job_description_sections["skills"].split(',')]

    # Skill gaps
    missing_skills = [skill for skill in critical_skills if skill.lower() not in resume_text.lower()]
    if missing_skills:
        red_flags.append("Skill Gaps: Missing skills " + ", ".join(missing_skills))

    return red_flags

# Function to extract matched skills from the resume
def extract_matched_skills(resume_text, job_description_sections):
    jd_skills = [skill.strip() for skill in job_description_sections["skills"].split(',')]  # Split skills into a list
    matched_skills = [skill for skill in jd_skills if skill.lower() in resume_text.lower()]  # Check for matches
    return matched_skills

def extract_profile_fields(resume_text):
    """Extract comprehensive profile information from resume text."""
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
# Function to calculate overall ATS score
def calculate_overall_score(ats_score, match_percentage, skill_match_score, 
                          experience_match_score, education_match_score, 
                          keyword_density_score, resume_quality_score, bonus_score):
    """Calculate overall score including bonus points."""
    
    base_score = (ats_score + match_percentage + skill_match_score + 
                 experience_match_score + education_match_score + 
                 keyword_density_score + resume_quality_score) // 7
    
    # Add bonus score and ensure the total doesn't exceed 100
    total_score = min(base_score + bonus_score, 100)
    return round(total_score, 2)

# Function to score skill matching
def score_skill_matching(resume_text, job_description_sections):
    jd_skills = job_description_sections["skills"].split(',')
    matched_skills = extract_matched_skills(resume_text, job_description_sections)
    skill_match_score = (len(matched_skills) / len(jd_skills)) * 100 if len(jd_skills) > 0 else 0
    return round(skill_match_score, 2)

# Function to score experience matching
def score_experience_matching(resume_text, job_description_sections):
    jd_experience = job_description_sections["experience"]
    experience_match_score = 100 if jd_experience.lower() in resume_text.lower() else 0
    return experience_match_score

# Function to score education matching
def score_education_matching(resume_text, job_description_sections):
    jd_education = job_description_sections["education"]
    education_match_score = 100 if jd_education.lower() in resume_text.lower() else 0
    return education_match_score

# Function to score keyword density
def score_keyword_density(resume_text, job_description):
    resume_words = resume_text.split()
    job_description_words = job_description.split()
    resume_word_count = len(resume_words)
    job_description_word_count = len(job_description_words)
    keyword_density_score = (resume_word_count / job_description_word_count) * 100 if job_description_word_count > 0 else 0
    return round(keyword_density_score, 2)

# Function to score resume quality
def score_resume_quality(resume_text):
    # Check for spelling and grammar mistakes (using simplified rules)
    # Example error patterns; replace with actual logic or a library for comprehensive checks
    spelling_errors = re.findall(r'\b(?:the|and|of|is|to|in|a)\b', resume_text)
    grammar_errors = re.findall(r'\b(?:your|there|their|its|it\'s)\b', resume_text)

    resume_quality_score = max(0, 100 - (len(spelling_errors) + len(grammar_errors)))
    return resume_quality_score

def parse_ai_response(ai_response):
    """Parse the AI response to extract information about gaps, job changes, and matched skills."""
    # Initialize default values
    has_gaps = False
    has_frequent_changes = False
    matched_skills_count = 0
    in_matched_skills_section = False
    # Split the response into sections
    sections = ai_response.lower().split('\n')
    
    # Process each line
    for line in sections:
        # Check for gaps
        if 'no employment gap' in line or 'no education gap' in line:
            has_gaps = True
        
        # Check for frequent job changes
        if 'no frequent job changes' in line or 'job hopping' in line:
            has_frequent_changes = True
        
        if 'matched skills:' in line or 'matched skills' in line:
            in_matched_skills_section = True
            continue
            
        # Check if we're entering the unmatched skills section (exit matched skills section)
        if 'unmatched skills:' in line or 'unmatched skills' in line:
            in_matched_skills_section = False
            continue
        
        # Count skills in the matched skills section
        if in_matched_skills_section and (line.startswith('*') or line.startswith('-') or line.startswith('•')):
            if len(line.strip('* -•').strip()) > 0:  # Ensure it's not an empty bullet point
                matched_skills_count += 1
    
    return {
        'has_gaps': has_gaps,
        'has_frequent_changes': has_frequent_changes,
        'matched_skills_count': matched_skills_count
    }

def calculate_bonus_score(ai_analysis):
    bonus_score = 0
    
    # Rule 1: No employment or education gaps
    if ai_analysis['has_gaps']:
        bonus_score += 5
    
    # Rule 2: No frequent job changes
    if ai_analysis['has_frequent_changes']:
        bonus_score += 5
    
    # Rule 3: More than 5 matched skills
    if ai_analysis['matched_skills_count'] > 5:
        bonus_score += 5

    return bonus_score

def analyze_with_google_ai(resume_text, job_description):
    prompt = f"""
    Analyze the following resume and job description for employment and education gaps, matched skills, and unmatched skills.

    Resume:
    {resume_text}

    Job Description:
    {job_description}

    Please provide:
    1. Any identified employment or education gaps in the resume (excluding current students or employees). Don't include the expected graduation. Only analyze the education and experience and STRICTLY DON'T INCLUDE INTERNSHIPS and also identify the candidates history of frequent job changes.
    2. A bullet point list of technical skills matched between the resume and job description, formatted as plain text. Strictly Don't include parenthesis. It should be in the format of "Matched skills" as heading and bulletin points of the skills.
    3. A bullet point list of technical skills present in the job description but absent in the resume. Strictly Don't include parenthesis. It should be in the format of "Unmatched skills" as heading and bulletin points of the skills.

    Give in the following structure:
    1.Red flags: In this provide with 3 bulletin points of employment gap,education gap,frequent job changes. Note: if there is a gap then specify it otherwise simple written as no employment gap or no education gap or no frequent job changes and also mention if there are any overlapping.
    2.Matched skills: only include the matched skills and dont use paranthesis.
    3.Unmatched skills: Only include the unmatched skills and dont use paranthesis.
    """
    model = genai.GenerativeModel('gemini-1.5-pro-latest')
    response = model.generate_content([prompt])
    return response.text


