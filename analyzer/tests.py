from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile

from .models import ResumeAnalysis
from .utils import detect_skills, calculate_ats_score, recommend_companies_and_roles, generate_suggestions, scan_sections_and_contact

class ResumeAnalysisModelTest(TestCase):
    """
    Tests the ResumeAnalysis model creation and field validation.
    """
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password123')
        
    def test_model_creation(self):
        pdf_file = SimpleUploadedFile("resume.pdf", b"Dummy PDF text content", content_type="application/pdf")
        analysis = ResumeAnalysis.objects.create(
            user=self.user,
            resume_file=pdf_file,
            filename='resume.pdf',
            extracted_text='Dummy PDF text content with Python and React skills.',
            skills_found=['Python', 'React'],
            ats_score=85,
            suggestions=[{'type': 'info', 'message': 'Looks good'}],
            recommended_roles=['Backend Software Engineer', 'Frontend Engineer'],
            recommended_companies=['Google', 'Meta']
        )
        
        self.assertEqual(analysis.filename, 'resume.pdf')
        self.assertEqual(analysis.ats_score, 85)
        self.assertEqual(analysis.skills_found, ['Python', 'React'])
        self.assertEqual(str(analysis), "testuser - resume.pdf (85%)")


class UtilityParserTest(TestCase):
    """
    Tests the parsing logic, skill matcher, scoring engine, and recommendation mappings.
    """
    def test_skill_detection(self):
        text = "I am a skilled Software Developer experienced in Python, Django, HTML, CSS, JavaScript, React, and Docker."
        skills = detect_skills(text)
        
        # Verify specific skills are extracted
        self.assertIn('Python', skills)
        self.assertIn('Django', skills)
        self.assertIn('React', skills)
        self.assertIn('Docker', skills)
        self.assertNotIn('Kubernetes', skills) # Not present in sample
        
    def test_special_characters_skill_detection(self):
        text_with_special = "Expert in C++, C#, and .NET frameworks."
        skills = detect_skills(text_with_special)
        
        self.assertIn('C++', skills)
        self.assertIn('C#', skills)
        self.assertIn('ASP.NET', skills) # Match standard patterns

    def test_score_calculation(self):
        # Full resume text simulation with sections, contacts, skills
        text = "Experience: Senior Backend Engineer at Google. Developed Python apps. Education: BS in CS. Skills: Python, SQL, Docker. Contact: test@example.com (123) 456-7890 github.com/testuser"
        skills = ['Python', 'SQL', 'Docker']
        
        sections_found, contact_info = scan_sections_and_contact(text)
        score = calculate_ats_score(text, skills, sections_found, contact_info)
        
        # Should be a high score because most elements exist
        self.assertGreaterEqual(score, 60)
        self.assertLessEqual(score, 100)

    def test_score_limits(self):
        # Empty/minimal text check
        score_low = calculate_ats_score("", [], [], {'email': None, 'phone': None, 'github': False, 'linkedin': False})
        self.assertEqual(score_low, 5) # Minimum score based on word length check only (too short)
        
    def test_role_and_company_recommendations(self):
        skills_fe = ['React', 'HTML', 'CSS', 'JavaScript']
        roles_fe, companies_fe = recommend_companies_and_roles(skills_fe)
        
        self.assertIn('Frontend Engineer', roles_fe)
        self.assertIn('Meta', companies_fe)
        
        skills_be = ['Python', 'Django', 'AWS', 'Docker']
        roles_be, companies_be = recommend_companies_and_roles(skills_be)
        
        self.assertIn('Backend Software Engineer', roles_be)
        self.assertIn('Amazon', companies_be)

    def test_suggestions_generation(self):
        text = "My name is John. I have no skills."
        sections_found = []
        contact_info = {'email': None, 'phone': None, 'github': False, 'linkedin': False}
        
        suggestions = generate_suggestions(text, [], sections_found, contact_info)
        
        # Verify warning/critical issues are raised
        messages = [s['message'] for s in suggestions]
        self.assertTrue(any("Email address" in m for m in messages))
        self.assertTrue(any("Phone number" in m for m in messages))
        self.assertTrue(any("Experience" in m for m in messages))
        self.assertTrue(any("Education" in m for m in messages))


class ViewSecurityTest(TestCase):
    """
    Tests security access and authentication redirects.
    """
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='password123')
        
    def test_dashboard_redirects_unauthenticated(self):
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 302)
        # Redirect to login URL (which is reverse('login'))
        self.assertIn(reverse('login'), response.url)

    def test_dashboard_accessible_when_logged_in(self):
        self.client.login(username='testuser', password='password123')
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'analyzer/dashboard.html')
        
    def test_anonymous_user_cannot_upload(self):
        response = self.client.post(reverse('analyze_resume'), {'resume': 'fakefile.pdf'})
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('login'), response.url)
