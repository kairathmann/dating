#  -*- coding: UTF8 -*-

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os, socket, sys

# ...shouldn't this be os.path.dirname(os.path.abspath(__file__)) ?
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'django_file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'django.log',
            'formatter': 'verbose',
        },
        'api_helios_file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'api_helios.log',
            'formatter': 'verbose',
        },
        'app_helios_file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'app_helios.log',
            'formatter': 'verbose',
        },
        'plant_eos_file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'plant_eos.log',
            'formatter': 'verbose',
        },
        'plant_hermes_file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'plant_hermes.log',
            'formatter': 'verbose',
        },
        'silo_asset_file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'silo_asset.log',
            'formatter': 'verbose',
        },
        'silo_geodata_file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'silo_geodata.log',
            'formatter': 'verbose',
        },
        'silo_message_file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'silo_message.log',
            'formatter': 'verbose',
        },
        'silo_user_file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'silo_user.log',
            'formatter': 'verbose',
        },
        'sys_base_file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'sys_base.log',
            'formatter': 'verbose',
        },
        'sys_util_file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'sys_util.log',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'formatter': 'verbose',
            'handlers': ['django_file'],
            'level': 'WARNING',
            'propagate': True,
        },
        'api_helios': {
            'formatter': 'verbose',
            'handlers': ['api_helios_file'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'app_helios': {
            'formatter': 'verbose',
            'handlers': ['app_helios_file'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'plant_eos': {
            'formatter': 'verbose',
            'handlers': ['plant_eos_file'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'plant_hermes': {
            'formatter': 'verbose',
            'handlers': ['plant_hermes_file'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'silo_asset': {
            'formatter': 'verbose',
            'handlers': ['silo_asset_file'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'silo_geodata': {
            'formatter': 'verbose',
            'handlers': ['silo_geodata_file'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'silo_message': {
            'formatter': 'verbose',
            'handlers': ['silo_message_file'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'silo_user': {
            'formatter': 'verbose',
            'handlers': ['silo_user_file'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'sys_base': {
            'formatter': 'verbose',
            'handlers': ['sys_base_file'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'sys_util': {
            'formatter': 'verbose',
            'handlers': ['sys_util_file'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}

# Determine if we're on a devbox and/or running the importer
##################################################################################################

RUN_LOCATION_DEVBOX = 1
RUN_LOCATION_STAGING = 2
RUN_LOCATION_PROD = 3

hostname = socket.gethostname()
if hostname == 'luna':
    RUN_LOCATION = RUN_LOCATION_DEVBOX
elif hostname == 'test':
    RUN_LOCATION = RUN_LOCATION_STAGING
elif hostname == 'prod':
    RUN_LOCATION = RUN_LOCATION_PROD
else:
    RUN_LOCATION = RUN_LOCATION_DEVBOX

if os.environ.get("RUN_LOCATION"):
    RUN_LOCATION = int(os.environ.get("RUN_LOCATION"))

if sys.argv[0] == 'import.py':

    RUNNING_IMPORTER = True
else:
    RUNNING_IMPORTER = False

#Optional logging to Amazon CloudWatch rather than to the local log files.
if os.environ.get('LUNA_CLOUDWATCH_LOGGING') == '1':
    LOGGING['handlers']['watchtower'] = {
       'level': 'DEBUG',
       'class': 'watchtower.CloudWatchLogHandler',
    }
    for logger in LOGGING['loggers'].values():
        logger['handlers'] = ['watchtower']

##################################################################################################

SECRET_KEY = os.environ.get('LUNA_SECRET_KEY')

QTUM_RPC = os.environ.get('LUNA_QTUM_RPC')

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = False
DEFAULT_CHARSET = 'utf-8'

INSTALLED_APPS = (

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.gis',
    'corsheaders',
    'import_export',

    'plant_eos',
    'plant_hermes',

    'silo_asset',
    'silo_geodata',
    'silo_message',
    'silo_user'
)

# https://docs.djangoproject.com/en/1.9/ref/settings/#append-slash
APPEND_SLASH = True

MIDDLEWARE_CLASSES = (

    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    # 'django.middleware.csrf.CsrfViewMiddleware', #TODO
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware'
)

# If True, cookies will be allowed to be included in cross-site HTTP requests. Defaults to False.
CORS_ALLOW_CREDENTIALS = True

# If True, the whitelist will not be used and all origins will be accepted. Defaults to False.
CORS_ORIGIN_ALLOW_ALL = False

# Needed for debugging locally
CORS_ORIGIN_WHITELIST = (

    'localhost:3000',
    'localhost:80',
    '127.0.0.1:80',
    '127.0.0.1:3000'
)

##################################################################################################

# python manage.py runserver 0.0.0.0:8001 (must change SITE_BASE to http://luna.com/:8080)
# python worker_helios.py wsgi --bind 127.0.0.1:8001 --workers 8 --log-file=-

DB_PROD = os.environ.get('POSTGRES_DB')
DB_USER = os.environ.get('POSTGRES_USER')
DB_PASS = os.environ.get('POSTGRES_PASSWORD')
DB_HOST = os.environ.get('POSTGRES_HOST')
DB_PORT = os.environ.get('POSTGRES_PORT')

DATABASES = {

    'default': {

        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': DB_PROD,
        'USER': DB_USER,
        'PASSWORD': DB_PASS,
        'HOST': DB_HOST,
        'PORT': DB_PORT,
        'CONN_MAX_AGE': 600
    },

    'worker_pool': {

        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': DB_PROD,
        'USER': DB_USER,
        'PASSWORD': DB_PASS,
        'HOST': DB_HOST,
        'PORT': DB_PORT,
        'CONN_MAX_AGE': 600
    }
}

POSTGIS_VERSION = (2, 4, 3)
# GEOS_LIBRARY_PATH = '/usr/lib/libgeos_c.so.1.8.2'


##################################################################################################
# SECURITY
##################################################################################################

AUTHENTICATION_BACKENDS = [

    'silo_user.user.auth_handlers.auth_backends.AuthenticationBackend'
]

PASSWORD_HASHERS = (

    'django.contrib.auth.hashers.BCryptPasswordHasher',
    'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
    'django.contrib.auth.hashers.SHA1PasswordHasher',
    'django.contrib.auth.hashers.MD5PasswordHasher',
    'django.contrib.auth.hashers.CryptPasswordHasher',
)

AUTH_USER_MODEL = 'silo_user.User'

##################################################################################################

COMPRESS_ENABLED = False
COMPRESS_JS_FILTERS = []

##################################################################################################

FILE_UPLOAD_HANDLERS = (

    'django.core.files.uploadhandler.MemoryFileUploadHandler',
    'django.core.files.uploadhandler.TemporaryFileUploadHandler'
)

ROOT_URLCONF = 'urls'

WSGI_APPLICATION = 'wsgi.application'

USE_JS_DEBUG_PROXY = False

TEMPLATES = [

    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',

        'APP_DIRS': True,

        'DIRS': [

            '/srv/luna/app_helios/templates',
            '/srv/luna/plant_eos/templates'
        ],

        'OPTIONS': {

            'debug': True,
            'builtins': [],
            'context_processors': [

                "django.contrib.auth.context_processors.auth",
                "django.template.context_processors.debug",
                "django.template.context_processors.i18n",
                "django.template.context_processors.media",
                "django.template.context_processors.static",
                "django.template.context_processors.request",
                "django.contrib.messages.context_processors.messages"
            ]
        }
    }
]

MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# These constants appear to be used by Django, even though we don't use StaticFiles
##################################################################################################

STATIC_URL = '/static/'
STATIC_ROOT = '/staticfiles/'

STATICFILES_DIRS = ('/mnt/', '/mnt/static/',)

STATICFILES_FINDERS = (

    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

##################################################################################################

NEWRELIC_INI_FILE = '/srv/luna/config/newrelic_luna.ini'

HELIOS_NAME = 'LUNA'

SENDGRID_API_SEND_KEY = os.environ.get('LUNA_SENDGRID_API_SEND_KEY')

EMAIL_NAME = 'The Luna Team'
EMAIL_NO_REPLY = 'noreply@example.com'

EMAIL_WHITELIST = [
]

##################################################################################################

MAXMIND_LOGIN = '###'
MAXMIND_PASS = '###'

# P1 PATHS
##################################################################################################

H1_STASH_URL = 'stash/'
H1_STASH_ROOT = '/mnt/stash/'

H1_CDN_URL = 'CDN1/'
H1_CDN_ROOT = '/mnt/CDN1/'

# IMG files are loaded using this base path
H1_IMG_LIB_URL = 'hydra/img/lib/'
H1_IMG_SRC_URL = 'hydra/img/src/'

# Our deployed contract on the Testnet
QTUM_TESTNET_CONTRACT_ADDRESS = 'TBD'
QTUM_TESTNET_CONTRACT_OWNER_ADDRESS = 'TBD'

# Our deployed contract on the Mainnet
QTUM_MAINNET_CONTRACT_ADDRESS = 'TBD'

# This is actually used as the hot wallet address
QTUM_MAINNET_CONTRACT_OWNER_ADDRESS = 'TBD'

if RUN_LOCATION == RUN_LOCATION_DEVBOX:

    RUNNING_ON_PROD = False

    # Don't use new relic on dev box instances
    USE_NEWRELIC_ON_EOS = False
    USE_NEWRELIC_ON_HELIOS = False

    DEBUG = True

    SITE_PROTOCOL = 'https://'
    SITE_DOMAIN = 'example.com'

    # Set the CSRF and Session cookies as 'insecure' so they'll work on the local Django test
    # server (which doesn't support TLS)

    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False

    # Address on the testnet of our ERC20 Token smart contract
    QTUM_CONTRACT_ADDRESS = QTUM_TESTNET_CONTRACT_ADDRESS

    # Address of the user who created the testnet token smart contract
    QTUM_CONTRACT_OWNER_ADDRESS = QTUM_TESTNET_CONTRACT_OWNER_ADDRESS

elif RUN_LOCATION == RUN_LOCATION_STAGING:

    RUNNING_ON_PROD = False

    USE_NEWRELIC_ON_EOS = True
    USE_NEWRELIC_ON_HELIOS = True

    DEBUG = True

    SITE_PROTOCOL = 'https://'
    SITE_DOMAIN = 'example.com'

    # Set the CSRF and Session cookies as 'insecure' so they'll work on the local Django test
    # server (which doesn't support TLS)

    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False

    # Address on the testnet of our ERC20 Token smart contract
    QTUM_CONTRACT_ADDRESS = QTUM_TESTNET_CONTRACT_ADDRESS

    # Address of the user who created the testnet token smart contract
    QTUM_CONTRACT_OWNER_ADDRESS = QTUM_TESTNET_CONTRACT_OWNER_ADDRESS

elif RUN_LOCATION == RUN_LOCATION_PROD:

    RUNNING_ON_PROD = True

    USE_NEWRELIC_ON_EOS = True
    USE_NEWRELIC_ON_HELIOS = True

    DEBUG = False  # NEVER SWITCH DEBUG ON IN PRODUCTION - It will leak secrets and credentials

    SITE_PROTOCOL = 'https://'
    SITE_DOMAIN = 'example.com'

    # Mark CSRF and Session cookies as 'secure' to prevent JS in the browser from being able to access
    # them. Note that setting these True on DEV will BREAK ALL SESSIONS AND UNIT TESTS because the local
    # Django test server doesn't support TLS

    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

    # Address on the mainnet of our ERC20 Token smart contract
    QTUM_CONTRACT_ADDRESS = QTUM_MAINNET_CONTRACT_ADDRESS

    # Address of the user who created the mainnet token smart contract
    QTUM_CONTRACT_OWNER_ADDRESS = QTUM_MAINNET_CONTRACT_OWNER_ADDRESS

else:
    print("Luna does not know its run location.")
    exit(1)

ALLOWED_HOSTS = [
    'localhost',
    SITE_DOMAIN,
]

# AWS CREDENTIALS
##########################################################

BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME')
REGION_NAME = os.environ.get('AWS_DEFAULT_REGION')

# IMGIX Configuration
IMGIX_SOURCE=os.environ.get('IMGIX_SOURCE')
IMGIX_SIGN_KEY=os.environ.get('IMGIX_SIGN_KEY')
