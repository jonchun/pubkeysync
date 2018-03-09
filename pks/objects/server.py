from subprocess import Popen, PIPE, TimeoutExpired

class Server:
    def __init__(self, agent, server_dict):
        self.agent = agent
        self.label, server_config = server_dict.popitem()
        self.host = server_config.get('host', None)
        if self.host is None:
            raise Exception('Invalid Host for server {}'.format(self.label))
        self.ssh_user = server_config.get('ssh_user', 'root')
        self.ssh_port = server_config.get('ssh_port', '22')
        self.authorized_keys_file = server_config.get('authorized_keys_file', '~/.ssh/authorized_keys')
        self.timeout = int(server_config.get('timeout', 5))
        self.groups = server_config.get('groups', [])
        self.users = server_config.get('users', [])
        self.categories = server_config.get('categories', [])

    def __repr__(self):
        return '<Server {} ({}@{}:{})>'.format(self.label, self.ssh_user, self.host, self.ssh_port)

    def get_groups(self):
        groups = []
        for group_label in self.groups:
            group = next((g for g in self.agent.groups if g.label == group_label), None)
            if group is None:
                raise Exception('Invalid Group: {}'.format(group_label))
            groups.append(group)
        return groups

    def get_users(self):
        users = []
        for user_label in self.users:
            user = next((u for u in self.agent.users if u.label == user_label), None)
            if user is None:
                raise Exception('Invalid User: {}'.format(user_label))
            users.append(user)
        return users

    def get_group_users(self):
        group_users = []
        for group in self.get_groups():
            group_users.extend(group.get_users())
        return group_users

    def get_all_users(self):
        group_users = self.get_group_users()
        users = self.get_users()

        # Remove duplicates
        all_users = list(set(group_users + users))
        return all_users

    def generate_authorized_keys(self):
        # Add agent key first.
        authorized_keys = self.agent.public_key

        # Loop through all users and add their keys
        all_users = self.get_all_users()
        if all_users == []:
            return ""

        for user in all_users:
            authorized_keys += '\n{}'.format(user.key)

        return authorized_keys

    def update_authorized_keys(self, verbose=False):
        ssh_process = Popen(['ssh',
                    '{}@{}'.format(self.ssh_user, self.host),
                    '-p', self.ssh_port,
                    '-q',
                    '-i', 'keys/{}'.format(self.agent.private_key_file)],
                    stdin=PIPE,
                    stdout=PIPE,
                    stderr=PIPE,
                    encoding='utf-8',
                    bufsize=1
                )
        try:
            authorized_keys = self.generate_authorized_keys().replace('"', '\\"')
            if authorized_keys == "":
                return False
            ssh_process.stdin.write('echo > {} "{}"\n'.format(self.authorized_keys_file, authorized_keys))
            ssh_process.stdin.write('exit\n')
            ssh_process.wait(timeout=self.timeout)
            if ssh_process.returncode != 0:
                raise Exception('SSH Connection Failed')
        except TimeoutExpired:
            error_msg = '{}: Connection timed out'.format(self)
            if(verbose):
                print('WARNING | ' + error_msg)
            self.agent.log_error(error_msg)
            return False
        except Exception as e:
            error_msg = '{}: {}'.format(self, e)
            self.agent.log_error(error_msg)
            if(verbose):
                print('WARNING | ' + error_msg)
            return False
        self.agent.log('{}: Keys Synced'.format(self))
        return True
