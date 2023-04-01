import os

DATABASES = {
    'default': {
        'ENGINE': os.environ.get('DJANGO_MOVIES_DB_ENGINE'),
        'NAME': os.environ.get('PG_MOVIES_DB_NAME'),
        'USER': os.environ.get('PG_MOVIES_USER'),
        'PASSWORD': os.environ.get('PG_MOVIES_PASSWORD'),
        'HOST': os.environ.get('PG_MOVIES_DB_HOST', '127.0.0.1'),
        'PORT': os.environ.get('PG_MOVIES_DB_PORT', 5432),
        'OPTIONS': {
           'options': '-c search_path=public,content'
        }
    }
}
