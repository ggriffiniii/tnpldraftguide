import os
import sys
sys.path.append('/www')
sys.path.append('/www/tnpldraft')

os.environ['DJANGO_SETTINGS_MODULE'] = 'tnpldraft.apache_settings'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
