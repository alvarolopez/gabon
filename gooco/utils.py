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

import prettytable
import six


def print_list(objs, fields, formatters={}, sortby_index=None):
    if sortby_index is None:
        sortby = None
    else:
        sortby = fields[sortby_index]
    pt = prettytable.PrettyTable([f for f in fields], caching=False)
    pt.align = 'l'

    for o in objs:
        row = []
        for field in fields:
            if field in formatters:
                row.append(formatters[field](o))
            else:
                field_name = field.lower().replace(' ', '_')
                data = getattr(o, field_name, '')
                if data is None:
                    data = '-'
                # '\r' would break the table, so remove it.
                data = six.text_type(data).replace("\r", "")
                row.append(data)
        pt.add_row(row)

    if sortby is not None:
        result = pt.get_string(sortby=sortby)
    else:
        result = pt.get_string()

    if six.PY3:
        result = result.decode()

    print(result)
