class User:
    def __init__(self, agent, user_dict):
        self.agent = agent
        self.label, user_config = user_dict.popitem()
        if user_config is None:
            user_config = {}
        self.key = ""
        self.key_file = user_config.get("key", "{}.pub".format(self.label))
        self.load_key()
        self.groups = user_config.get('groups', [])


    def __repr__(self):
        return '<User {}>'.format(self.label)

    def load_key(self):
        try:
            with open('keys/{}'.format(self.key_file), 'r') as f:
                key_string = f.read()
        except Exception:
            raise Exception('Unable to load key file for {}'.format(self))
        else:
            self.key = key_string
