# -*- coding: utf-8 -*-
# Create your views here.

import simplejson
import urllib
import urlparse
import base64
import re
import qrcode
import hashlib
import smtplib
import stripe
import datetime
import random
import vobject

from django.conf import settings
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.http import HttpResponseRedirect, HttpResponse
from django.utils.http import urlencode
from django.core.mail import EmailMessage
from django.template import Template, Context
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth import authenticate, login
from django.db.models import Q, Count
from django.contrib.sites.models import Site
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
#models
from qrmap.models import Usuario, Code, Opening, UrlCode, CodeChanges, EventQRCode, \
    EventQrCodeUse, UserEventQrCode, Image as ImageUpload, BusinessCard, FieldBusiness, \
    SocialBusiness, Plan, Payment, RankBusiness, OpenBusiness
#facebook
from qrmap.facebook import Facebook
#forms
from qrmap.forms import EventForm
from easy_thumbnails.files import *


def index(request, url=None):
    if url:
        urlCode = UrlCode.objects.get(url=url)
        code_object = Code.objects.get(pk=urlCode.code.pk)
        code_changes_object = CodeChanges.objects.filter(code=code_object)
        if code_changes_object.count() > 0:
            opening_object = Opening(
                code=code_object,
                ip=request.META['REMOTE_ADDR'],
                user_agent=request.META['HTTP_USER_AGENT']
            )
            opening_object.save()
            return HttpResponseRedirect(code_changes_object[code_changes_object.count() - 1].new_url)
        else:
            opening_object = Opening(
                code=code_object,
                ip=request.META['REMOTE_ADDR'],
                user_agent=request.META['HTTP_USER_AGENT']
            )
            opening_object.save()
            return HttpResponseRedirect(code_object.url)
        #opening_object = Opening(
        #    code=code_object,
        #    ip=request.META['REMOTE_ADDR'],
        #    user_agent=request.META['HTTP_USER_AGENT']
        #)
        #opening_object.save()
        #return HttpResponseRedirect(code_object.url)
    else:
        if request.GET:
            if 'code' in request.GET:
                site_object = Site.objects.all()[0]
                args = {
                    'client_id': settings.FACEBOOK_APP_ID,
                    'redirect_uri': 'http://' + str(site_object.domain) + '/',
                    'client_secret': settings.FACEBOOK_API_SECRET,
                    'code': request.GET.get('code')
                }
                url = 'https://graph.facebook.com/oauth/access_token?' +\
                      urllib.urlencode(args)
                response = urlparse.parse_qs(urllib.urlopen(url).read())
                access_token = response['access_token'][0]
                expires = response['expires'][0]
                face = Facebook()
                user_face = face.authenticate(access_token, None, expires)
                request.session['user'] = user_face
                request.session.set_expiry(3600)
                request.session.modified = True
                return HttpResponseRedirect(reverse('index'))
        else:
            set_facebook = {
                'FACEBOOK_APP_ID': settings.FACEBOOK_APP_ID,
                'FACEBOOK_REDIRECT_URI': 'http://www.qmoqui.com/'
            }
            if request.META.has_key('HTTP_USER_AGENT'):
                user_agent = request.META['HTTP_USER_AGENT']
                pattern = "(up.browser|up.link|mmp|symbian|smartphone|midp|wap|phone|windows ce|pda|mobile|mini|palm|netfront)"
                prog = re.compile(pattern, re.IGNORECASE)
                match = prog.search(user_agent)
                if match:
                    return render_to_response(
                        'index_mobile.html',
                        {'settings': set_facebook},
                        context_instance=RequestContext(request)
                    )
                else:
                    user_is = False
                    usuario = None
                    if request.session.get("user"):
                        user_is = True
                        usuario = request.session["user"]
                    return render_to_response(
                        'index.html',
                        {
                            'settings': set_facebook,
                            'user': usuario,
                            'user_is': user_is
                        },
                        context_instance=RequestContext(request)
                    )


def login_face(request):
    set_facebook = {
        'FACEBOOK_APP_ID': settings.FACEBOOK_APP_ID,
        'FACEBOOK_REDIRECT_URI': 'http://www.qmoqui.com/'
    }
    return render_to_response(
        'dialog.html',
        {'settings': set_facebook},
        context_instance=RequestContext(request)
    )


def open_form(request):
    return render_to_response(
        'open_form.html',
        {},
        context_instance=RequestContext(request)
    )


def featured(request):
    user_is = False
    usuario = None
    if request.session.get("user"):
        user_is = True
        usuario = request.session["user"]
    return render_to_response(
        'featured.html',
        {
            'user': usuario,
            'user_is': user_is
        },
        context_instance=RequestContext(request)
    )


def plans(request):
    user_is = False
    usuario = None
    action = False
    if request.session.get("user"):
        user_is = True
        usuario = request.session["user"]
    if request.method == "GET":
        if 'action' in request.GET:
            if request.GET["action"] == "change-plan":
                action = True
    return render_to_response(
        'plans.html',
        {
            'user': usuario,
            'user_is': user_is,
            'action': action
        },
        context_instance=RequestContext(request)
    )


def privacy(request):
    return render_to_response(
        'privacy.html',
        {},
        context_instance=RequestContext(request)
    )


def getSessionFacebook(request):
    if request.GET:
        if 'access' in request.GET:
            dictionary = {}
            if request.session.get('user'):
                dictionary['session'] = True
            else:
                dictionary['session'] = False
            return HttpResponse(simplejson.dumps(dictionary))


@csrf_protect
def dashboard(request):
    if request.method == "POST":
        form_event = EventForm(request.POST, request.FILES)
        if form_event.is_valid():
            form_event.save()
            return HttpResponseRedirect('/dashboard/')
    else:
        user = request.session.get('user')
        code_objects = Code.objects.filter(user=user)
        site_object = Site.objects.all()[0]
        event_objects = EventQRCode.objects.filter(user=user)
        business_card = BusinessCard.objects.filter(user=user)
        if request.META.has_key('HTTP_USER_AGENT'):
            user_agent = request.META['HTTP_USER_AGENT']
            pattern = "(up.browser|up.link|mmp|symbian|smartphone|midp|wap|phone|windows ce|pda|mobile|mini|palm|netfront)"
            prog = re.compile(pattern, re.IGNORECASE)
            match = prog.search(user_agent)
            if match:
                return render_to_response(
                    'dashboard-mobile.html',
                    {
                        'user': user,
                        'codes': code_objects,
                        'site': site_object,
                        'form_event': EventForm(),
                        'events': event_objects,
                        'businesses': business_card
                    },
                    context_instance=RequestContext(request)
                )
            else:
                return render_to_response(
                    'dashboard.html',
                    {
                        'user': user,
                        'codes': code_objects,
                        'site': site_object,
                        'form_event': EventForm(),
                        'events': event_objects,
                        'businesses': business_card
                    },
                    context_instance=RequestContext(request)
                )


def endSession(request):
    try:
        del request.session['user']
    except KeyError:
        pass
    return HttpResponseRedirect(reverse('index'))


@csrf_protect
def generate_qr_code(request):
    if request.method == "POST":
        code_object = Code(
            url=request.POST["url"],
            name=request.POST["name"],
            type_qr='S',
            user=request.session.get("user")
        )
        code_object.save()
        sha = hashlib.md5(str(code_object.pk))
        url_code_object = UrlCode(
            code=code_object,
            url=sha.hexdigest()
        )
        url_code_object.save()
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.ERROR_CORRECT_L,
            box_size=10,
            border=4
        )
        site_object = Site.objects.all()[0]
        data = 'http://' + str(site_object.domain) + '/' + str(url_code_object.url)
        qr.add_data(data)
        qr.make(fit=True)
        img = qr.make_image()
        img.save('%s/%s.jpg' % (settings.MEDIA_ROOT, str(url_code_object.url)), "JPEG")
        if request.META.has_key('HTTP_USER_AGENT'):
            user_agent = request.META['HTTP_USER_AGENT']
            pattern = "(up.browser|up.link|mmp|symbian|smartphone|midp|wap|phone|windows ce|pda|mobile|mini|palm|netfront)"
            prog = re.compile(pattern, re.IGNORECASE)
            match = prog.search(user_agent)
            if match:
                return HttpResponseRedirect(reverse('dashboard'))
            else:
                repo = {
                    'msg': 'http://%s%s%s.jpg' % (Site.objects.all()[0],settings.MEDIA_URL, str(url_code_object.url)),
                    'url': '%s/%s.jpg' % (settings.MEDIA_URL, str(url_code_object.url)),
                    'id': code_object.pk,
                    'name': code_object.name,
                    'type': code_object.get_type_qr_display(),
                    'link': code_object.url
                }
                return HttpResponse(simplejson.dumps(repo))


@csrf_exempt
def get_open(request):
    if request.method=="GET":
        sha = request.GET['qrList']
        url_code_object = UrlCode.objects.get(url=sha)
        opening_objects = Opening.objects.filter(code__pk=url_code_object.code.pk)
        lista = []
        lista.append(opening_objects.count())
        lista_fecha = []
        lista_fecha = opening_objects.values("datetime")
        fechas_dia = Opening.objects.filter(code__pk=url_code_object.code.pk).datetimes("datetime","day")
        contador = []
        lista_por_dia = []
        #TODO: Obteniendo sumatoria por dia de apertura
        for i in fechas_dia:
            a = 0
            for j in lista_fecha:
                if j["datetime"].date() == i.date():
                    a += 1
                else:
                    lista_fecha[a:]
            contador.append(a)
            dictionary_fechas = {
                'name': i.date().strftime("%Y-%m-%d"),
                'cantidad': a
            }
            lista_por_dia.append(dictionary_fechas)

        dict_open = {
            'count':lista,
            'lista_por_dia': lista_por_dia
        }
        return HttpResponse(simplejson.dumps(dict_open))


@csrf_exempt
def getVisits(request):
    if 'event' in request.GET:
        event_object = EventQRCode.objects.get(pk=request.GET['event'])
        cantidad = 0
        user_objects = UserEventQrCode.objects.filter(event=event_object)
        for i in user_objects:
            use_event = EventQrCodeUse.objects.filter(user_event=i)
            q = use_event.count()
            cantidad += q
        lista_by_ocurrency = []
        for j in EventQrCodeUse.objects.values('ocurrency').annotate(count=Count('ocurrency')):
            dict_by_ocurrency = {
                'ocurrency': j['ocurrency'],
                'count': j['count']
            }
            lista_by_ocurrency.append(dict_by_ocurrency)
        dict_q = {
            'q': cantidad,
            'by_business': lista_by_ocurrency,
            'api': event_object.event_api
        }
        return HttpResponse(simplejson.dumps(dict_q))


def getCode(request,code):
    code_object = Code.objects.get(pk=code)
    site_object = Site.objects.all()[0]
    return render_to_response(
        'page-code.html',
        {
            'code': code_object,
            'site': site_object
        },
        context_instance=RequestContext(request)
    )


def event_by_user(request):
    if 'name' in request.GET:
        event_object = EventQRCode.objects.get(url_name=request.GET['name'])
        user_event = UserEventQrCode.objects.filter(event=event_object)
        user_zero = None
        for i in user_event:
            sha = hashlib.md5(str(i.pk)+str(i.email))
            if request.GET['code'] == sha.hexdigest():
                user_zero = i
                break
        if request.META.has_key('HTTP_USER_AGENT'):
            user_agent = request.META['HTTP_USER_AGENT']
            pattern = "(up.browser|up.link|mmp|symbian|smartphone|midp|wap|phone|windows ce|pda|mobile|mini|palm|netfront)"
            prog = re.compile(pattern, re.IGNORECASE)
            match = prog.search(user_agent)
            if match:
                return render_to_response(
                    'owner_business_mobile.html',
                    {
                        'user': user_zero,
                        'event': event_object
                    },
                    context_instance=RequestContext(request)
                )
            else:
                return render_to_response(
                    'owner_business.html',
                    {
                        'user': user_zero,
                        'event': event_object
                    },
                    context_instance=RequestContext(request)
                )


@csrf_exempt
def save_user_biz(request):
    if 'biz' in request.GET and 'user' in request.GET:
        msg = None
        try:
            event_use = EventQrCodeUse.objects.get(user_event__pk=request.GET['user'], ocurrency=request.GET['biz'])
            msg = 'Error!, User and Business already exists.'
        except EventQrCodeUse.DoesNotExist:
            user_object = UserEventQrCode.objects.get(pk=request.GET['user'])
            event_use = EventQrCodeUse(
                user_event=user_object,
                ocurrency=request.GET['biz']
            )
            event_use.save()
            msg = 'Thanks for register your business with QMoqui'
        dict_response = {
            'msg': msg
        }
        return HttpResponse(simplejson.dumps(dict_response))


@csrf_exempt
def createUser(request):
    if request.method == "POST":
        user_object = User.objects.create_user(request.POST["usuario"], request.POST["usuario"], request.POST["passwd"])
        user_object.save()
        usuario_object = Usuario(
            user=user_object,
            access_token=base64.b64encode(str(request.POST["usuario"])),
            expires=3600,
            userid = base64.b64encode(str(user_object.pk)),
            user_type='N'
        )
        usuario_object.save()
        plan_object = Plan(
            user=usuario_object,
            user_plan=request.POST["plan"],
            payment_method='C',
            start_date=datetime.datetime.now().date(),
            unregister_date=datetime.date.today() + datetime.timedelta(1*365/12),
        )
        plan_object.save()
        message = u'<p style="text-align: center; padding: 2em; background: #0AA8A6; width: 250px;"><img src="http://qmoqui.com/static/img/logo-w.png"></p><h2 style="color: #0AA8A6; font-size: 2.5em; margin: 20px 0;">Hello %s</h2><p style="line-height: 1.75em;">Welcome, and thank you for creating an account with QMOQUI!</p><p style="line-height: 1.75em;">Please click on the below to confirm your account. Once confirmed, you can create your profile and start creating your personal QR+ platform.</p><p style="line-height: 1.75em;"><a href="http://%s/activate/?token=%s" style="margin: 2.5em 0; display: block; width: 250px; text-align: center; padding: 2em; color: #fff; background: #0AA8A6;">Confirm your account email</a></p><p style="line-height: 1.75em;">Thanks again for choosing QMOQUI, The possibilities are endless............. </p><p style="line-height: 1.75em;">Please do not hesitate to contact us if you have any questions or suggestions: <a href="http://www.qmoqui.com/contact" style="color: #0AA8A6;">www.qmoqui.com/contact</a></p>' % (usuario_object.user.username, Site.objects.all()[0], usuario_object.access_token)
        senders = "sender@qmoqui.com"
        recievers = usuario_object.user.username
        text = 'Account Verification - QMoqui'
        msg = EmailMessage(text, message, senders, [recievers])
        msg.content_subtype = "html"  # Main content is now text/html
        msg.send()
        dict_response = {
            'msg': 'Account verification, check your email inbox',
            'response': True
        }
        return HttpResponse(simplejson.dumps(dict_response))


def new_account(request, type_plan):
    if type_plan:
        return render_to_response(
            'new_account.html',
            {
                'type_plan': type_plan
            },
            context_instance=RequestContext(request)
        )


def change_plan(request, type_plan):
    if type_plan:
        dict_plans = {
            'S': 'free',
            'M': 'simply',
            'Q': 'pro',
            'W': 'simply_no_trial',
            'T': 'pro_no_trial'
        }
        customer_object = None
        stripe.api_key = "sk_test_uQa3bWOX6fcs7eJCFJ6R25Zl"
        user = request.session.get("user")
        plan = user.plan
        plan.user_plan = type_plan
        plan.start_date = datetime.datetime.now().date()
        plan.save()
        customers = stripe.Customer.all()
        if customers.count > 0:
            for customer in customers.data:
                if user.user.username == customer.email:
                    customer_object = customer
                    break
        customer_object.update_subscription(plan=dict_plans[type_plan], prorate=True)
        return HttpResponseRedirect(reverse('account-settings'))


def account_settings(request):
    stripe.api_key = "sk_test_uQa3bWOX6fcs7eJCFJ6R25Zl"
    flag = False
    user = None
    payment_flag = False
    payment_info = None
    customer_object = None
    invoice_object = None
    if request.session.get("user"):
        flag = True
        user = request.session.get("user")
        payment_object = Payment.objects.filter(user=user)
        if payment_object.count() > 0:
            payment_flag = True
            payment_info = payment_object[payment_object.count()-1]
            customers = stripe.Customer.all()
            if customers.count > 0:
                for customer in customers.data:
                    if user.user.username == customer.email:
                        customer_object = customer
                        break
            invoices = stripe.Invoice.upcoming(customer=customer_object.id)
            if invoices.lines.count > 0:
                invoice_object = invoices
    return render_to_response(
        'settings.html',
        {
            'flag': flag,
            'user': user,
            'payment_flag': payment_flag,
            'payment': payment_info,
            'customer': customer_object,
            'invoice': invoice_object
        },
        context_instance=RequestContext(request)
    )


def activateToken(request):
    if request.method == "GET":
        try:
            usuario_object = Usuario.objects.get(access_token=request.GET["token"])
            plan_object = Plan.objects.get(user=usuario_object)
            plan_object.activate = True
            plan_object.save()
            return render_to_response(
                'activate.html',
                {
                    'user': usuario_object
                },
                context_instance=RequestContext(request)
            )
        except Usuario.DoesNotExist:
            pass


@csrf_protect
def loginAccount(request):
    if request.method == "POST":
        username = request.POST["user"]
        password = request.POST["password"]
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                usuario_object = Usuario.objects.get(user=user)
                request.session["user"] = usuario_object
                dict_response = {
                    'msg': 'Login successful',
                    'response': True
                }
                return HttpResponse(simplejson.dumps(dict_response))
            else:
                dict_response = {
                    'msg': 'Error',
                    'response': False
                }
                return HttpResponse(simplejson.dumps(dict_response))


def reader(request):
    if request.META.has_key('HTTP_USER_AGENT'):
        user_agent = request.META['HTTP_USER_AGENT']
        pattern = "(up.browser|up.link|mmp|symbian|smartphone|midp|wap|phone|windows ce|pda|mobile|mini|palm|netfront)"
        prog = re.compile(pattern, re.IGNORECASE)
        match = prog.search(user_agent)
        if match:
            return render_to_response(
                'mreader.html',
                {},
                context_instance=RequestContext(request)
            )
        else:
            return render_to_response(
                'reader.html',
                {},
                context_instance=RequestContext(request)
            )


@csrf_exempt
def uploadImage(request):
    if request.method == "POST":
        #file =  request.META["HTTP_X_FILENAME"]
        image_object = ImageUpload(
            img=request.FILES['file']
        )
        image_object.save()
        request.session['img'] = image_object.id
        thumbnailer = get_thumbnailer(image_object.img)
        thumb = thumbnailer.get_thumbnail({'size': (300, 300)})
        thumb = thumbnailer.get_thumbnail_name({'size': (300, 300)})
        thumbStr = thumb.replace("\\", "/")
        thumbnail = "/media/" + thumbStr
        return HttpResponse(thumbnail)
    else:
        return HttpResponse("not save")


@csrf_exempt
def testPreview(request):
    if request.method == "GET":
        business_card_object = BusinessCard(
            name=request.GET["name"],
            url_name=slugify(request.GET["qrname"]),
            bg_color=request.GET["bg"],
            bio=request.GET["bio"],
            user=request.session["user"]
        )
        business_card_object.save()
        request.session["last_biz"] = business_card_object
        image_object = ImageUpload.objects.get(pk=request.session["img"])
        image_object.business_card = business_card_object
        image_object.save()
        if 'phones' in request.GET:
            objects_phones = str(request.GET["phones"]).split(",")
            if len(objects_phones)>1:
                for p in objects_phones:
                    field_object = FieldBusiness(
                        type_record_field="P",
                        val_record_field=p,
                        business_card=business_card_object
                    )
                    field_object.save()
            else:
                field_object = FieldBusiness(
                    type_record_field="P",
                    val_record_field=objects_phones[0],
                    business_card=business_card_object
                )
                field_object.save()
        if 'emails' in request.GET:
            objects_emails = str(request.GET["emails"]).split(",")
            if len(objects_emails)>1:
                for p in objects_email:
                    field_object = FieldBusiness(
                        type_record_field="E",
                        val_record_field=p,
                        business_card=business_card_object
                    )
                    field_object.save()
            else:
                field_object = FieldBusiness(
                    type_record_field="E",
                    val_record_field=objects_emails[0],
                    business_card=business_card_object
                )
                field_object.save()
        if 'addresses' in request.GET:
            objects_addresses = str(request.GET["addresses"]).split(";")
            if len(objects_addresses)>1:
                for p in objects_addresses:
                    field_object = FieldBusiness(
                        type_record_field="A",
                        val_record_field=p,
                        business_card=business_card_object
                    )
                    field_object.save()
            else:
                field_object = FieldBusiness(
                    type_record_field="A",
                    val_record_field=objects_addresses[0],
                    business_card=business_card_object
                )
                field_object.save()
        if 'texts' in request.GET:
            objects_texts = str(request.GET["texts"]).split(",")
            if len(objects_texts)>1:
                for p in objects_phones:
                    field_object = FieldBusiness(
                        type_record_field="T",
                        val_record_field=p,
                        business_card=business_card_object
                    )
                    field_object.save()
            else:
                field_object = FieldBusiness(
                    type_record_field="T",
                    val_record_field=objects_texts[0],
                    business_card=business_card_object
                )
                field_object.save()
        if 'websites' in request.GET:
            objects_websites = str(request.GET["websites"]).split(",")
            if len(objects_websites)>1:
                for p in objects_websites:
                    field_object = FieldBusiness(
                        type_record_field="W",
                        val_record_field=p,
                        business_card=business_card_object
                    )
                    field_object.save()
            else:
                field_object = FieldBusiness(
                    type_record_field="W",
                    val_record_field=objects_websites[0],
                    business_card=business_card_object
                )
                field_object.save()
        shaBiz = hashlib.md5(str(business_card_object.pk))
        code_object = Code(
            url='http://%s/preview/%s/' % (Site.objects.all()[0], shaBiz.hexdigest()),
            name=request.GET["qrname"],
            type_qr="P",
            user=request.session.get("user")
        )
        code_object.save()
        sha = hashlib.md5(str(code_object.pk))
        url_code_object = UrlCode(
            code=code_object,
            url=sha.hexdigest()
        )
        url_code_object.save()
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.ERROR_CORRECT_L,
            box_size=10,
            border=4
        )
        site_object = Site.objects.all()[0]
        data = 'http://' + str(site_object.domain) + '/' + str(url_code_object.url)
        qr.add_data(data)
        qr.make(fit=True)
        img = qr.make_image()
        img.save('%s/%s.jpg' % (settings.MEDIA_ROOT, str(url_code_object.url)), "JPEG")
        repo = {
            'msg': 'http://%s%s%s.jpg' % (Site.objects.all()[0],settings.MEDIA_URL, str(url_code_object.url)),
            'url': '%s%s.jpg' % (settings.MEDIA_URL, str(url_code_object.url)),
            'id': code_object.pk,
            'link': code_object.url,
            'biz': shaBiz.hexdigest()
        }
        return HttpResponse(simplejson.dumps(repo))


@csrf_exempt
def activeBizCard(request):
    if request.method == "GET":
        object_business = None
        biz_objects_card = BusinessCard.objects.filter(active=False)
        for i in biz_objects_card:
            sha = hashlib.md5(str(i.pk))
            if request.GET["biz"] == sha.hexdigest():
                object_business = i
                object_business.active = True
                object_business.save()
                break
        code_objects = Code.objects.get(pk=request.GET["code"])
        new_code_changes = CodeChanges(
            new_url='http://%s/myqr/%s/' % (Site.objects.all()[0], request.GET["biz"]),
            code=code_objects
        )
        new_code_changes.save()
        return HttpResponse("Your My QR+ is active")


@csrf_exempt
def preview(request, code=None):
    code_objects = Code.objects.get(url='http://%s/preview/%s/' % (Site.objects.all()[0], code))
    if code:
        object_business = None
        biz_objects_card = BusinessCard.objects.filter(active=False)
        for i in biz_objects_card:
            sha = hashlib.md5(str(i.pk))
            if code == sha.hexdigest():
                object_business = i
                break
        return render_to_response(
            'preview-vcard.html',
            {
                'business': object_business
            },
            context_instance=RequestContext(request)
        )


@csrf_exempt
def myqr(request, code=None):
    if code:
        object_business = None
        biz_objects_card = BusinessCard.objects.filter(active=True)
        for i in biz_objects_card:
            sha = hashlib.md5(str(i.pk))
            if code == sha.hexdigest():
                object_business = i
                break
        return render_to_response(
            'preview-vcard.html',
            {
                'business': object_business
            },
            context_instance=RequestContext(request)
        )


@csrf_exempt
def business_myqr(request, url=None):
    if url:
        session = False
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        if request.session.get("rank"): session = True
        biz_objects = BusinessCard.objects.get(url_name=url)
        rank_objects = RankBusiness.objects.filter(business_card=biz_objects).distinct()
        rank_objects_count = rank_objects.count()
        total = 0
        avg_rank = None
        if not request.session.get("open"):
            open_objects = OpenBusiness(
                ip=ip,
                business_card=biz_objects
            )
            open_objects.save()
            request.session["open"] = True
        open_business = OpenBusiness.objects.filter(business_card=biz_objects).distinct()
        if rank_objects:
            for i in rank_objects:
                total = total + i.vote
            avg_rank = total/rank_objects_count
        return render_to_response(
            'preview-bcard.html',
            {
                'business': biz_objects,
                'session': session,
                'avg_rank': avg_rank,
                'total': rank_objects_count,
                'open': open_business.count()
            },
            context_instance=RequestContext(request)
        )


@csrf_exempt
def billing(request):
    if request.method == "POST":
        user = request.session.get("user")
        stripe.api_key = "sk_test_uQa3bWOX6fcs7eJCFJ6R25Zl"
        # Create a Customer
        token = request.POST['stripeToken']
        plan_object = Plan.objects.get(user=user)
        customer = stripe.Customer.create(
          card=token,
          plan=plan_object.get_user_plan_display(),
          email=user.user.username
        )
        payment_object = Payment(
            name=request.POST["card-name"],
            address=request.POST["billing"],
            card_type=request.POST["card-type"],
            card_number=request.POST["card-number"],
            exp_month=request.POST["exp-month"],
            exp_year=request.POST["exp-year"],
            cvc=request.POST["cvc"],
            user=user
        )
        payment_object.save()
        return HttpResponseRedirect(reverse('account-settings'))


@csrf_exempt
def vcard_object(request, url):
    if request.method == "POST":
        if "emailvcard" in request.POST:
            emailvcard = request.POST['emailvcard']
            business_card = BusinessCard.objects.get(url_name=url)
            v = vobject.vCard()
            v.add('n')
            v.n.value = vobject.vcard.Name(family=business_card.name, given=business_card.name)
            v.add('fn')
            v.fn.value = "%s %s" % (business_card.name, business_card.name)
            v.add('email')
            v.email.value = u'%s' % str(business_card.fieldbusiness_set.filter(type_record_field='E')[0])
            v.add('tel')
            v.tel.value = u'%s' % str(business_card.fieldbusiness_set.filter(type_record_field='P')[0])
            v.tel.type_param = 'WORK'
            v.add('url')
            v.url.value = u'%s' % str(business_card.websitecard_set.all()[0].url)
            output = v.serialize()
            filename = "%s.vcf" % (business_card.url_name)
            #response = HttpResponse(output, mimetype="text/x-vCard")
            #response['Content-Disposition'] = 'attachment; filename=%s' % filename
            myvcf = open('%s%s' % (settings.MEDIA_ROOT, filename), 'w')
            myvcf.write(output)
            myvcf.close()
            body = u'''
            <h1 style="background: #0AA8A6; padding: 8px;"><img src="http://qmoqui.com/static/img/logo-w.png"/></h1>
            <p>Add <b>%s</b> to your contact list from the file attached</p>
            ''' % business_card.name
            emailmsg = EmailMessage('Your new contact', body, 'Qmoqui <no-reply@qmoqui.com>', [emailvcard,])
            emailmsg.attach_file('%s%s' % (settings.MEDIA_ROOT, filename))
            emailmsg.content_subtype = "html"
            emailmsg.send()
            return HttpResponse('Please check your email inbox')


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def rank_business(request, url):
    if request.method == "POST":
        if "rank" in request.POST:
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                ip = x_forwarded_for.split(',')[0]
            else:
                ip = request.META.get('REMOTE_ADDR')
            business_card_object = BusinessCard.objects.get(url_name=url)
            rank_object = RankBusiness(
                vote=request.POST["rank"],
                ip=ip,
                business_card=business_card_object
            )
            rank_object.save()
            request.session["rank"] = ip
            return HttpResponse("Thanks for rank me!!!")


def check_rank_session(request):
    if request.method == "GET":
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        response = 0
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        if request.session.get("rank"):
            if ip == request.session["rank"]: response = 1
        return HttpResponse(response)


def report(request):
    code_objects = Code.objects.all().distinct()
    return render_to_response(
        'reports.html',
        {
            'codes': code_objects
        },
        context_instance=RequestContext(request)
    )


