# Generated by Django 2.2.3 on 2019-08-12 16:39

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0005_user_area'),
    ]

    operations = [
        migrations.AlterField(
            model_name='image',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='user.User', verbose_name='用户ID'),
        ),
        migrations.CreateModel(
            name='UserRelation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('follower_id', models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, related_name='sample2', to='user.User', verbose_name='被关注者用户ID')),
                ('user_id', models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, related_name='sample1', to='user.User', verbose_name='用户ID')),
            ],
        ),
    ]
