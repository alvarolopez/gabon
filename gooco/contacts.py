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

import httplib2

from apiclient import discovery

from gooco import creds


class Contact(object):
    def __init__(self, person_id, name, email):
        person_id = person_id.replace("people/", "")
        self.person_id = person_id
        self.name = name
        self.email = email


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

    def list_contacts(self, sort_order="FIRST_NAME_ASCENDING"):
        l = []
        next_page = None
        while True:
            c = self.api.people().connections().list(
                resourceName='people/me',
                sortOrder=sort_order,
                requestMask_includeField='person.names,person.email_addresses',
                pageSize=100,
                pageToken=next_page,
            ).execute()
            for x in c["connections"]:
                get_primary = lambda x: x["metadata"].get("primary")
                name = filter(get_primary, x["names"])[0]["displayName"]
                email = filter(get_primary, x["emailAddresses"])[0]["value"]
                person_id = x["resourceName"]
                l.append(Contact(person_id, name, email))
            next_page = c.get("nextPageToken", None)
            if next_page is None:
                break
        return l


API = ContactsAPI()
