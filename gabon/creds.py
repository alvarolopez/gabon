# Copyright 2017 Alvaro Lopez Garcia
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import os.path

import oauth2client.client
import oauth2client.file
import oauth2client.tools
from oslo_config import cfg

from gabon import exception

opts = [
    cfg.StrOpt('client_id',
               default=None,
               help='Client ID to be used when requesting authentication '
                    'instead of the default one. Note that you do not need '
                    'to specify one, unless you are sure about what you are '
                    'doing. If you set this value you would need to specify '
                    'the client_secret as well.'),
    cfg.StrOpt('client_secret',
               default=None,
               help='Client secret to be used when requesting authentication '
                    'instead of the default one. Note that you do not need '
                    'to specify one, unless you are sure about what you are '
                    'doing. If you set this value you would need to specify '
                    'the client_id as well.'),
    # TODO(aloga): we need to handle directories and files in a smarter way. we
    # need to crete directories if they do not exist, if permissions are wrong,
    # etc.
    cfg.StrOpt('client_credentials_store',
               default='~/.gabon/client_auth.json',
               help='Path where client credentials are stored.')
]


CONF = cfg.CONF
CONF.register_opts(opts)

_SCOPE = ['https://www.googleapis.com/auth/contacts.readonly']
_API_CLIENT_ID = ("760477478139-urpn11m4js4su1q43o18jmmdgmegdsq2."
                  "apps.googleusercontent.com")
_API_CLIENT_SECRET = "tuoZmkdIkfXcvYevAJqu33g5"


def get_credentials(args=None):
    store_file = os.path.expanduser(CONF.client_credentials_store)
    store = oauth2client.file.Storage(store_file)

    creds = store.get()

    if creds is None or creds.invalid:
        client_id = CONF.client_id or _API_CLIENT_ID
        client_secret = CONF.client_secret or _API_CLIENT_SECRET
        if not client_id and client_secret:
            raise exception.InvalidConfiguration(
                reason="You need to specify both client_id AND client_secret"
            )

        # TODO(aloga): put a user agent here
        flow = oauth2client.client.OAuth2WebServerFlow(
            client_id=client_id,
            client_secret=client_secret,
            scope=_SCOPE
        )
        creds = oauth2client.tools.run_flow(flow, store, args)

    return creds
