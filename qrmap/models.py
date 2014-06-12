import simplejson
import urllib
import base64
import hashlib
import requests
import smtplib
from django.db import models
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.core.mail import EmailMessage

# Create your models here.

class Usuario(models.Model):
    CHOICES_USER_TYPE = (
        ('F', 'Facebook'),
        ('G', 'Google +'),
        ('T', 'Twitter'),
        ('N', 'Native')
    )
    user = models.ForeignKey(User, null=True)
    access_token = models.CharField(max_length=255, unique=True)
    expires = models.IntegerField(null=True)
    userid = models.CharField(max_length=200, unique=True, null=True)
    session_key = models.CharField(max_length=255, blank=True, null=True)
    user_type = models.CharField(max_length=1, choices=CHOICES_USER_TYPE, blank=True, null=True)

    def __unicode__(self):
        return '%s' % self.user

    class Meta:
        ordering = ('id',)

    def query(self):
        """
        operacion para obtener uid and time expires
        """
        url = 'https://graph.facebook.com/me?access_token=%s'\
              % self.access_token
        response = simplejson.load(urllib.urlopen(url))
        return response


class Plan(models.Model):
    CHOICES_TIPO = (
        ('S', 'free'),
        ('M', 'simply'),
        ('Q', 'pro'),
        ('W', 'simply_no_trial'),
        ('T', 'pro_no_trial')
    )
    CHOICES_METHOD = (
        ('T', 'Free'),
        ('C', 'Credit Card'),
        ('H', 'Cash')
    )
    user = models.OneToOneField(Usuario)
    user_plan = models.CharField(max_length=1, choices=CHOICES_TIPO)
    payment_method = models.CharField(max_length=1, choices=CHOICES_METHOD, blank=True, null=True)
    start_date = models.DateField(auto_now_add=True, verbose_name='Start date')
    unregister_date = models.DateField(auto_now_add=False, verbose_name='Unregister date', blank=True)
    active = models.BooleanField(default=True)

    def __unicode__(self):
        return '%s, %s' % (self.user.user.username, self.get_user_plan_display())

    def save(self):
        if self.user_plan == 'F':
            self.payment_method = 'T'
        super(Plan, self).save()


class Payment(models.Model):
    name = models.CharField(max_length=45, blank=True, null=True)
    address = models.CharField(max_length=90, blank=True, null=True)
    card_type = models.CharField(max_length=20, blank=True, null=True)
    card_number = models.CharField(max_length=24, blank=True, null=True)
    exp_month = models.CharField(max_length=2, blank=True, null=True)
    exp_year = models.CharField(max_length=4, blank=True, null=True)
    cvc = models.CharField(max_length=4, blank=True, null=True)
    user = models.ForeignKey(Usuario)


class Code(models.Model):
    CHOICES_TYPE = (
        ('S', 'Simple QR'),
        ('P', 'My QR+')
    )
    name = models.CharField(max_length=90, blank=True, null=True)
    type_qr = models.CharField(max_length=1, choices=CHOICES_TYPE, blank=True, null=True, verbose_name='Type')
    url = models.URLField()
    image = models.ImageField(upload_to='codes', blank=True, null=True)
    is_trackable = models.BooleanField(default=True)
    get_email = models.BooleanField(default=True)
    user = models.ForeignKey(Usuario)

    def __unicode__(self):
        return u'%s' % self.url

    def decoder(self):
        sha = hashlib.md5(str(self.pk))
        deco = sha.hexdigest()
        return deco


class EventQRCode(models.Model):
    file = models.FileField(upload_to='events', blank=True, null=True)
    date_time = models.DateTimeField(auto_now=True)
    name = models.CharField(max_length=45)
    url_name = models.SlugField()
    event_api = models.URLField(blank=True, null=True, verbose_name='API Event', help_text='A Valid URI API, offer by third party')
    user = models.ForeignKey(Usuario, blank=True, null=True)

    def __unicode__(self):
        return self.name


class UserEventQrCode(models.Model):
    firstname = models.CharField(max_length=45, verbose_name='First Name')
    lastname= models.CharField(max_length=45, verbose_name='Last Name')
    email = models.EmailField()
    address = models.CharField(max_length=120)
    phone = models.CharField(max_length=16)
    cell_phone = models.CharField(max_length=16)
    url = models.URLField(blank=True, null=True)
    image = models.URLField(blank=True, null=True)
    event = models.ForeignKey(EventQRCode)

    def __unicode__(self):
        return '%s, %s' % (self.firstname, self.lastname)


class EventQrCodeUse(models.Model):
    user_event = models.ForeignKey(UserEventQrCode)
    ocurrency = models.CharField(max_length=90)
    time_ocurrency = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return '%s' % self.user_event.email


class CodeChanges(models.Model):
    new_url = models.URLField()
    code = models.ForeignKey(Code)

    def __unicode__(self):
        return u'%s' % self.new_url


class UrlCode(models.Model):
    code = models.ForeignKey(Code)
    url = models.CharField(max_length=255)

    def __unicode__(self):
        return u'%s' % self.code


class Opening(models.Model):
    code = models.ForeignKey(Code)
    email = models.EmailField(blank=True, null=True)
    datetime = models.DateTimeField(blank=True, null=True, auto_now=True)
    ip = models.IPAddressField(blank=True, null=True)
    user_agent = models.CharField(max_length=255, blank=True, null=True)
    ubicaciion = models.CharField(max_length=45, blank=True, null=True)

    def __unicode__(self):
        return '%s' % self.code


class BusinessCard(models.Model):
    CHOICES_CARD = (
        ('B', 'Business'),
        ('P', 'Personal')
    )
    type_card = models.CharField(max_length=1, blank=True, null=True, choices=CHOICES_CARD, verbose_name='Card Type')
    name = models.CharField(max_length=90)
    url_name = models.SlugField(blank=True, null=True)
    position = models.CharField(max_length=60, blank=True, null=True)
    bg_color = models.CharField(max_length=7, default='#ffffff')
    bio = models.TextField()
    website = models.URLField(blank=True, null=True)
    has_video = models.BooleanField(default=False, verbose_name='Has Video?')
    video = models.URLField(blank=True, null=True)
    service_product = models.TextField(blank=True, null=True)
    user = models.ForeignKey(Usuario)
    active = models.BooleanField(default=False)

    def __unicode__(self):
        return '%s' % self.name

    class Meta:
        verbose_name = 'Business card'


class MoreInformationCard(models.Model):
    name = models.CharField(max_length=60)
    url_name = models.SlugField()
    business_card = models.ForeignKey(BusinessCard)

    def __unicode__(self):
        return '%s' % self.name

    class Meta:
        verbose_name = 'Add More Information to MyQR+'


class FieldMoreInformation(models.Model):
    CHOICES_FIELD = (
        ('A', 'Address'),
        ('P', 'Phone'),
        ('T', 'Text'),
        ('E', 'Email')
    )
    type_record_field = models.CharField(max_length=1, choices=CHOICES_FIELD)
    name = models.CharField(max_length=60, blank=True, null=True)
    val_field = models.CharField(max_length=120)
    more_information = models.ForeignKey(MoreInformationCard)


class GalleryCard(models.Model):
    name = models.CharField(max_length=45, blank=True, null=True)
    img = models.ImageField(upload_to='business-card')
    business_card = models.ForeignKey(BusinessCard)


class WebsiteCard(models.Model):
    url = models.URLField()
    business_card = models.ForeignKey(BusinessCard)


class Image(models.Model):
    img = models.ImageField(upload_to='img-business')
    business_card = models.ForeignKey(BusinessCard, blank=True, null=True)

    def __unicode__(self):
        return '%s' % self.img

    class Meta:
        verbose_name = 'Image'


class FieldBusiness(models.Model):
    CHOICES_FIELD = (
        ('A', 'Address'),
        ('P', 'Phone'),
        ('T', 'Text'),
        ('E', 'Email'),
        ('W', 'Website')
    )
    type_record_field = models.CharField(max_length=1, choices=CHOICES_FIELD)
    val_record_field = models.CharField(max_length=120)
    business_card = models.ForeignKey(BusinessCard, blank=True, null=True)

    def __unicode__(self):
        return '%s' % self.val_record_field

    class Meta:
        verbose_name_plural = 'Fields for business card'


class CouponBusiness(models.Model):
    image = models.ImageField(upload_to='coupons')
    business_card = models.ForeignKey(BusinessCard)

    def __unicode__(self):
        return '%s, %s' % (self.image, self.business_card.name)

    class Meta:
        verbose_name = 'Coupon for Business Card'
        verbose_name_plural = 'Coupons for Business Card'


class RankBusiness(models.Model):
    vote = models.IntegerField()
    ip = models.IPAddressField()
    business_card = models.ForeignKey(BusinessCard)

    def __unicode__(self):
        return '%s from %s, %s' % (self.vote, self.ip, self.business_card.name)

    class Meta:
        verbose_name = 'Rank'
        verbose_name_plural = 'Rank'


class OpenBusiness(models.Model):
    ip = models.IPAddressField()
    business_card = models.ForeignKey(BusinessCard)

    def __unicode__(self):
        return '%s from %s' % (self.ip, self.business_card.name)

    class Meta:
        verbose_name = 'Opened Business Card'
        verbose_name_plural = 'Opened Business Card'


class SocialBusiness(models.Model):
    CHOICES_NETWORK = (
        ('F', 'Facebook'),
        ('T', 'Twitter'),
        ('G', 'Google +'),
        ('K', 'Flickr'),
        ('Y', 'YouTube'),
        ('S', 'Skype'),
        ('U', 'Tumblr'),
        ('L', 'Linkedin'),
        ('P', 'Pinterest')
    )
    type_network = models.CharField(max_length=1, choices=CHOICES_NETWORK)
    url_network = models.URLField()
    business_card = models.ForeignKey(BusinessCard, blank=True, null=True)

    def __unicode__(self):
        return '%s' % self.url_network

    class Meta:
        verbose_name_plural = 'Social network for business card'
