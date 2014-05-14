import httplib2
import simplejson
import urllib
from django.contrib.auth.models import User
from qrmap.models import Usuario
from django.conf import settings

__author__ = 'mauricio'

class Facebook:

    def refresh_token(self):
        url = 'https://graph.facebook.com/oauth/authorize?client_id=%s&redirect_uri=%s&scope=publish_stream,email&display=popup' % (settings.FACEBOOK_APP_ID,settings.FACEBOOK_REDIRECT_URI)
        return url

    def authenticate(self,access_token=None,user=None,expires=None):
        user_facebook = None
        try:
            url = 'https://graph.facebook.com/me?access_token=%s' \
            % access_token
            response = simplejson.load(urllib.urlopen(url))
            user_facebook = Usuario.objects.get(
                userid = response['id']
            )
            profile = user_facebook.query()
            user_facebook.access_token = access_token
            user_facebook.expires = expires
            user_facebook.save()
        except Usuario.DoesNotExist:
            user_facebook = Usuario(
                access_token = access_token
            )    
            user_facebook.save()            
            profile = user_facebook.query()
            user_object = User.objects.create_user(profile['email'])
            user_object.set_unusable_password()
            user_object.backend='qrmap.facebook.Facebook'
            user_object.email = profile['email']
            user_object.first_name = profile['first_name']
            user_object.last_name = profile['last_name']
            user_object.is_active = True
            user_object.save() 
            user_facebook.expires = expires
            user_facebook.userid = profile['id']
            user_facebook.user = user_object
            user_facebook.save()
        return user_facebook

    def authenticate_only_facebook(self,access_token=None):
        user_facebook = Usuario.objects.get(
            access_token=access_token
        )
        profile = user_facebook.query()
        try:
            user = Usuario.objects.get(user__username = profile['email'])
        except Usuario.DoesNotExist, e:
            user = User(username = profile['email'])

        user.set_unusable_password()
        user.backend='qrmap.facebook.Facebook'
        user.email = profile['email']
        user.first_name = profile['first_name']
        user.last_name = profile['last_name']
        user.is_active = True
        user.save()

        try:
            Usuario.objects.get(userid=profile['id']).delete()
        except Usuario.DoesNotExist, e:
            pass

        user_facebook.uid = profile['id']
        user_facebook.user = user
        user_facebook.save()

        return user

    def createUserConect(self,access_token,user_connect):
        user_facebook = Usuario.objects.get(
            access_token=access_token
        )
        profile = user_facebook.query()
        user_facebook.userid = profile['id']
        print profile['id']
        user_facebook.user = user_connect
        user_facebook.save()

        return user_facebook

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
