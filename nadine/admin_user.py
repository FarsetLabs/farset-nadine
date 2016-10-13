from django.contrib import admin
from django import forms
from django.forms.utils import ErrorList
from django.contrib.auth.models import User, Group
from django.contrib.auth.admin import UserAdmin

from nadine.models import *


admin.site.register(URLType)


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    max_num = 1


class URLInline(admin.TabularInline):
    model = URL
    extra = 1


class EmailAddressInline(admin.TabularInline):
    model = EmailAddress
    fields=['id', 'is_primary', 'email', 'verified_ts',]
    readonly_fields=['id', 'is_primary', 'verified_ts', ]
    extra = 0


class EmergencyContactInline(admin.StackedInline):
    model = EmergencyContact
    can_delete = False
    max_num = 1


class XeroContactInline(admin.TabularInline):
    model = XeroContact
    readonly_fields=['last_sync', ]
    can_delete = False
    max_num = 1


class UserWithProfileAdmin(UserAdmin):

    def membership(self):
        active_membership = self.profile.active_membership()
        if active_membership:
            return active_membership.membership_plan
        return ""

    inlines = [EmailAddressInline, UserProfileInline, URLInline, EmergencyContactInline, XeroContactInline]
    list_display = ('username', 'email', membership, 'date_joined', 'last_login')
    ordering = ('-date_joined', 'username')
    search_fields = ('username', 'first_name', 'last_name', 'emailaddress__email')
    readonly_fields = ('last_login', 'date_joined')
    fieldsets = (
        (None, {'fields': ('username', 'first_name', 'last_name',
            'is_active', 'is_staff', 'is_superuser', 'last_login', 'date_joined', 'password')}),
    )


# Hook it all up
admin.site.unregister(User)
admin.site.register(User, UserWithProfileAdmin)
admin.site.unregister(Group)

# Copyright 2016 Office Nomads LLC (http://www.officenomads.com/) Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0 Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
