__author__ = 'mauricio'

from django.contrib import admin
#models
from qrmap.models import Usuario, Code, Opening, CodeChanges, UrlCode, EventQRCode, EventQrCodeUse, UserEventQrCode, \
    Image, BusinessCard, FieldBusiness, SocialBusiness, GalleryCard, WebsiteCard, MoreInformationCard, FieldMoreInformation, \
    Plan, Payment, CouponBusiness, RankBusiness, OpenBusiness

class AdminEvent(admin.ModelAdmin):

    prepopulated_fields = {'url_name': ('name',)}


class AdminUserEvent(admin.ModelAdmin):

    list_display = ['firstname', 'lastname', 'url', 'image']


class AdminCode(admin.ModelAdmin):

    list_display = ('id','name', 'type_qr', 'url')
    list_filter = ('type_qr',)
    list_editable = ('name', 'type_qr')


class AdminGallery(admin.TabularInline):

    model = GalleryCard


class AdminWebsite(admin.TabularInline):

    model = WebsiteCard


class AdminCoupinBusiness(admin.TabularInline):

    model = CouponBusiness
    extra = 1


class AdminBusiness(admin.ModelAdmin):

    inlines = [
        AdminGallery,
        AdminWebsite,
        AdminCoupinBusiness
    ]
    prepopulated_fields = {'url_name': ('name',)}


class AdminFieldInformation(admin.TabularInline):

    model = FieldMoreInformation


class AdminMoreInformation(admin.ModelAdmin):

    prepopulated_fields = {'url_name': ('name',)}
    inlines = [
        AdminFieldInformation,
    ]


class AdminImage(admin.ModelAdmin):
	list_display = ('img', 'business_card')
	list_filter = ('business_card__name',)


class AdminFieldBusiness(admin.ModelAdmin):
    list_filter = ('business_card__name',)


admin.site.register(Usuario)
admin.site.register(Code, AdminCode)
admin.site.register(Opening)
admin.site.register(CodeChanges)
admin.site.register(UrlCode)
admin.site.register(EventQRCode, AdminEvent)
admin.site.register(EventQrCodeUse)
admin.site.register(UserEventQrCode, AdminUserEvent)
admin.site.register(Image, AdminImage)
admin.site.register(BusinessCard, AdminBusiness)
admin.site.register(FieldBusiness, AdminFieldBusiness)
admin.site.register(SocialBusiness)
admin.site.register(MoreInformationCard, AdminMoreInformation)
admin.site.register(Plan)
admin.site.register(Payment)
admin.site.register(RankBusiness)
admin.site.register(OpenBusiness)
