import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_googleform_owners'),
    ]

    operations = [
        migrations.AddField(
            model_name='request',
            name='starts_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='request',
            name='ends_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='request',
            name='max_submissions',
            field=models.PositiveIntegerField(blank=True, null=True,
                                              validators=[django.core.validators.MinValueValidator(1)]),
        ),
    ]
