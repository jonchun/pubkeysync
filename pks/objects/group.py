class Group:
    def __init__(self, agent, group_dict):
        self.agent = agent
        self.label, group_config = group_dict.popitem()

    def __repr__(self):
        return '<Group {}>'.format(self.label)

    def get_users(self):
        group_users = list((user for user in self.agent.users if self.label in user.groups))
        return group_users
