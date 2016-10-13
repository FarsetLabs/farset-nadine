# -*- coding: utf-8 -*-
# Generated by Django 1.9.9 on 2016-08-31 17:12
from __future__ import unicode_literals, print_function

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion

#
# These 8 models use Member to map to a user and to make things easier for the
# future migration where we rename Member to UserProfile, we are crating a User
# field we can start moving over to.  --JLS
#

def member_to_user(model):
    # print(" %d objects found..." % model.objects.all().count(), end="")
    for o in model.objects.all():
        if o.member:
            o.user = o.member.user
            o.save()
        #else:
        #    print()
        #    print("      '%s' has no Member object! (pk=%s)" % (o, o.pk))
    # print()


def forwards_func(apps, schema_editor):
    # print()
    # print ("    Migrating DailyLog... ", end="")
    member_to_user(apps.get_model("nadine", "DailyLog"))
    # print ("    Migrating Membership... ", end="")
    member_to_user(apps.get_model("nadine", "Membership"))
    # print ("    Migrating SentEmailLog... ", end="")
    member_to_user(apps.get_model("nadine", "SentEmailLog"))
    # print ("    Migrating SecurityDeposit... ", end="")
    member_to_user(apps.get_model("nadine", "SecurityDeposit"))
    # print ("    Migrating SpecialDay... ", end="")
    member_to_user(apps.get_model("nadine", "SpecialDay"))
    # print ("    Migrating MemberNote... ", end="")
    member_to_user(apps.get_model("nadine", "MemberNote"))
    # print ("    Migrating Bill... ", end="")
    member_to_user(apps.get_model("nadine", "Bill"))
    # print ("    Migrating Transaction... ", end="")
    member_to_user(apps.get_model("nadine", "Transaction"))


def reverse_func(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('nadine', '0006_membershipplan_enabled'),
    ]

    operations = [
        migrations.AddField(
            model_name='bill',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='transaction',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='dailylog',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='membership',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='sentemaillog',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='specialday',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='securitydeposit',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='membernote',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='membernote',
            name='created_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to=settings.AUTH_USER_MODEL),
        ),
        migrations.RunPython(forwards_func, reverse_func),
        migrations.AlterField(
            model_name='bill',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='dailylog',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='membership',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='securitydeposit',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='specialday',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='membernote',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
