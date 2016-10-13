from django.conf.urls import url

from interlink import views

urlpatterns = [
    url(r'^messages/(?P<list_id>[^/]+)/$', views.list_messages, name='interlink_messages'),
    url(r'^subscribers/(?P<list_id>[^/]+)/$', views.list_subscribers, name='interlink_subscribers'),
    url(r'^unsubscribe/(?P<list_id>[^/]+)/(?P<username>[^/]+)$', views.unsubscribe, name='interlink_unsubscribe'),
    url(r'^subscribe/(?P<list_id>[^/]+)/(?P<username>[^/]+)$', views.subscribe, name='interlink_subscribe'),
    url(r'^moderate/$', views.moderator_list, name='interlink_moderate'),
    url(r'^moderate/(?P<id>[\d]+)/$', views.moderator_inspect, name='interlink_inspect'),
    url(r'^moderate/(?P<id>[\d]+)/approve/$', views.moderator_approve, name='interlink_approve'),
    url(r'^moderate/(?P<id>[\d]+)/reject/$', views.moderator_reject, name='interlink_reject'),
    url(r'^$', views.index, name='interlink_index'),
]

# Copyright 2016 Office Nomads LLC (http://www.officenomads.com/) Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0 Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
