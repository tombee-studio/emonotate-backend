from django.db import migrations


def set_owners(apps, schema_editor):
    """A form belongs to the owner of the first request that uses it."""
    GoogleForm = apps.get_model('users', 'GoogleForm')
    Request = apps.get_model('users', 'Request')
    for pk, owner in (Request.objects.filter(google_form__isnull=False).order_by('-pk')
                      .values_list('google_form', 'owner')):
        GoogleForm.objects.filter(pk=pk).update(user=owner)


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_googleform_user'),
    ]

    operations = [
        migrations.RunPython(set_owners, migrations.RunPython.noop),
    ]
