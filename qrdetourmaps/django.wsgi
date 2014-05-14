import os
import sys

path = '/var/www/detour'
if path not in sys.path:
    sys.path.append(path)
    sys.path.append(path + "/qrdetourmaps")

os.environ['DJANGO_SETTINGS_MODULE'] = 'qrdetourmaps.settings'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
