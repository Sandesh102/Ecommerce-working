"""
Script to add logging configuration to Django settings.py
"""

settings_file = r"c:\Users\NNN\Desktop\zzz\Ecommerce_before_deployment\ecommerce\settings.py"

# Read the current settings
with open(settings_file, 'r', encoding='utf-8') as f:
    content = f.read()

# Define the logging configuration to add
logging_config = """
# Logging configuration - captures all errors and outputs to console
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.request': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': False,
        },
        'django.db.backends': {
            'handlers': ['console'],
            'level': 'INFO' if DEBUG else 'WARNING',
            'propagate': False,
        },
    },
}
"""

# Find the position to insert (after SESSION_COOKIE_AGE)
insert_marker = "SESSION_COOKIE_AGE = 1209600"
if insert_marker in content:
    # Find the position after this line
    pos = content.find(insert_marker)
    # Find the end of the line
    end_of_line = content.find('\n', pos)
    # Insert the logging config after the blank lines
    insert_pos = end_of_line + 1
    # Skip any blank lines
    while insert_pos < len(content) and content[insert_pos] in ['\n', '\r']:
        insert_pos += 1
    
    # Insert the logging configuration
    new_content = content[:insert_pos] + logging_config + '\n' + content[insert_pos:]
    
    # Write back
    with open(settings_file, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("✅ Successfully added logging configuration to settings.py")
else:
    print("❌ Could not find SESSION_COOKIE_AGE in settings.py")
