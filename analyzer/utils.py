import re
from pypdf import PdfReader

# Comprehensive Skill Taxonomy grouped by domain
SKILLS_TAXONOMY = {
    # Frontend
    'HTML': r'\bhtml(?:5)?\b',
    'CSS': r'\bcss(?:3)?\b',
    'JavaScript': r'\bjavascript\b|\bjs\b',
    'TypeScript': r'\btypescript\b|\bts\b',
    'React': r'\breact(?:\.js)?\b',
    'Angular': r'\bangular(?:\.js)?\b',
    'Vue': r'\bvue(?:\.js)?\b',
    'Svelte': r'\bsvelte\b',
    'Next.js': r'\bnext(?:\.js)?\b',
    'Redux': r'\bredux\b',
    'Webpack': r'\bwebpack\b',
    'Sass': r'\bsass\b|\bscss\b',
    'Tailwind CSS': r'\btailwind\b',
    'Bootstrap': r'\bbootstrap\b',
    
    # Backend
    'Python': r'\bpython\b',
    'Django': r'\bdjango\b',
    'Flask': r'\bflask\b',
    'FastAPI': r'\bfastapi\b',
    'Java': r'\bjava\b',
    'Spring Boot': r'\bspring\s*boot\b|\bspring\b',
    'Node.js': r'\bnode(?:\.js)?\b',
    'Express.js': r'\bexpress(?:\.js)?\b',
    'Go': r'\bgo(?:lang)?\b',
    'Ruby': r'\bruby\b',
    'Ruby on Rails': r'\brails\b|\bruby\s*on\s*rails\b',
    'PHP': r'\bphp\b',
    'Laravel': r'\blaravel\b',
    'C#': r'(?:^|\s|\b)c#(?:\b|\s|$)',
    'ASP.NET': r'\basp\.net\b',
    'C++': r'(?:^|\s|\b)c\+\+(?:\b|\s|$)',
    'C': r'(?:^|\s|\b)c(?:\b|\s|$)',
    
    # Database
    'SQL': r'\bsql\b',
    'MySQL': r'\bmysql\b',
    'PostgreSQL': r'\bpostgresql\b|\bpostgres\b',
    'MongoDB': r'\bmongodb\b|\bmongo\b',
    'Redis': r'\bredis\b',
    'SQLite': r'\bsqlite\b',
    'Oracle': r'\boracle\b',
    'Cassandra': r'\bcassandra\b',
    'DynamoDB': r'\bdynamodb\b',
    'Firebase': r'\bfirebase\b',
    
    # Cloud & DevOps
    'AWS': r'\baws\b|\bamazon\s*web\s*services\b',
    'Azure': r'\bazure\b',
    'Google Cloud': r'\bgcp\b|\bgoogle\s*cloud\b',
    'Docker': r'\bdocker\b',
    'Kubernetes': r'\bkubernetes\b|\bk8s\b',
    'Jenkins': r'\bjenkins\b',
    'Git': r'\bgit\b',
    'GitHub': r'\bgithub\b',
    'GitLab': r'\bgitlab\b',
    'CI/CD': r'\bci/cd\b|\bcontinuous\s*integration\b',
    'Terraform': r'\bterraform\b',
    'Ansible': r'\bansible\b',
    'Linux': r'\blinux\b',
    'Bash': r'\bbash\b|\bshell\s*scripting\b',
    'Nginx': r'\bnginx\b',
    
    # Data Science & AI
    'Machine Learning': r'\bmachine\s*learning\b|\bml\b',
    'Deep Learning': r'\bdeep\s*learning\b|\bdl\b',
    'Artificial Intelligence': r'\bartificial\s*intelligence\b|\bai\b',
    'NLP': r'\bnlp\b|\bnatural\s*language\s*processing\b',
    'Computer Vision': r'\bcomputer\s*vision\b|\bcv\b',
    'PyTorch': r'\bpytorch\b',
    'TensorFlow': r'\btensorflow\b|\btf\b',
    'Pandas': r'\bpandas\b',
    'NumPy': r'\bnumpy\b',
    'Scikit-Learn': r'\bscikit-learn\b|\bsklearn\b',
    'R': r'(?:^|\s|\b)r(?:\b|\s|$)',
    'Tableau': r'\btableau\b',
    'Power BI': r'\bpower\s*bi\b',
    'Spark': r'\bspark\b|\bapache\s*spark\b',
    'Hadoop': r'\bhadoop\b',
    
    # Mobile
    'React Native': r'\breact\s*native\b',
    'Flutter': r'\bflutter\b',
    'Swift': r'\bswift\b',
    'Kotlin': r'\bkotlin\b',
    'Android': r'\bandroid\b',
    'iOS': r'\bios\b',
    
    # Agile & Tools
    'Agile': r'\bagile\b',
    'Scrum': r'\bscrum\b',
    'Jira': r'\bjira\b',
}

# Standard resume section keywords for checking section completeness
SECTIONS = {
    'Experience': [r'experience', r'employment', r'work history', r'career history', r'professional background'],
    'Education': [r'education', r'academic', r'qualification', r'degree', r'university', r'college'],
    'Projects': [r'projects', r'portfolio', r'personal projects', r'key projects'],
    'Skills': [r'skills', r'technical skills', r'core competencies', r'technologies', r'expertise'],
    'Certifications': [r'certifications', r'certificates', r'awards', r'licenses', r'courses']
}

def extract_text_from_pdf(pdf_file):
    """
    Extracts text from an uploaded PDF file object using pypdf.
    """
    text = ""
    try:
        reader = PdfReader(pdf_file)
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    except Exception as e:
        # Fallback or logging could be added here
        print(f"Error extracting PDF: {e}")
        text = ""
    
    # Clean whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def detect_skills(text):
    """
    Identifies professional skills in the text based on regex matching.
    """
    found_skills = []
    text_lower = text.lower()
    
    for skill_name, pattern in SKILLS_TAXONOMY.items():
        if re.search(pattern, text_lower, re.IGNORECASE):
            found_skills.append(skill_name)
            
    return sorted(found_skills)

def calculate_ats_score(text, skills, sections_found, contact_info):
    """
    Calculates a heuristic ATS Score from 0 to 100.
    """
    score = 0
    
    # 1. Section Completeness (Max 25 points)
    # 5 points for each section present
    section_score = len(sections_found) * 5
    score += section_score
    
    # 2. Skill Coverage (Max 30 points)
    # Based on the number of recognized skills found
    num_skills = len(skills)
    if num_skills >= 11:
        skill_score = 30
    elif num_skills >= 6:
        skill_score = 25
    elif num_skills >= 3:
        skill_score = 15
    elif num_skills >= 1:
        skill_score = 5
    else:
        skill_score = 0
    score += skill_score
    
    # 3. Contact Info Presence (Max 25 points)
    # Email = 10, Phone = 10, GitHub/LinkedIn = 5
    contact_score = 0
    if contact_info.get('email'):
        contact_score += 10
    if contact_info.get('phone'):
        contact_score += 10
    if contact_info.get('github') or contact_info.get('linkedin'):
        contact_score += 5
    score += contact_score
    
    # 4. Word Count and Format Heuristics (Max 20 points)
    words = text.split()
    word_count = len(words)
    
    if 200 <= word_count <= 1000:
        length_score = 20
    elif 100 <= word_count < 200:
        length_score = 12
    elif word_count > 1000:
        length_score = 15 # slightly penalized for being too wordy
    else:
        length_score = 5 # too short to contain valuable info
    score += length_score
    
    return min(score, 100)

def scan_sections_and_contact(text):
    """
    Identifies which standard sections exist and parses key contact details.
    """
    sections_found = []
    text_lower = text.lower()
    
    # Scan for sections
    for section_name, patterns in SECTIONS.items():
        for pattern in patterns:
            if re.search(r'\b' + pattern + r'\b', text_lower):
                sections_found.append(section_name)
                break
                
    # Scan for email
    email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text)
    email = email_match.group(0) if email_match else None
    
    # Scan for phone
    # Matches simple formats: +1-234-567-8901, (123) 456-7890, 123-456-7890, etc.
    phone_match = re.search(r'(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', text)
    phone = phone_match.group(0) if phone_match else None
    
    # Scan for social handles
    github = True if re.search(r'github\.com/[\w\.-]+', text_lower) else False
    linkedin = True if re.search(r'linkedin\.com/in/[\w\.-]+', text_lower) else False
    
    return sections_found, {
        'email': email,
        'phone': phone,
        'github': github,
        'linkedin': linkedin
    }

def generate_suggestions(text, skills, sections_found, contact_info):
    """
    Generates actionable feedback based on what the resume lacks.
    """
    suggestions = []
    
    # Check Contact details
    if not contact_info.get('email'):
        suggestions.append({
            'type': 'critical',
            'message': 'Email address not found. Ensure your email is clearly visible at the top of your resume.'
        })
    if not contact_info.get('phone'):
        suggestions.append({
            'type': 'critical',
            'message': 'Phone number not found. Recruiters need a way to call you; please add it.'
        })
    if not contact_info.get('github') and not contact_info.get('linkedin'):
        suggestions.append({
            'type': 'warning',
            'message': 'No GitHub or LinkedIn links detected. Add professional online profiles to show your network and work history.'
        })
        
    # Check Sections
    all_sections = set(SECTIONS.keys())
    missing_sections = all_sections - set(sections_found)
    
    for section in missing_sections:
        severity = 'critical' if section in ['Experience', 'Education', 'Skills'] else 'warning'
        suggestions.append({
            'type': severity,
            'message': f"Missing standard '{section}' section. Label this clearly so ATS scanners can parse it correctly."
        })
        
    # Check Skills Count
    if len(skills) < 5:
        suggestions.append({
            'type': 'warning',
            'message': f"Only {len(skills)} tech skills detected. Add more skills relevant to your target role to rank higher in search results."
        })
    elif len(skills) > 20:
        suggestions.append({
            'type': 'info',
            'message': "High number of skills detected. Keep them highly relevant to your target job to avoid visual clutter."
        })
        
    # Check Length
    word_count = len(text.split())
    if word_count < 200:
        suggestions.append({
            'type': 'critical',
            'message': "Resume is extremely short (less than 200 words). Expand your description of projects and job experience."
        })
    elif word_count > 1000:
        suggestions.append({
            'type': 'warning',
            'message': "Resume exceeds 1000 words. Try to keep it concise and strictly focused on key accomplishments, ideally limiting it to 1-2 pages."
        })
        
    return suggestions

def recommend_companies_and_roles(skills):
    """
    Recommends career paths and potential employers based on detected skills.
    """
    roles = []
    companies = []
    
    skills_set = {s.lower() for s in skills}
    
    # Web / Frontend mapping
    frontend_skills = {'react', 'angular', 'vue', 'svelte', 'typescript', 'javascript', 'html', 'css', 'next.js', 'redux', 'tailwind css'}
    # Backend mapping
    backend_skills = {'python', 'django', 'flask', 'fastapi', 'java', 'spring boot', 'node.js', 'express.js', 'go', 'ruby', 'ruby on rails', 'php', 'laravel', 'c#', 'asp.net', 'c++'}
    # Data Science / AI mapping
    data_skills = {'machine learning', 'deep learning', 'artificial intelligence', 'nlp', 'computer vision', 'pytorch', 'tensorflow', 'pandas', 'numpy', 'scikit-learn', 'r', 'spark', 'hadoop'}
    # Cloud / DevOps mapping
    devops_skills = {'aws', 'azure', 'google cloud', 'docker', 'kubernetes', 'jenkins', 'git', 'github', 'gitlab', 'ci/cd', 'terraform', 'ansible', 'linux', 'bash'}
    # Mobile mapping
    mobile_skills = {'react native', 'flutter', 'swift', 'kotlin', 'android', 'ios'}
    
    # 1. Evaluate Roles
    if skills_set.intersection(frontend_skills):
        roles.append('Frontend Engineer')
        roles.append('UI Developer')
        companies.extend(['Meta', 'Netflix', 'Stripe', 'Vercel', 'Airbnb'])
        
    if skills_set.intersection(backend_skills):
        roles.append('Backend Software Engineer')
        roles.append('Systems Engineer')
        companies.extend(['Amazon', 'Microsoft', 'Uber', 'Google', 'Salesforce'])
        
    if skills_set.intersection(data_skills):
        roles.append('Data Scientist')
        roles.append('Machine Learning Engineer')
        companies.extend(['OpenAI', 'Google DeepMind', 'NVIDIA', 'Tesla', 'Meta'])
        
    if skills_set.intersection(devops_skills):
        roles.append('DevOps Engineer')
        roles.append('Cloud Infrastructure Architect')
        roles.append('Site Reliability Engineer (SRE)')
        companies.extend(['Amazon Web Services (AWS)', 'HashiCorp', 'Red Hat', 'Datadog', 'Microsoft'])
        
    if skills_set.intersection(mobile_skills):
        roles.append('Mobile App Developer (iOS/Android)')
        companies.extend(['Apple', 'Spotify', 'Uber', 'Lyft', 'Instagram'])
        
    # Deduplicate recommendations and handle fallbacks
    roles = list(set(roles))
    companies = list(set(companies))
    
    if not roles:
        roles = ['Software Engineer (Generalist)', 'Associate Technical Consultant']
    if not companies:
        companies = ['Accenture', 'Infosys', 'Cognizant', 'Capgemini', 'TCS']
        
    # Limit list sizes
    return roles[:3], companies[:4]

def analyze_resume(pdf_file, filename):
    """
    Orchestrator function: Extracts text, parses sections, detects skills, 
    calculates the ATS score, compiles suggestions, and generates role/company recommendations.
    """
    raw_text = extract_text_from_pdf(pdf_file)
    
    if not raw_text:
        return {
            'text': '',
            'skills': [],
            'ats_score': 0,
            'suggestions': [{'type': 'critical', 'message': 'Could not extract text from the PDF. Ensure it is not password protected or scanned as an un-OCRed image.'}],
            'roles': ['Software Engineer'],
            'companies': ['Tech Company']
        }
        
    skills = detect_skills(raw_text)
    sections_found, contact_info = scan_sections_and_contact(raw_text)
    score = calculate_ats_score(raw_text, skills, sections_found, contact_info)
    suggestions = generate_suggestions(raw_text, skills, sections_found, contact_info)
    roles, companies = recommend_companies_and_roles(skills)
    
    return {
        'text': raw_text,
        'skills': skills,
        'ats_score': score,
        'suggestions': suggestions,
        'roles': roles,
        'companies': companies
    }
