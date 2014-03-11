# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'l1cx=%-owxv1hs8+55cxg^1p@fq_z72=$zzc5%doar+%#_3gg3'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True
ALLOWED_HOSTS = []

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": "wooster",
        "USER": "kevin",
        "PASSWORD": "",
        "HOST": "",
        "PORT": "",
    },
}
