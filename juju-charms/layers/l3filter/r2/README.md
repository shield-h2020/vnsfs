# Overview

This repository contains the [Juju] layer that represents a working example of a proxy charm.

# What is a proxy charm?

A proxy charm is a limited type of charm that does not interact with software running on the same host, such as controlling and configuring a remote device (a static VM image, a router/switch, etc.). It cannot take advantage of some of Juju's key features, such as [scaling], [relations], and [leadership].

Proxy charms are primarily a stop-gap, intended to prototype quickly, with the end goal being to develop it into a full-featured charm, which installs and executes code on the same machine as the charm is running.

# Usage

```bash
# Clone this repository
git clone https://osm.etsi.org/gerrit/osm/juju-charms
cd juju-charms

# Setup environment variables
source juju-env.sh

cd layers/pingpong
charm build

# Examine the built charm
cd ../../builds/pingpong
ls
actions       config.yaml  icon.svg    metadata.yaml     tests
actions.yaml  copyright    layer.yaml  reactive          tox.ini
bin           deps         lib         README.md         wheelhouse
builds        hooks        Makefile    requirements.txt

```

You can view a screencast of this: https://asciinema.org/a/96738

The `charm build` process combines this pingpong layer with each layer that it
has included in the `metadata.yaml` file, along with their various dependencies.

This built charm is what will then be used by the SO to communicate with the
VNF.

# Configuration

The pingpong charm has several configuration properties that can be set via
the SO:

- ssh-hostname
- ssh-username
- ssh-password
- ssh-private-key
- mode

The ssh-* keys are included by the `sshproxy` layer, and enable the charm to
connect to the VNF image.

The mode key must be one of two values: `ping` or `pong`. This informs the
charm as to which function it is serving.

# Contact Information
For support, please send an email to the [OSM Tech] list.


[OSM Tech]: mailto:OSM_TECH@list.etsi.org
[Juju]: https://jujucharms.com/about
[configure]: https://jujucharms.com/docs/2.0/charms-config
[scaling]: https://jujucharms.com/docs/2.0/charms-scaling
[relations]: https://jujucharms.com/docs/2.0/charms-relations
[leadership]: https://jujucharms.com/docs/2.0/developer-leadership
[created your charm]: https://jujucharms.com/docs/2.0/developer-getting-started





-----


# Integration

After you've [created your charm], open `interfaces.yaml` and add
`layer:sshproxy` to the includes stanza, as shown below:
```
includes: ['layer:basic', 'layer:sshproxy']
```

## Reactive states

This layer will set the following states:

- `sshproxy.configured` This state is set when SSH credentials have been supplied to the charm.


## Example
In `reactive/mycharm.py`, you can add logic to execute commands over SSH. This
example is run via a `start` action, and starts a service running on a remote
host.
```
...
import charms.sshproxy


@when('sshproxy.configured')
@when('actions.start')
def start():
    """ Execute's the command, via the start action` using the
    configured SSH credentials
    """
    sshproxy.ssh("service myservice start")

```

## Actions
This layer includes a built-in `run` action useful for debugging or running arbitrary commands:

```
$ juju run-action mycharm/0 run command=hostname
Action queued with id: 014b72f3-bc02-4ecb-8d38-72bce03bbb63

$ juju show-action-output 014b72f3-bc02-4ecb-8d38-72bce03bbb63
results:
  output: juju-66a5f3-11
status: completed
timing:
  completed: 2016-10-27 19:53:49 +0000 UTC
  enqueued: 2016-10-27 19:53:44 +0000 UTC
  started: 2016-10-27 19:53:48 +0000 UTC

```
## Known Limitations and Issues

### Security issues

- Password and key-based authentications are supported, with the caveat that
both (password and private key) are stored plaintext within the Juju controller.

# Configuration and Usage

This layer adds the following configuration options:
- ssh-hostname
- ssh-username
- ssh-password
- ssh-private-key

Once  [configure] those values at any time. Once they are set, the `sshproxy.configured` state flag will be toggled:

```
juju deploy mycharm ssh-hostname=10.10.10.10 ssh-username=ubuntu ssh-password=yourpassword
```
or
```
juju deploy mycharm ssh-hostname=10.10.10.10 ssh-username=ubuntu ssh-private-key="cat `~/.ssh/id_rsa`"
```


# Contact Information
Homepage: https://github.com/AdamIsrael/layer-sshproxy

[Juju]: https://jujucharms.com/about
[configure]: https://jujucharms.com/docs/2.0/charms-config
[scaling]: https://jujucharms.com/docs/2.0/charms-scaling
[relations]: https://jujucharms.com/docs/2.0/charms-relations
[leadership]: https://jujucharms.com/docs/2.0/developer-leadership
[created your charm]: https://jujucharms.com/docs/2.0/developer-getting-started
