# Generated by Django 2.2.3 on 2019-08-29 15:25

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='topic',
            name='topic_join',
            field=models.ManyToManyField(default='', related_name='sample8', to='user.User', verbose_name='话题参与者'),
        ),
        migrations.AlterField(
            model_name='topic',
            name='topic_user',
            field=models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, related_name='sample7', to='user.User', verbose_name='话题发布人'),
        ),
    ]
