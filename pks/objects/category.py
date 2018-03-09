from copy import copy

class Category:
    def __init__(self, agent, category_dict):
        self.agent = agent
        self.label, category_config = category_dict.popitem()
        self.ssh_user = category_config.get('ssh_user', None)
        self.groups = category_config.get('groups', [])
        self.users = category_config.get('users', [])

    def __repr__(self):
        return '<Category {}>'.format(self.label)

    # Returns new servers and modifies old ones
    def get_new_servers(self):
        new_servers = []
        for server in self.agent.servers:
            if self.label in server.categories:
                server_new = copy(server)
                # Add all groups/users from this category to the server
                server_new.groups = list(set(self.groups + server_new.groups))
                server_new.users = list(set(self.users + server_new.users))

                # Check if ssh_user is set
                if self.ssh_user is not None and self.ssh_user != server_new.ssh_user:
                    server_new.ssh_user = self.ssh_user
                    new_servers.append(server_new)
                else:
                    if (server.groups, server.users) != (server_new.groups, server_new.users):
                        # If the ssh_user is the same but groups/users are different, we need to update the old server instance instead of adding a new one with the superset.
                        server.groups = server_new.groups
                        server.users = server_new.users
        return new_servers
