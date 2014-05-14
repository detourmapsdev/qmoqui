#!/usr/bin/python
import sys, os

sys.path.append('/home/qrdetourmaps')
sys.path.append('/usr/local/lib/python2.7/dist-packages/django/bin')
#sys.path.append('/home/ohgoditb/django_src')
sys.path.append('/usr/local/lib/python2.7/dist-packages')
sys.path.append('/usr/bin/')

os.environ['DJANGO_SETTINGS_MODULE'] = 'qrdetourmaps.settings'


from django.core.mail import EmailMessage
from qrmap.models import Usuario
user = Usuario.objects.get(pk=19)
message = u"<p>Welcome to the schedule for QMoqui</p>" #'<p style="text-align: center; padding: 2em; background: #0AA8A6; width: 250px;"><img src="http://qmoqui.com/static/img/logo-w.png"></p><h2 style="color: #0AA8A6; font-size: 2.5em; margin: 20px 0;">Hello %s</h2><p style="line-height: 1.75em;">Welcome, and thank you for creating an account with QMOQUI!</p><p style="line-height: 1.75em;">Please click on the below to confirm your account. Once confirmed, you can create your profile and start creating your personal QR+ platform.</p><p style="line-height: 1.75em;"><a href="http://%s/activate/?token=%s" style="margin: 2.5em 0; display: block; width: 250px; text-align: center; padding: 2em; color: #fff; background: #0AA8A6;">Confirm your account email</a></p><p style="line-height: 1.75em;">Thanks again for choosing QMOQUI, The possibilities are endless............. </p><p style="line-height: 1.75em;">Please do not hesitate to contact us if you have any questions or suggestions: <a href="http://www.qmoqui.com/contact" style="color: #0AA8A6;">www.qmoqui.com/contact</a></p>' % (usuario_object.user.username, Site.objects.all()[0], usuario_object.access_token)
senders = "sender@qmoqui.com"
recievers = user.user.username
text = 'Account Verification - QMoqui'
msg = EmailMessage(text, message, senders, [recievers, "manuel@detourmaps.com", "test.detourmaps@gmail.com"])
msg.content_subtype = "html"  # Main content is now text/html
msg.send()
