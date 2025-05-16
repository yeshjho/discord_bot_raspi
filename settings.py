# for django orm
import os


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': f'{BASE_DIR}/discord.db',
    }
}

INSTALLED_APPS = (
    'db.dictionary',
)

SECRET_KEY = os.getenv('DISCORD_BOT_DJANGO_SECRET_KEY')

TIME_ZONE = 'Asia/Seoul'
