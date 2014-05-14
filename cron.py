#!/usr/bin/python

#from django.core.email import EmailMessage

#message = "<p>Welcome</p>" #u'<p style="text-align: center; padding: 2em; background: #0AA8A6; width: 250px;"><img src="http://qmoqui.com/static/img/logo-w.png"></p><h2 style="color: #0AA8A6; font-size: 2.5em; margin: 20px 0;">Hello %s</h2><p style="line-height: 1.75em;">Welcome, and thank you for creating an account with QMOQUI!</p><p style="line-height: 1.75em;">Please click on the below to confirm your account. Once confirmed, you can create your profile and start creating your personal QR+ platform.</p><p style="line-height: 1.75em;"><a href="http://%s/activate/?token=%s" style="margin: 2.5em 0; display: block; width: 250px; text-align: center; padding: 2em; color: #fff; background: #0AA8A6;">Confirm your account email</a></p><p ssenders = "qmoqui.sender@gmail.com"
#recievers = "mauri544@gmail.com"
#text = 'Account Verification - QMoqui'
#msg = EmailMessage(text, message, "qmoqui.sender@gmail.com", [recievers])
#msg.content_subtype = "html"  # Main content is now text/htmsg.send()
#msg.send()
SMTPserver = 'smtp.gmail.com'
sender =     'qmoqui.sender@gmail.com'
destination = ['mauri544@gmail.com']

USERNAME = "qmoqui.sender@gmail.com"
PASSWORD = "G_04718802"

# typical values for text_subtype are plain, html, xml
text_subtype = 'plain'


content="""\
Test message
"""

subject="Sent from Python"

import sys
import os
import re

from smtplib import SMTP_SSL as SMTP       # this invokes the secure SMTP protocol (port 465, uses SSL)
# from smtplib import SMTP                  # use this for standard SMTP protocol   (port 25, no encryption)
from email.MIMEText import MIMEText

try:
    msg = MIMEText(content, text_subtype)
    msg['Subject']=       subject
    msg['From']   = sender # some SMTP servers will do this automatically, not all

    conn = SMTP(SMTPserver)
    conn.set_debuglevel(False)
    conn.login(USERNAME, PASSWORD)
    try:
        conn.sendmail(sender, destination, msg.as_string())
    finally:
        conn.close()

except Exception, exc:
    sys.exit( "mail failed; %s" % str(exc) ) # give a error message
