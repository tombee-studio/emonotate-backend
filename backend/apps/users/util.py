from django.contrib.auth.models import Group
from users.models import *

def prepare():
    for name, perms in [
        ('Guest', 
         ['view_request', 'view_content', 'view_valuetype', 
          'add_youtubecontent', 'view_youtubecontent', 
          'view_enquete',
          'view_emailuser', 'view_curve', 'add_curve', 'change_curve', 'delete_curve']),
        ('General', 
         ['view_request',       'add_request',      'change_request', 'delete_request', 
          'view_content',       'add_content',      'change_content', 'delete_content',
          'view_valuetype',     'add_valuetype',    'change_valuetype', 'delete_valuetype',
          'view_youtubecontent','add_youtubecontent', 'change_youtubecontent', 'delete_youtubecontent',
          'view_enquete',
          'view_emailuser',     'add_emailuser',    'change_emailuser', 'delete_emailuser',
          'view_curve',         'add_curve',    'change_curve', 'delete_curve']),
        ('Researchers', 
         ['view_request',       'add_request',      'change_request', 'delete_request', 
          'view_content',       'add_content',      'change_content', 'delete_content',
          'view_valuetype',     'add_valuetype',    'change_valuetype', 'delete_valuetype',
          'view_enquete', 'add_enquete', 'change_enquete', 'delete_enquete',
          'view_youtubecontent','add_youtubecontent', 'change_youtubecontent', 'delete_youtubecontent',
          'view_emailuser',     'add_emailuser',    'change_emailuser', 'delete_emailuser',
          'view_curve',         'add_curve',    'change_curve', 'delete_curve'])]:
        group, _ = Group.objects.get_or_create(name=name)
        group.permissions.add(*Permission.objects.filter(content_type__app_label='users', codename__in=perms))
