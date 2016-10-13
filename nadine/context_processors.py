from django.conf import settings
from django.contrib.sites.models import Site
from staff.forms import MemberSearchForm
from members.models import HelpText


def site(request):
    site = Site.objects.get_current()
    return {'site': site}


def nav_context(request):
    site_search_form = MemberSearchForm()
    return {'site_search_form': site_search_form}


def tablet_context(request):
    try:
        return {'tablet_ios': settings.TABLET.lower() == 'ios'}
    except AttributeError:
        return {'tablet_ios': False}

def allow_online_registration(request):
    return {'ALLOW_ONLINE_REGISTRATION': settings.ALLOW_ONLINE_REGISTRATION}

# Copyright 2014 Office Nomads LLC (http://www.officenomads.com/) Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0 Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
