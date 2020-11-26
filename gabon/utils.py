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

    print(result)


def print_dict(d, dict_property="Property", dict_value="Value"):
    pt = prettytable.PrettyTable([dict_property, dict_value], caching=False)
    pt.align = 'l'
    for k, v in sorted(d.items()):
        # if value has a newline, add in multiple rows
        # e.g. fault with stacktrace
        if v and isinstance(v, six.string_types) and (r'\n' in v or '\r' in v):
            # '\r' would break the table, so remove it.
            if '\r' in v:
                v = v.replace('\r', '')
            lines = v.strip().split(r'\n')
            col1 = k
            for line in lines:
                pt.add_row([col1, line])
                col1 = ''
        else:
            if v is None:
                v = '-'
            pt.add_row([k, v])

    result = pt.get_string()

    print(result)
