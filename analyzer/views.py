from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.db.models import Avg, Max, Min, Q
import os

from .models import ResumeAnalysis, Job, Application, Profile
from .forms import StudentSignUpForm, CompanySignUpForm, JobForm
from .utils import analyze_resume

# ==========================================
# Role-Based Access Control Decorators
# ==========================================
def student_required(view_func):
    """
    Decorator to restrict access to Student/Candidate users.
    """
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if request.user.profile.user_type != 'student':
            messages.error(request, "Access Denied: This page is restricted to candidates.")
            return redirect('company_dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper

def company_required(view_func):
    """
    Decorator to restrict access to Company/Employer users.
    """
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if request.user.profile.user_type != 'company':
            messages.error(request, "Access Denied: This page is restricted to employers.")
            return redirect('student_dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper


# ==========================================
# Job Match Scoring Helper
# ==========================================
def calculate_job_match(student_skills, job_skills):
    """
    Compares candidate skills against job requirements.
    Formula: Match Score = (Matched Skills / Required Skills) * 100
    Returns score (0-100), matched list, and missing list.
    """
    if not job_skills:
        return 100, [], []
        
    student_skills_set = {s.lower() for s in student_skills}
    job_skills_set = {s.lower() for s in job_skills}
    
    matched = job_skills_set.intersection(student_skills_set)
    missing = job_skills_set - student_skills_set
    
    score = int((len(matched) / len(job_skills_set)) * 100)
    
    # Map back to original casing of job requirements
    matched_original = [s for s in job_skills if s.lower() in matched]
    missing_original = [s for s in job_skills if s.lower() in missing]
    
    return score, matched_original, missing_original


# ==========================================
# Authentication & Portal Routing
# ==========================================
def home_view(request):
    """
    Landing portal for both Students and Recruiter Agents.
    """
    if request.user.is_authenticated:
        if request.user.profile.user_type == 'company':
            return redirect('company_dashboard')
        return redirect('student_dashboard')
    return render(request, 'analyzer/home.html')

def student_register_view(request):
    """
    Handles candidate registration.
    """
    if request.user.is_authenticated:
        return redirect('home')
        
    if request.method == 'POST':
        form = StudentSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Welcome to ResuAI, {user.username}! Create your profile by scanning a resume.")
            return redirect('student_dashboard')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field.capitalize()}: {error}")
    else:
        form = StudentSignUpForm()
        
    return render(request, 'analyzer/register.html', {'form': form, 'role': 'student'})

def company_register_view(request):
    """
    Handles employer registration.
    """
    if request.user.is_authenticated:
        return redirect('home')
        
    if request.method == 'POST':
        form = CompanySignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Corporate account created for {user.profile.company_name}! Get started by posting a job opening.")
            return redirect('company_dashboard')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field.capitalize()}: {error}")
    else:
        form = CompanySignUpForm()
        
    return render(request, 'analyzer/register.html', {'form': form, 'role': 'company'})

def login_view(request):
    """
    Authenticates and redirects users dynamically to their respective dashboards.
    """
    if request.user.is_authenticated:
        if request.user.profile.user_type == 'company':
            return redirect('company_dashboard')
        return redirect('student_dashboard')
        
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"Welcome back, {username}!")
                if user.profile.user_type == 'company':
                    return redirect('company_dashboard')
                return redirect('student_dashboard')
        else:
            messages.error(request, "Invalid username or password. Please try again.")
    else:
        form = AuthenticationForm()
        
    return render(request, 'analyzer/login.html', {'form': form})

def logout_view(request):
    """
    Logs out user.
    """
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('login')


# ==========================================
# Student Candidate Views
# ==========================================
@login_required
@student_required
def student_dashboard_view(request):
    """
    Displays resume statistics, skills mapping, job suggestions, and past scans.
    """
    analyses = ResumeAnalysis.objects.filter(user=request.user)
    latest_analysis = analyses.first()
    
    # Calculate stats
    stats = analyses.aggregate(
        avg_score=Avg('ats_score'),
        max_score=Max('ats_score'),
        min_score=Min('ats_score')
    )
    
    stats_data = {
        'total': analyses.count(),
        'avg': round(stats['avg_score']) if stats['avg_score'] is not None else 0,
        'max': stats['max_score'] if stats['max_score'] is not None else 0,
        'min': stats['min_score'] if stats['min_score'] is not None else 0
    }
    
    # SVG Chart trend data
    recent_analyses = list(analyses.order_by('created_at')[:7])
    chart_dates = [a.created_at.strftime('%m/%d') for a in recent_analyses]
    chart_scores = [a.ats_score for a in recent_analyses]
    
    # Job recommendations and missing skills gap
    recommended_jobs = []
    missing_skills_all = set()
    recommended_companies = set()
    
    if latest_analysis:
        student_skills = latest_analysis.skills_found
        active_jobs = Job.objects.all()
        
        for job in active_jobs:
            match_score, matched, missing = calculate_job_match(student_skills, job.required_skills)
            
            # Keep jobs with some relevance
            recommended_jobs.append({
                'job': job,
                'match_score': match_score,
                'missing': missing[:3],
                'company_name': job.company.profile.company_name or job.company.username
            })
            
            # Map missing skills and hiring companies
            if match_score < 100:
                missing_skills_all.update(missing)
            recommended_companies.add(job.company.profile.company_name or job.company.username)
            
        # Sort jobs by match percentage descending
        recommended_jobs = sorted(recommended_jobs, key=lambda x: x['match_score'], reverse=True)[:5]
    
    # Get applicant history tracker
    applied_list = Application.objects.filter(student=request.user)
    
    context = {
        'analyses': analyses,
        'latest_analysis': latest_analysis,
        'stats': stats_data,
        'chart_dates': chart_dates,
        'chart_scores': chart_scores,
        'recommended_jobs': recommended_jobs,
        'missing_skills': sorted(list(missing_skills_all))[:5],
        'recommended_companies': sorted(list(recommended_companies))[:4],
        'applied_list': applied_list
    }
    return render(request, 'analyzer/student_dashboard.html', context)

@login_required
@student_required
def job_listings_view(request):
    """
    Searchable, filterable list of active jobs showing candidate compatibility.
    """
    query = request.GET.get('q', '')
    min_match = request.GET.get('match', '')
    
    jobs = Job.objects.all()
    if query:
        jobs = jobs.filter(Q(title__icontains=query) | Q(description__icontains=query))
        
    latest_analysis = ResumeAnalysis.objects.filter(user=request.user).first()
    student_skills = latest_analysis.skills_found if latest_analysis else []
    
    jobs_with_matching = []
    for job in jobs:
        match_score, matched, missing = calculate_job_match(student_skills, job.required_skills)
        
        # Filter by match score if set
        if min_match:
            try:
                if match_score < int(min_match):
                    continue
            except ValueError:
                pass
                
        jobs_with_matching.append({
            'job': job,
            'match_score': match_score,
            'company_name': job.company.profile.company_name or job.company.username,
        })
        
    # Sort matched listings by percentage descending
    jobs_with_matching = sorted(jobs_with_matching, key=lambda x: x['match_score'], reverse=True)
    
    context = {
        'jobs_list': jobs_with_matching,
        'query': query,
        'min_match': min_match,
        'has_resume': len(student_skills) > 0
    }
    return render(request, 'analyzer/job_listings.html', context)

@login_required
@student_required
def job_detail_apply_view(request, pk):
    """
    Displays job profile and handles application submission.
    """
    job = get_object_or_404(Job, pk=pk)
    latest_analysis = ResumeAnalysis.objects.filter(user=request.user).first()
    
    if not latest_analysis:
        messages.warning(request, "Please upload and analyze a PDF resume on your dashboard before applying to jobs.")
        return redirect('student_dashboard')
        
    student_skills = latest_analysis.skills_found
    match_score, matched, missing = calculate_job_match(student_skills, job.required_skills)
    
    # Check if already applied
    already_applied = Application.objects.filter(student=request.user, job=job).exists()
    
    if request.method == 'POST':
        if already_applied:
            messages.info(request, "You have already submitted an application for this job opening.")
            return redirect('student_dashboard')
            
        # Determine status category
        if match_score >= 90:
            status = 'Highly Recommended'
        elif match_score >= 70:
            status = 'Shortlisted'
        else:
            status = 'Rejected'
            
        Application.objects.create(
            student=request.user,
            job=job,
            match_score=match_score,
            status=status
        )
        messages.success(request, f"Application for '{job.title}' submitted successfully! Your match score is {match_score}%.")
        return redirect('student_dashboard')
        
    context = {
        'job': job,
        'match_score': match_score,
        'matched_skills': matched,
        'missing_skills': missing,
        'already_applied': already_applied,
        'company_name': job.company.profile.company_name or job.company.username
    }
    return render(request, 'analyzer/job_detail.html', context)


# ==========================================
# Company Employer Views
# ==========================================
@login_required
@company_required
def company_dashboard_view(request):
    """
    Dashboard for employers showing posted positions and applications.
    """
    jobs = Job.objects.filter(company=request.user)
    
    # Calculate counts and details
    jobs_data = []
    total_apps = 0
    for j in jobs:
        app_count = j.applications.count()
        total_apps += app_count
        jobs_data.append({
            'job': j,
            'app_count': app_count
        })
        
    context = {
        'company_name': request.user.profile.company_name or request.user.username,
        'jobs_data': jobs_data,
        'total_apps': total_apps,
    }
    return render(request, 'analyzer/company_dashboard.html', context)

@login_required
@company_required
def create_job_view(request):
    """
    Publishes a new job opening.
    """
    if request.method == 'POST':
        form = JobForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.company = request.user
            job.save()
            messages.success(request, f"Job listing for '{job.title}' published successfully!")
            return redirect('company_dashboard')
    else:
        form = JobForm()
        
    return render(request, 'analyzer/create_job.html', {'form': form, 'action': 'Create'})

@login_required
@company_required
def edit_job_view(request, pk):
    """
    Modifies an existing job posting.
    """
    job = get_object_or_404(Job, pk=pk, company=request.user)
    if request.method == 'POST':
        form = JobForm(request.POST, instance=job)
        if form.is_valid():
            form.save()
            messages.success(request, f"Job listing for '{job.title}' updated successfully!")
            return redirect('company_dashboard')
    else:
        form = JobForm(instance=job)
        
    return render(request, 'analyzer/create_job.html', {'form': form, 'action': 'Edit', 'job': job})

@login_required
@company_required
def delete_job_view(request, pk):
    """
    Removes a job posting.
    """
    job = get_object_or_404(Job, pk=pk, company=request.user)
    title = job.title
    job.delete()
    messages.success(request, f"Job listing '{title}' deleted.")
    return redirect('company_dashboard')

@login_required
@company_required
def candidate_ranking_view(request, pk):
    """
    Ranks applicants by matching percentage in a leaderboard format.
    """
    job = get_object_or_404(Job, pk=pk, company=request.user)
    
    # Fetch applications and order by match score descending
    applications = Application.objects.filter(job=job).order_by('-match_score')
    
    # Compute status breakdowns
    total = applications.count()
    highly_rec = applications.filter(status='Highly Recommended').count()
    shortlisted = applications.filter(status='Shortlisted').count()
    rejected = applications.filter(status='Rejected').count()
    
    context = {
        'job': job,
        'applications': applications,
        'stats': {
            'total': total,
            'highly': highly_rec,
            'shortlisted': shortlisted,
            'rejected': rejected
        }
    }
    return render(request, 'analyzer/candidate_ranking.html', context)

@login_required
@company_required
def candidate_detail_view(request, pk):
    """
    Allows employers to inspect a candidate's resume analysis details.
    """
    application = get_object_or_404(Application, pk=pk, job__company=request.user)
    student = application.student
    
    # Get latest scan
    latest_analysis = ResumeAnalysis.objects.filter(user=student).first()
    
    if not latest_analysis:
        messages.error(request, "Candidate hasn't uploaded a parsed resume scan.")
        return redirect('candidate_ranking', pk=application.job.pk)
        
    # Recalculate match specifics for formatting
    match_score, matched, missing = calculate_job_match(
        latest_analysis.skills_found, 
        application.job.required_skills
    )
    
    context = {
        'application': application,
        'student': student,
        'analysis': latest_analysis,
        'matched_skills': matched,
        'missing_skills': missing,
    }
    return render(request, 'analyzer/candidate_detail.html', context)


# ==========================================
# Generic Portals & Core Actions
# ==========================================
@login_required
@student_required
@require_POST
def analyze_resume_view(request):
    """
    Handles student PDF resume uploads and analysis.
    """
    if 'resume' not in request.FILES:
        messages.error(request, "Please select a resume file to upload.")
        return redirect('student_dashboard')
        
    uploaded_file = request.FILES['resume']
    if not uploaded_file.name.endswith('.pdf'):
        messages.error(request, "Only PDF files are supported.")
        return redirect('student_dashboard')
        
    analysis_results = analyze_resume(uploaded_file, uploaded_file.name)
    
    ResumeAnalysis.objects.create(
        user=request.user,
        resume_file=uploaded_file,
        filename=uploaded_file.name,
        extracted_text=analysis_results['text'],
        skills_found=analysis_results['skills'],
        ats_score=analysis_results['ats_score'],
        suggestions=analysis_results['suggestions'],
        recommended_roles=analysis_results['roles'],
        recommended_companies=analysis_results['companies']
    )
    
    messages.success(request, f"Resume '{uploaded_file.name}' analyzed successfully!")
    return redirect('student_dashboard')

@login_required
@student_required
def analysis_detail_view(request, pk):
    """
    Renders detailed resume metrics.
    """
    analysis = get_object_or_404(ResumeAnalysis, pk=pk, user=request.user)
    
    score = analysis.ats_score
    if score >= 75:
        score_class = 'success'
        score_message = 'Excellent'
    elif score >= 50:
        score_class = 'warning'
        score_message = 'Moderate'
    else:
        score_class = 'danger'
        score_message = 'Needs Improvement'
        
    context = {
        'analysis': analysis,
        'score_class': score_class,
        'score_message': score_message
    }
    return render(request, 'analyzer/result_detail.html', context)

@login_required
@student_required
@require_POST
def delete_analysis_view(request, pk):
    """
    Deletes an analysis.
    """
    analysis = get_object_or_404(ResumeAnalysis, pk=pk, user=request.user)
    filename = analysis.filename
    if analysis.resume_file:
        if os.path.exists(analysis.resume_file.path):
            os.remove(analysis.resume_file.path)
    analysis.delete()
    messages.success(request, f"Scan report for '{filename}' deleted.")
    return redirect('student_dashboard')

def about_view(request):
    """
    Renders about page.
    """
    return render(request, 'analyzer/about.html')

def contact_view(request):
    """
    Renders contact page.
    """
    return render(request, 'analyzer/contact.html')
