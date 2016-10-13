from django.conf.urls import url

from arpwatch import views

urlpatterns = [
   url(r'^$', views.index, name='arp_index'),
   url(r'^import/$', views.import_files, name='arp_import'),
   url(r'^devices/$', views.device_list, name='arp_devices'),
   url(r'^device/(?P<id>[\d]+)/$', views.device, name='arp_device'),
   url(r'^device/$', views.device_logs_today, name='arp_devices_today'),
   url(r'^device/(?P<year>\d+)/(?P<month>\d+)/(?P<day>\d+)/$', views.device_logs_by_day, name='arp_device_logs'),
   url(r'^user/$', views.logins_today, name='arp_user'),
   url(r'^user/(?P<year>\d+)/(?P<month>\d+)/(?P<day>\d+)/$', views.logins_by_day, name='arp_user_logs'),
]

# Copyright 2016 Office Nomads LLC (http://www.officenomads.com/) Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0 Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
