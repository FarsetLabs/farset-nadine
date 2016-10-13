import os
import time
import urllib
import sys
import datetime

from django.conf import settings
from django.core.management.base import NoArgsCommand, CommandError

from arpwatch import arp

class Command(NoArgsCommand):
    help = "Import new arplogs"

    requires_system_checks = True

    def handle_noargs(self, **options):
        arp.import_all()
        arp.map_ip_to_mac(1)


# Copyright 2010 Office Nomads LLC (http://officenomads.com/) Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0 Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
