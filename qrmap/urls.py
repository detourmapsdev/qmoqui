# -*- coding: utf-8 -*-
__author__ = 'mauricio'

from django.conf.urls import patterns, url

urlpatterns = patterns('qrmap.views',
    url(r'^$', 'index', name='index'),
    url(r'^(?P<url>\w+)$', 'index', name='tracker'),
    url(r'^event/$', 'event_by_user', name='event_by_user'),
    url(r'^qr-reader/$', 'reader', name='reader'),
    url(r'^getSession/$', 'getSessionFacebook', name='getSession'),
    url(r'^dashboard/$', 'dashboard', name='dashboard'),
    url(r'^endSession/$', 'endSession', name='endSession'),
    url(r'^saveCode/$', 'generate_qr_code', name='saveCode'),
    url(r'^getOpening/$', 'get_open', name='open'),
    url(r'^getVisits/$', 'getVisits', name='visits'),
    url(r'^featured-benefits/$', 'featured', name='featured'),
    url(r'^plans-pricing/$', 'plans', name='plans'),
    url(r'^privacy-policy/$', 'privacy', name='privacy'),
    url(r'^facebook/$', 'login_face', name='facebook'),
    url(r'^form/$', 'open_form', name='form'),
    url(r'^new-account/(?P<type_plan>\w+)/$', 'new_account', name='new-account'),
    url(r'^account-settings/$', 'account_settings', name='account-settings'),
    url(r'^confirm/$', 'save_user_biz', name='confirm'),
    url(r'^code/(?P<code>\d+)/$', 'getCode', name='code'),
    url(r'^createAccount/$', 'createUser', name='create-user'),
    url(r'^change-plan/(?P<type_plan>\w+)/$', 'change_plan', name='change-plan'),
    url(r'^activate/$', 'activateToken', name='activate-token'),
    url(r'^login-accoutn/$', 'loginAccount', name='login-account'),
    url(r'^preview/$', 'testPreview', name='preview'),
    url(r'^billing/$', 'billing', name='billing'),
    url(r'^active/$', 'activeBizCard', name='active'),
    url(r'^upload/$', 'uploadImage', name='upload'),
    url(r'^preview/(?P<code>\w+)/$', 'preview', name='preview'),
    url(r'^myqr/business/(?P<url>[-\w]+)/$', 'business_myqr', name='biz-myqr'),
    url(r'^vcard/(?P<url>[-\w]+)/$', 'vcard_object', name='vcard'),
    url(r'^rank/(?P<url>[-\w]+)/$', 'rank_business', name='rank'),
    url(r'^check-rank/(?P<url>[-\w]+)/$', 'check_rank_session', name='check-rank'),
    url(r'^myqr/(?P<code>\w+)/$', 'myqr', name='myqr'),
    url(r'^code-reports/$', 'report', name='report'),
)
