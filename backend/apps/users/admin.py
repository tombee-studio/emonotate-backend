from django.contrib import admin

from .models import *


class RequestInline(admin.TabularInline):
    model = RelationParticipant


class EmailUserInline(admin.TabularInline):
    model = RelationParticipant


class RequestAdmin(admin.ModelAdmin):
    inlines = [EmailUserInline]


class EmailUserAdmin(admin.ModelAdmin):
    inlines = [RequestInline]


admin.site.register(Content)
admin.site.register(EmailUser, EmailUserAdmin)
admin.site.register(ValueType)
admin.site.register(Curve)
admin.site.register(YouTubeContent)
admin.site.register(Request, RequestAdmin)
admin.site.register(Questionaire)
