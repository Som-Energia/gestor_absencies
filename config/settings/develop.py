from .base import *
import yaml


BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

with open(os.path.join(BASE_DIR, 'config/settings/config.yaml')) as f:
    config = yaml.load(f.read(), Loader=yaml.FullLoader)


DEBUG = True

SECRET_KEY = '*l@3iz$!9j3_tbeb-y+s*4^#$e_lddbe9a-4+4%0uc@ovjdn1j'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config['databases']['develop']['name'],
        'USER': config['databases']['develop']['user'],
        'PASSWORD': config['databases']['develop']['password'],
        'HOST': config['databases']['develop']['host'],
        'PORT': config['databases']['develop']['port'],
    }
}

CORS_ORIGIN_WHITELIST = config['whitelist']['develop']

RQ_QUEUES = {
    'default': {
        'HOST': 'redis',
        'PORT': 6379,
        'DB': 0,
        'DEFAULT_TIMEOUT': 360,
    }
}
