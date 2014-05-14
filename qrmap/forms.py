__author__ = 'root'
import csv
import simplejson
import urllib
import urlparse
import base64
import re
import qrcode
import hashlib
from django import forms
from django.contrib.sites.models import Site
from django.conf import settings
#models
from qrmap.models import EventQRCode, UserEventQrCode, Usuario


class EventForm(forms.ModelForm):

    class Meta:
        model = EventQRCode

    def save(self, commit=False):
        event_instance = super(EventForm, self).save(commit=False)
        event_instance.user = self.cleaned_data['user']
        event_instance.save()
        records = csv.reader(self.cleaned_data["file"])
        for line in records:
            user_event = UserEventQrCode(
                firstname=line[0],
                lastname=line[1],
                email=line[2],
                address=line[3],
                phone=line[4],
                cell_phone=line[5],
                event=event_instance
            )
            user_event.save()
            sha = hashlib.md5(str(user_event.pk)+str(user_event.email))
            user_event.url = 'http://%s/event/?name=%s&code=%s' % (Site.objects.all()[0], self.cleaned_data["url_name"], sha.hexdigest())
            user_event.image = 'http://%s/media/%s.jpg' % (Site.objects.all()[0], sha.hexdigest())
            user_event.save()
            site_object = Site.objects.all()[0]
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.ERROR_CORRECT_L,
                box_size=10,
                border=4
            )
            data = user_event.url
            qr.add_data(data)
            qr.make(fit=True)
            img = qr.make_image()
            img.save('%s/%s.jpg' % (settings.MEDIA_ROOT, str(sha.hexdigest())), "JPEG")
