from django.apps import AppConfig
import sys
import os

class AnalyzerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'analyzer'

    def ready(self):
        # Only trigger database migrations when starting the development server
        # and not running a migration command to avoid recursion
        is_running_server = ('runserver' in sys.argv or os.environ.get('RUN_MAIN') == 'true')
        is_migration_command = any(cmd in sys.argv for cmd in ['makemigrations', 'migrate', 'sqlmigrate', 'showmigrations', 'test'])
        
        if is_running_server and not is_migration_command:
            from django.conf import settings
            db_config = settings.DATABASES['default']
            
            # If MySQL engine is active, verify/create database before migrations
            if db_config['ENGINE'] == 'django.db.backends.mysql':
                import pymysql
                try:
                    host = db_config.get('HOST', '127.0.0.1')
                    port = int(db_config.get('PORT', 3306) or 3306)
                    user = db_config.get('USER', 'root')
                    password = db_config.get('PASSWORD', '')
                    db_name = db_config.get('NAME', 'resume_analyzer')
                    
                    conn = pymysql.connect(
                        host=host,
                        port=port,
                        user=user,
                        password=password
                    )
                    cursor = conn.cursor()
                    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
                    cursor.close()
                    conn.close()
                    print(f"ResuAI: Verified/Created MySQL database '{db_name}'.")
                except Exception as e:
                    print(f"ResuAI: Auto-creation database warning: {e}")

            from django.core.management import call_command
            try:
                print("ResuAI: Checking database tables and running pending migrations...")
                call_command('migrate', interactive=False)
                print("ResuAI: Database migrations verified and applied successfully!")
            except Exception as e:
                print(f"ResuAI: Auto-migration warning: {e}")

