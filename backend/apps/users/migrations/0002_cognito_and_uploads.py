import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='UploadedSource',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key', models.CharField(max_length=1024, unique=True)),
                ('mime_type', models.CharField(max_length=64)),
                ('content', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='upload', to='users.content')),
            ],
        ),
        migrations.CreateModel(
            name='CognitoIdentity',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pool_id', models.CharField(max_length=128)),
                ('subject', models.UUIDField()),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('pool_id', 'subject')},
            },
        ),
    ]
