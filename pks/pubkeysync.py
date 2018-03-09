from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend

import logging
import os
import yaml

from .objects.category import Category
from .objects.group import Group
from .objects.user import User
from .objects.server import Server

class PubKeySync:
    def __init__(self, **kwargs):
        logging.basicConfig(filename='logs/pubkeysync.log', level=logging.INFO, format='%(asctime).19s | %(levelname)s | %(message)s')
        self._log = logging.getLogger("pks")
        self.printlog('-----PubKeySync Started-----')
        self.printlog('Loading configuration...')
        self.config()

    def config(self):
        # Catch this cleanly and output messages if config files are invalid.
        try:
            with open('config/pubkeysync.yaml', 'r') as f:
                config = yaml.load(f.read())

            self.private_key_file = config['private_key']
            self.public_key_file = config['public_key']

            # Add Groups
            self.groups = []
            for group_dict in config['groups']:
                if isinstance(group_dict, str):
                    group_dict = {group_dict: {}}
                group = Group(self, group_dict)
                self.groups.append(group)

            # Add Users
            self.users = []
            for user_dict in config['users']:
                if isinstance(user_dict, str):
                    user_dict = {user_dict: {}}
                user = User(self, user_dict)
                self.users.append(user)

            # Add Categories
            self.categories = []
            for category_dict in config['categories']:
                if isinstance(category_dict, str):
                    category_dict = {category_dict: {}}
                category = Category(self, category_dict)
                self.categories.append(category)

            # Add Servers
            self.servers = []
            for server_dict in config['servers']:
                server = Server(self, server_dict)
                self.servers.append(server)

            self.load_agent_keys()
        except Exception as e:
            print('Load Failed: {}'.format(e))
            self.log_error('Load Failed: {}'.format(e))
            exit()

    def printlog(self, msg):
        print(msg)
        self.log(msg)

    def log(self, msg):
        self._log.info(msg)

    def log_error(self, msg):
        self._log.error(msg)

    def load_agent_keys(self):
        try:
            if not os.path.isfile('keys/{}'.format(self.private_key_file)) and not os.path.isfile('keys/{}'.format(self.public_key_file)):
                print('Agent key-pair does not exist. Creating...')
                # generate new keypair if files don't exist

                key = rsa.generate_private_key(backend=default_backend(), public_exponent=65537, key_size=2048)

                # get public key in OpenSSH format
                _public_key = key.public_key().public_bytes(serialization.Encoding.OpenSSH, \
                    serialization.PublicFormat.OpenSSH)

                # get private key in PEM container format
                pem = key.private_bytes(encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.TraditionalOpenSSL,
                    encryption_algorithm=serialization.NoEncryption())

                with open('keys/{}'.format(self.private_key_file), 'wb') as f:
                    f.write(pem)
                # Set owner-only permissions
                os.chmod('keys/{}'.format(self.private_key_file), 0o600)

                self.public_key = _public_key.decode('utf-8') + ' pubkeysync-agent'
                with open('keys/{}'.format(self.public_key_file), 'w') as f:
                    f.write(self.public_key)
                return self.public_key
            else:
                if not os.path.isfile('keys/{}'.format(self.private_key_file)):
                    raise Exception
                with open('keys/{}'.format(self.public_key_file), 'r') as f:
                    self.public_key = f.read()
                return self.public_key
        except Exception:
            raise Exception('Unable to load key file for PKS agent')

    def push_keys(self, verbose=False):
        category_servers = []
        for category in self.categories:
            category_servers.extend(category.get_new_servers())

        all_servers = list(set(self.servers + category_servers))
        for server in all_servers:
            server.update_authorized_keys(verbose)
