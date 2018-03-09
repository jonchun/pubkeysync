# PubKeySync

This is a tool to easily push public keys across all your servers. For hobbyists or developers that don't quite have a need for for full blown devops/configuration management software such as Puppet or Ansible, but would still like an easy way to synchronize public keys.

## Getting Started

This can be deployed on any Linux distribution that has the `ssh` binary available. It's as easy as manually editing the configuration files and running it to push/sync the changes.

### Prerequisites

- You will first need to have Python3 installed. 
- You will also need pip3 installed.

Ubuntu:
```
apt-get install python3 python3-pip
```

### Installing

First, clone this repository into a directory of your choice.

```
git clone https://github.com/Jonchun/pubkeysync.git
```

Change directories

```
cd pubkeysync
```

Make a copy of `pubkeysync.example.yaml`.
```
cp config/pubkeysync.example.yaml config/pubkeysync.yaml
```

Install required Python3 packages.
```
pip3 install -r requirements.txt
```

## Configuration

The configuration is done using [YAML](http://www.yaml.org/start.html). The structure of the configuration file is meant to be as straightforward to use as possible.

#### Terminology
- **Agent**: The agent refers to this software itself. This software opens remote SSH connections to the _Servers_ that you want to sync.
- **Groups**: _Groups_ are a way to classify your _Users_. _Users_ can belong to any number of _Groups_.
- **Users**: Each _User_ is representative of a single public key.
- **Servers**: Each _Server_ is representative of a remote SSH account.
- **Categories**: _Categories_ are a way to classify your _Servers_. _Servers_ can belong to any number of _Categories_.

#### Explanation of configuration keys
Any key names denoted with a star (*) are _REQUIRED_.
Key Name | Default Value | Explanation
--- | --- | ---
`private_key`* | `pubkeysync.key` | Private Key the agent uses to connect to remote servers.
`public_key`* | `pubkeysync.pub` | Public Key the agent uses when updating the `authorized_keys` file of remote servers.

`users:`
+ `-user_label:`

    + Key Name | Default Value | Explanation
        --- | --- | ---
        `key` | `user_label.pub` | Public Key for this user that gets synced to remote servers. Set this if you want to use a custom file name.
        `groups` | `[]` | List of comma separated strings indicating the _Groups_ that this _User_ belongs to.

`categories:`
+ `-category_label:`

    + Key Name | Default Value | Explanation
        --- | --- | ---
        `groups` | `[]` | List of comma separated strings indicating the _Groups_ that should have their keys synced if a server belongs to this _Category_.
        `users` | `[]` | List of comma separated strings indicating the _Users_ that should have their keys synced if a server belongs to this _Category_.
        `ssh_user` | `None` | If a ssh_user field is provided, all key-syncs for this category will be for the custom ssh_user rather than the default ssh_user. This is useful if you want to sync sets of keys to the same remote servers but with different usernames. (e.g. `root` vs `wheel`)

`servers:`
+ `-servers_label:`

    + Key Name | Default Value | Explanation
        --- | --- | ---
        `host`* | `None` | Remote IP address or hostname of your server.
        `ssh_user` | `root` | Remote user of your server.
        `ssh_port` | `22` | Remote port for SSH.
        `groups` | `[]` | List of comma separated strings indicating the _Groups_ that should have their keys synced to this _Server_.
        `users` | `[]` | List of comma separated strings indicating the _Users_ that should have their keys synced to this _Server_.
        `timeout` | 5 | This is the amount of time before an SSH connection to a remote server times out and is considered "Failed".
        `authorized_keys_file` | `~/.ssh/authorized_keys` | This is the remote file that gets updated with the public keys.
        

## Running
Once you've configured PubKeySync to your liking, you can simply execute the script.

**IMPORTANT:** Please make sure that your users' public keys reside in the `keys` directory. Otherwise, execution will fail since PubKeySync won't be able to load your users' keys.
```
python3 pubkeysync.py
```

## Contributing

Please feel free to make pull requests or open issues if you run into any trouble or unexpected behavior.


## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details
