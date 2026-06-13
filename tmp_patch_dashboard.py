from pathlib import Path

view_path = Path('analyzer/views.py')
template_path = Path('analyzer/templates/analyzer/company_dashboard.html')

view_old = '''    # Calculate counts and details
    jobs_data = []
    for j in jobs:
        app_count = j.applications.count()
        jobs_data.append({
            'job': j,
            'app_count': app_count
        })
        
    context = {
        'company_name': request.user.profile.company_name or request.user.username,
        'jobs_data': jobs_data
    }
'''
view_new = '''    # Calculate counts and details
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
'''

template_old = '''                <!-- Accumulate application counts -->
                <span class="stat-value">
                    {% temp_total_apps as total_apps %}
                    {% for item in jobs_data %}
                        <!-- We sum applicant counts in context or use a simple length sum -->
                    {% endfor %}
                    {{ user.jobs.all.applications.count|default:user.jobs.count }}
                </span>
'''
template_new = '''                <span class="stat-value">{{ total_apps|default:0 }}</span>
'''

for path, old, new in [(view_path, view_old, view_new), (template_path, template_old, template_new)]:
    text = path.read_text()
    if old not in text:
        raise ValueError(f'Old block not found in {path}')
    path.write_text(text.replace(old, new))

print('patched')