from django.contrib import admin

from .models import *


class RequestInline(admin.TabularInline):
    model = RelationParticipant
    extra = 0


class EmailUserInline(admin.TabularInline):
    model = RelationParticipant
    extra = 0


class CurveInline(admin.TabularInline):
    model = EnqueteAnswer
    extra = 0


class EnqueteInline(admin.TabularInline):
    model = EnqueteAnswer
    extra = 0


class RequestAdmin(admin.ModelAdmin):
    inlines = [EmailUserInline]


class EmailUserAdmin(admin.ModelAdmin):
    inlines = [RequestInline]


class CurveAdmin(admin.ModelAdmin):
    inlines = [EnqueteInline]


class EnqueteAdmin(admin.ModelAdmin):
    inlines = [CurveInline]


admin.site.register(Content)
admin.site.register(EmailUser, EmailUserAdmin)
admin.site.register(ValueType)
admin.site.register(Curve, CurveAdmin)
admin.site.register(Enquete, EnqueteAdmin)
admin.site.register(YouTubeContent)
admin.site.register(Request, RequestAdmin)
