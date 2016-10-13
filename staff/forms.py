from django import forms
from django.contrib.auth.models import User
from django.utils.html import strip_tags
from django.utils import timezone
from taggit.forms import *

from nadine.models import *
from nadine.utils.payment_api import PaymentAPI
from nadine import email

import datetime
import logging

logger = logging.getLogger(__name__)


class DateRangeForm(forms.Form):
    start = forms.DateField()
    end = forms.DateField()


class PayBillsForm(forms.Form):
    username = forms.CharField(required=True, widget=forms.HiddenInput)
    amount = forms.DecimalField(min_value=0, max_value=10000, required=True, max_digits=7, decimal_places=2)
    transaction_note = forms.CharField(required=False, widget=forms.Textarea)


class RunBillingForm(forms.Form):
    run_billing = forms.BooleanField(required=True, widget=forms.HiddenInput)


class NewUserForm(forms.Form):
    first_name = forms.CharField(max_length=100, label="First name *", required=True, widget=forms.TextInput(attrs={'autocapitalize': "words"}))
    last_name = forms.CharField(max_length=100, label="Last name *", required=True, widget=forms.TextInput(attrs={'autocapitalize': "words"}))
    email = forms.EmailField(max_length=100, label="Email *", required=True)

    def clean_first_name(self):
        return self.cleaned_data['first_name'].strip().title()

    def clean_last_name(self):
        return self.cleaned_data['last_name'].strip().title()

    def clean_email(self):
        email = self.cleaned_data['email'].strip().lower()
        if User.objects.filter(email=email).count() > 0:
            raise forms.ValidationError("Email address '%s' already in use." % email)
        return email

    def create_username(self, suffix=""):
        clean_first = self.cleaned_data['first_name'].strip().lower()
        clean_last = self.cleaned_data['last_name'].strip().lower()
        username = "%s_%s%s" % (clean_first, clean_last, suffix)
        clean_username = username.replace(" ", "_")
        clean_username = clean_username.replace(".", "_")
        clean_username = clean_username.replace("-", "_")
        clean_username = clean_username.replace("@", "")
        clean_username = clean_username.replace("+", "")
        return clean_username

    def save(self):
        "Creates the User and Profile records with the field data and returns the user"
        if not self.is_valid():
            raise Exception('The form must be valid in order to save')

        # Generate a unique username
        tries = 1
        username = self.create_username()
        while User.objects.filter(username=username).count() > 0:
            tries = tries + 1
            username = self.create_username(suffix=tries)

        first = self.cleaned_data['first_name']
        last = self.cleaned_data['last_name']
        email = self.cleaned_data['email']

        user = User(username=username, first_name=first, last_name=last, email=email)
        password = User.objects.make_random_password(length=32)
        user.set_password(password)
        user.save()

        return user

    class Meta:
        widgets = {
            'first_name': forms.TextInput(attrs={'autocapitalize': 'on', 'autocorrect': 'off'}),
            'last_name': forms.TextInput(attrs={'autocapitalize': 'on', 'autocorrect': 'off'}),
        }


class MemberSearchForm(forms.Form):
    terms = forms.CharField(max_length=100)


class MemberEditForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={'readonly':'readonly'}))
    first_name = forms.CharField(widget=forms.TextInput(attrs={'size': '50'}))
    last_name = forms.CharField(widget=forms.TextInput(attrs={'size': '50'}))
    email = forms.EmailField(widget=forms.TextInput(attrs={'size': '50'}))
    email2 = forms.EmailField(widget=forms.TextInput(attrs={'size': '50'}), required=False)
    phone = forms.CharField(widget=forms.TextInput(attrs={'size': '16'}), required=False)
    phone2 = forms.CharField(widget=forms.TextInput(attrs={'size': '16'}), required=False)
    address1 = forms.CharField(widget=forms.TextInput(attrs={'size': '50'}), required=False)
    address2 = forms.CharField(widget=forms.TextInput(attrs={'size': '50'}), required=False)
    city = forms.CharField(widget=forms.TextInput(attrs={'size': '20'}), required=False)
    state = forms.CharField(widget=forms.TextInput(attrs={'size': '5'}), required=False)
    zipcode = forms.CharField(widget=forms.TextInput(attrs={'size': '10'}), required=False)
    company_name = forms.CharField(widget=forms.TextInput(attrs={'size': '50'}), required=False)
    url_personal = forms.URLField(widget=forms.TextInput(attrs={'size': '50'}), required=False)
    url_professional = forms.URLField(widget=forms.TextInput(attrs={'size': '50'}), required=False)
    url_facebook = forms.URLField(widget=forms.TextInput(attrs={'size': '50'}), required=False)
    url_twitter = forms.URLField(widget=forms.TextInput(attrs={'size': '50'}), required=False)
    url_linkedin = forms.URLField(widget=forms.TextInput(attrs={'size': '50'}), required=False)
    url_github = forms.URLField(widget=forms.TextInput(attrs={'size': '50'}), required=False)
    gender = forms.ChoiceField(choices=GENDER_CHOICES, required=False)
    howHeard = forms.ModelChoiceField(label="How heard", queryset=HowHeard.objects.all(), required=False)
    industry = forms.ModelChoiceField(queryset=Industry.objects.all(), required=False)
    neighborhood = forms.ModelChoiceField(queryset=Neighborhood.objects.all(), required=False)
    has_kids = forms.NullBooleanField(required=False)
    self_employed = forms.NullBooleanField(required=False)
    photo = forms.ImageField(required=False)

    emergency_name = forms.CharField(widget=forms.TextInput(attrs={'size': '50'}), label="Emergency Contact", required=False)
    emergency_relationship = forms.CharField(widget=forms.TextInput(attrs={'size': '50'}), label="Relationship", required=False)
    emergency_phone = forms.CharField(widget=forms.TextInput(attrs={'size': '16'}), label="Phone", required=False)
    emergency_email = forms.EmailField(widget=forms.TextInput(attrs={'size': '50'}), label="E-mail", required=False)

    def save(self):
        "Creates the User and Profile records with the field data and returns the user"
        if not self.is_valid():
            raise Exception('The form must be valid in order to save')

        user = User.objects.get(username=self.cleaned_data['username'])
        user.first_name=self.cleaned_data['first_name']
        user.last_name=self.cleaned_data['last_name']
        user.email=self.cleaned_data['email']
        user.save()

        # Alternate Emails
        email2 = self.cleaned_data['email2']
        if email2 and not email2 in user.profile.all_emails():
            e2 = EmailAddress(user=user, email=email2)
            e2.save()

        # Save profile fields
        user.profile.phone = self.cleaned_data['phone']
        user.profile.phone2 = self.cleaned_data['phone2']
        user.profile.address1 = self.cleaned_data['address1']
        user.profile.address2 = self.cleaned_data['address2']
        user.profile.city = self.cleaned_data['city']
        user.profile.state = self.cleaned_data['state']
        user.profile.zipcode = self.cleaned_data['zipcode']
        user.profile.gender = self.cleaned_data['gender']
        user.profile.howHeard = self.cleaned_data['howHeard']
        user.profile.industry = self.cleaned_data['industry']
        user.profile.neighborhood = self.cleaned_data['neighborhood']
        user.profile.has_kids = self.cleaned_data['has_kids']
        user.profile.self_emplyed = self.cleaned_data['self_employed']
        user.profile.company_name = self.cleaned_data['company_name']
        if self.cleaned_data['photo']:
            user.profile.photo = self.cleaned_data['photo']
        user.profile.save()

        # Save the URLs
        user.profile.save_url("personal", self.cleaned_data['url_personal'])
        user.profile.save_url("professional", self.cleaned_data['url_professional'])
        user.profile.save_url("facebook", self.cleaned_data['url_facebook'])
        user.profile.save_url("twitter", self.cleaned_data['url_twitter'])
        user.profile.save_url("linkedin", self.cleaned_data['url_linkedin'])
        user.profile.save_url("github", self.cleaned_data['url_github'])

        emergency_contact = user.get_emergency_contact()
        emergency_contact.name=self.cleaned_data['emergency_name']
        emergency_contact.relationship=self.cleaned_data['emergency_relationship']
        emergency_contact.phone=self.cleaned_data['emergency_phone']
        emergency_contact.email=self.cleaned_data['emergency_email']
        emergency_contact.save()

class CoworkingDayForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={'readonly':'readonly'}))
    visit_date = forms.DateField(widget=forms.HiddenInput())
    payment = forms.ChoiceField(choices=PAYMENT_CHOICES, required=True)
    note = forms.CharField(required=False)

    def save(self):
        "Creates the Daily Log to track member activity"
        if not self.is_valid():
            raise Exception('The form must be valid in order to save')

        # Make sure there isn't another log for this member on this day
        u = User.objects.get(username=self.cleaned_data['username'])
        v = self.cleaned_data['visit_date']
        if CoworkingDay.objects.filter(user=u, visit_date=v).count() > 0:
            raise Exception('Member already signed in')

        day = CoworkingDay()
        day.user = u
        day.visit_date = v
        day.payment = self.cleaned_data['payment']
        day.note = self.cleaned_data['note']
        day.save()
        return day


class MembershipForm(forms.Form):
    username = forms.CharField(required=True, widget=forms.HiddenInput)
    plan_list = MembershipPlan.objects.filter(enabled=True).order_by('name')
    membership_id = forms.IntegerField(required=False, min_value=0, widget=forms.HiddenInput)
    membership_plan = forms.ModelChoiceField(queryset=plan_list, required=True)
    start_date = forms.DateField(initial=datetime.date.today)
    end_date = forms.DateField(required=False)
    monthly_rate = forms.IntegerField(required=True, min_value=0)
    dropin_allowance = forms.IntegerField(required=True, min_value=0)
    daily_rate = forms.IntegerField(required=True, min_value=0)
    has_desk = forms.BooleanField(initial=False, required=False)
    has_key = forms.BooleanField(initial=False, required=False)
    has_mail = forms.BooleanField(initial=False, required=False)
    paid_by = forms.ModelChoiceField(queryset=User.helper.active_members(), required=False)
    # These are for the MemberNote
    note = forms.CharField(required=False, widget=forms.Textarea)
    created_by = None

    def save(self):
        if not self.is_valid():
            raise Exception('The form must be valid in order to save')
        membership_id = self.cleaned_data['membership_id']

        adding = False
        membership = None
        if membership_id:
            # Editing
            membership = Membership.objects.get(id=membership_id)
        else:
            # Adding
            adding = True
            membership = Membership()

        username = self.cleaned_data['username']
        membership.user = User.objects.get(username=username)
        membership.member = membership.user.profile

        # Any change triggers disabling of the automatic billing
        try:
            api = PaymentAPI()
            api.disable_recurring(username)
            logger.debug("Automatic Billing Disabled for '%s'" % username)
        except Exception as e:
            logger.error(e)

        # We need to look at their last membership but we'll wait until after the save
        last_membership = membership.user.profile.last_membership()

        # Save this membership
        membership.membership_plan = self.cleaned_data['membership_plan']
        membership.start_date = self.cleaned_data['start_date']
        membership.end_date = self.cleaned_data['end_date']
        membership.monthly_rate = self.cleaned_data['monthly_rate']
        membership.dropin_allowance = self.cleaned_data['dropin_allowance']
        membership.daily_rate = self.cleaned_data['daily_rate']
        membership.has_desk = self.cleaned_data['has_desk']
        membership.has_key = self.cleaned_data['has_key']
        membership.has_mail = self.cleaned_data['has_mail']
        membership.paid_by = self.cleaned_data['paid_by']
        membership.save()

        # Save the note if we were given one
        note = self.cleaned_data['note']
        if note:
            MemberNote.objects.create(user=membership.user, created_by=self.created_by, note=note)

        if adding:
            email.send_new_membership(membership.user)

        return membership

class EventForm(forms.Form):
    user = forms.ModelChoiceField(widget=forms.Select(attrs={'class': 'browser-default'}), queryset=User.objects.order_by('first_name'))
    room = forms.ModelChoiceField(widget=forms.Select(attrs={'class': 'browser-default'}), queryset=Room.objects.all(), required=False)
    start_time = forms.DateTimeField(widget=forms.DateTimeInput(attrs={'placeholder':'e.g. 12/28/16 14:30'}, format='%m/%d/%Y %H:%M'), required=True)
    end_time = forms.DateTimeField(widget=forms.DateTimeInput(attrs={'placeholder':'e.g. 12/28/16 16:30'}, format='%m/%d/%Y %H:%M:%S'), required=True)
    description = forms.CharField(max_length=100, required=False)
    charge = forms.DecimalField(decimal_places=2, max_digits=9, required=True)
    publicly_viewable = forms.ChoiceField(widget=forms.Select(attrs={'class': 'browser-default'}), choices=((True, 'Yes'), (False, 'No')), required=False)

    def save(self):
        if not self.is_valid():
            raise Exception('The form must be valid in order to save')

        user = self.cleaned_data['user']
        room = self.cleaned_data['room']
        start_ts = self.cleaned_data['start_time']
        end_ts = self.cleaned_data['end_time']
        description = self.cleaned_data['description']
        charge = self.cleaned_data['charge']
        is_public = self.cleaned_data['publicly_viewable']

        event = Event(user=user, room=room, start_ts=start_ts, end_ts=end_ts, description=description, charge=charge, is_public=is_public)

        event.save()

        return event

# Copyright 2016 Office Nomads LLC (http://www.officenomads.com/) Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0 Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
