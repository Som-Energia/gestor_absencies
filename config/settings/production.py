from datetime import timedelta
import yaml
from .base import *

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

with open(os.path.join(BASE_DIR, 'config/settings/config.yaml')) as f:
    config = yaml.load(f.read(), Loader=yaml.FullLoader)


DEBUG = False

SECRET_KEY = config['secret_key']

ALLOWED_HOSTS = [

    'gestorabsencies-demo.somenergia.local'
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config['databases']['prod']['name'],
        'USER': config['databases']['prod']['user'],
        'PASSWORD': config['databases']['prod']['password'],
        'HOST': config['databases']['prod']['host'],
        'PORT': config['databases']['prod']['port'],
    }
}

REST_FRAMEWORK['JWT_VERIFY_EXPIRATION'] = True
REST_FRAMEWORK['JWT_EXPIRATION_DELTA'] = timedelta(days=15)

CORS_ORIGIN_WHITELIST = config['whitelist']['develop']
