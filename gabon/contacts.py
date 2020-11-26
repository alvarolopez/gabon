# Copyright 2017 Alvaro Lopez Garcia
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import copy
import httplib2

from apiclient import discovery
import six

from gabon import creds


class Contact(object):
    def __init__(self, person_id, info):
        self.person_id = person_id

        self._info = {}
        self._raw_data = info
        self._loaded = False

        self._add_details(self._raw_data)

    def _add_details(self, raw):
        names = raw.get("names", [])
        emails = raw.get("emailAddresses", [])

        get_primary = lambda x: x["metadata"].get("primary")

        name = email = ""
        if names:
            name = list(filter(get_primary, names))[0]["displayName"]
        if emails:
            email = list(filter(get_primary, emails))[0]["value"]

        nicknames = raw.get("nicknames", [])

        self._info["name"] = name
        self._info["email"] = email
        self._info["nicknames"] = nicknames

        for (k, v) in six.iteritems(self._info):
            try:
                setattr(self, k, v)
                self._info[k] = v
            except AttributeError:
                # In this case we already defined the attribute on the class
                pass

    def __getattr__(self, k):
        if k not in self.__dict__:
            raise AttributeError(k)
        else:
            return self.__dict__[k]

    def is_loaded(self):
        return self._loaded

    def set_loaded(self, val):
        self._loaded = val

    def to_dict(self):
        return copy.deepcopy(self._info)


class ContactsAPI(object):
    def __init__(self):
        self._people_service = None

    @property
    def api(self):
        discover_url = 'https://people.googleapis.com/$discovery/rest'
        if self._people_service is None:
            http = httplib2.Http()
            credentials = creds.get_credentials()
            http = credentials.authorize(http)

            self._people_service = discovery.build(
                serviceName='people',
                version='v1',
                http=http,
                discoveryServiceUrl=discover_url
            )
        return self._people_service

    def get_contact(self, contact_id):
        fields = 'names,email_addresses,nicknames'
        info = self.api.people().get(resourceName=contact_id,
                                     personFields=fields).execute()
        c = Contact(contact_id, info)
        return c

    def list_contacts(self, sort_order="FIRST_NAME_ASCENDING"):
        l = []
        next_page = None
        while True:
            c = self.api.people().connections().list(
                resourceName='people/me',
                sortOrder=sort_order,
                personFields='names,email_addresses',
                pageSize=100,
                pageToken=next_page,
            ).execute()
            for x in c["connections"]:
                info = x
                person_id = x["resourceName"]
                l.append(Contact(person_id, info=info))
            next_page = c.get("nextPageToken", None)
            if next_page is None:
                break
        return l


API = ContactsAPI()
