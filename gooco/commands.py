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

from __future__ import print_function

import abc
import sys

import oauth2client.tools
from oslo_config import cfg
import six

from gooco import contacts
from gooco import creds
from gooco import exception
from gooco import interface
from gooco import utils


def add_command_parsers(subparsers):
    AuthenticateCommand(subparsers)
    ListCommand(subparsers)
    GetCommand(subparsers)
    InterfaceCommand(subparsers)


command_opt = cfg.SubCommandOpt('command',
                                title='Commands',
                                help='Show available commands.',
                                handler=add_command_parsers)

CONF = cfg.CONF
CONF.register_cli_opt(command_opt)


@six.add_metaclass(abc.ABCMeta)
class Command(object):
    def __init__(self, parser, name, cmd_help, parents=[]):
        self.name = name
        self.cmd_help = cmd_help
        self.parser = parser.add_parser(name, help=cmd_help, parents=parents)
        self.parser.set_defaults(func=self.run)

    @abc.abstractmethod
    def run(self):
        raise NotImplementedError("Method must be overridden on subclass")


class AuthenticateCommand(Command):
    def __init__(self, parser, name="authenticate",
                 cmd_help="Authenticate using Google OAuth2"):
        super(AuthenticateCommand, self).__init__(
            parser,
            name,
            cmd_help,
            parents=[oauth2client.tools.argparser]
        )

    def run(self):
        args = oauth2client.tools.argparser.parse_known_args(sys.argv)[0]
        c = creds.get_credentials(args)
        if c.invalid:
            print("Authentication was NOT successful")
        else:
            print("Authentication was successful")


class InterfaceCommand(Command):
    def __init__(self, parser, name="curses",
                 cmd_help="Start curses interface"):
        super(InterfaceCommand, self).__init__(parser, name, cmd_help)

    def run(self):
        interface.Interface()


class GetCommand(Command):
    def __init__(self, parser, name="get",
                 cmd_help="Get info from contact"):
        super(GetCommand, self).__init__(parser, name, cmd_help)
        self.parser.add_argument("person_id",
                                 help="Person ID to retrieve.")

    def run(self):
        person_id = CONF.command.person_id
        c = contacts.API.get_contact(person_id)
        utils.print_dict(c.to_dict())


class ListCommand(Command):
    def __init__(self, parser, name="list",
                 cmd_help="List all contacts"):
        super(ListCommand, self).__init__(parser, name, cmd_help)

    def run(self):
        c = contacts.API.list_contacts()
        fields = ["Person ID", "Name", "Email"]
        utils.print_list(c, fields)


class CommandManager(object):
    def execute(self):
        try:
            CONF.command.func()
        except exception.GoocoException as e:
            print("ERROR: %s" % e, file=sys.stderr)
            sys.exit(1)
        except KeyboardInterrupt:
            print("\nExiting...", file=sys.stderr)
            sys.exit(0)
