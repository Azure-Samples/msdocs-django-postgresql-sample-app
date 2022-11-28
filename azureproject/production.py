from .settings import *
import os

# Configure the domain name using the environment variable
# that Azure automatically creates for us.
ALLOWED_HOSTS = [os.environ['universityapplication-server.postgres.database.azure.com']] if 'universityapplication-server.postgres.database.azure.com' in os.environ else []
CSRF_TRUSTED_ORIGINS = ['https://'+ os.environ['universityapplication-server.postgres.database.azure.com']] if 'universityapplication-server.postgres.database.azure.com' in os.environ else []
DEBUG = False

# WhiteNoise configuration
MIDDLEWARE = [                                                                   
    'django.middleware.security.SecurityMiddleware',
# Add whitenoise middleware after the security middleware                             
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',                      
    'django.middleware.common.CommonMiddleware',                                 
    'django.middleware.csrf.CsrfViewMiddleware',                                 
    'django.contrib.auth.middleware.AuthenticationMiddleware',                   
    'django.contrib.messages.middleware.MessageMiddleware',                      
    'django.middleware.clickjacking.XFrameOptionsMiddleware',                    
]

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'  
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# DBHOST is only the server name, not the full URL
hostname = os.environ['universityapplication-server']

# Configure Postgres database; the full username for PostgreSQL flexible server is
# username (not @sever-name).
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ['postgres'],
        'HOST': hostname + ".postgres.database.azure.com",
        'USER': os.environ['otpljolaqm'],
        'PASSWORD': os.environ['2HO2E0P83B7T3NZ8$'] 
    }
}
