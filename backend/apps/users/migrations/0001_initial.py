import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Content',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('title', models.CharField(max_length=256)),
                ('url', models.URLField(default='', max_length=1024)),
            ],
        ),
        migrations.CreateModel(
            name='Enquete',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('title', models.CharField(max_length=128, unique=True)),
                ('description', models.TextField(blank=True, max_length=1000, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='GoogleForm',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(blank=True, default='', max_length=1024)),
                ('url', models.URLField()),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('username_entry_field', models.CharField(blank=True, default='', max_length=128)),
                ('curve_id_entry_field', models.CharField(blank=True, default='', max_length=128)),
            ],
        ),
        migrations.CreateModel(
            name='EmailUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(default='', max_length=32, unique=True)),
                ('email', models.EmailField(blank=True, max_length=256)),
                ('is_staff', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=True)),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now)),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('is_verified', models.BooleanField(blank=True, default=False, null=True)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('inviting_users', models.ManyToManyField(null=True, to=settings.AUTH_USER_MODEL)),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='YouTubeContent',
            fields=[
                ('content_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='users.content')),
                ('video_id', models.CharField(max_length=128, unique=True)),
            ],
            bases=('users.content',),
        ),
        migrations.AddField(
            model_name='content',
            name='user',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.CreateModel(
            name='Curve',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('values', models.JSONField()),
                ('version', models.CharField(max_length=16)),
                ('room_name', models.CharField(default='', max_length=32)),
                ('locked', models.BooleanField(default=True)),
                ('kind', models.IntegerField(choices=[(1, 'フリーハンド'), (2, '指定点')], default=1)),
                ('content', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='users.content')),
                ('user', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='EnqueteAnswer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('answer', models.TextField(max_length=1000)),
                ('curve', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='users.curve')),
                ('enquete', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='users.enquete')),
            ],
        ),
        migrations.AddField(
            model_name='curve',
            name='enquete',
            field=models.ManyToManyField(through='users.EnqueteAnswer', to='users.enquete'),
        ),
        migrations.CreateModel(
            name='GCPToken',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('access_token', models.TextField(default='', unique=True)),
                ('refresh_token', models.TextField(default='', unique=True)),
                ('bucket_name', models.TextField(default='', unique=True)),
                ('user', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='InvitingToken',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('token', models.TextField(default='', unique=True)),
                ('expiration_date', models.DateTimeField(blank=True)),
                ('user', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='RelationParticipant',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sended_mail', models.BooleanField(default=False)),
                ('message', models.TextField(blank=True, default='')),
                ('user', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Request',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('room_name', models.CharField(blank=True, max_length=6, null=True, unique=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('title', models.CharField(default='', max_length=128)),
                ('description', models.TextField(default='')),
                ('intervals', models.IntegerField(default=1)),
                ('is_required_free_hand', models.BooleanField(default=False)),
                ('values', models.JSONField(blank=True, default=list)),
                ('expiration_date', models.DateTimeField(auto_now_add=True)),
                ('state_processing_to_download', models.IntegerField(choices=[(0, 'WAITING'), (1, 'PROCESSING'), (2, 'SUCCESSED'), (-1, 'FAILED')], default=0)),
                ('content', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='users.content')),
                ('enquetes', models.ManyToManyField(blank=True, to='users.enquete')),
                ('google_form', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='users.googleform')),
                ('owner', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='owner', to=settings.AUTH_USER_MODEL)),
                ('participants', models.ManyToManyField(through='users.RelationParticipant', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='relationparticipant',
            name='request',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='users.request'),
        ),
        migrations.CreateModel(
            name='Section',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('title', models.CharField(default='', max_length=256)),
                ('webvtt', models.TextField(blank=True, default='')),
                ('content', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='users.content')),
                ('user', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='request',
            name='section',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='users.section'),
        ),
        migrations.CreateModel(
            name='ValueType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('title', models.CharField(default='', max_length=256)),
                ('axis_type', models.IntegerField(choices=[(1, '平常状態を含んで上と下がある値'), (2, '平常状態から上にしか上がらない値')], default=1)),
                ('user', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='request',
            name='value_type',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='users.valuetype'),
        ),
        migrations.AddField(
            model_name='curve',
            name='value_type',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='users.valuetype'),
        ),
    ]
