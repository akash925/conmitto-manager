from .base import *
from .dev import *
import logging
import os
from .utils import get_env_variable
try:
    from .local import *
except ImportError:
    pass

logging.disable(logging.WARNING)

redis_host = os.environ.get('REDIS_HOST', 'localhost')

# Celery
CELERY_BROKER_URL = 'redis://%s' % redis_host

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [('redis://%s:6379' % os.environ.get('REDIS_HOST', 'localhost'))],
        }
    },
}

BROKER_BACKEND = 'memory'
CELERY_ALWAYS_EAGER = True
DATABASES = {
    # for unit tests
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.spatialite',
        'NAME': 'conmitto'
    }
}
