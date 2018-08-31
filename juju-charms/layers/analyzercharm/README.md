# Overview

This repository contains the [Juju] layer that represents a charm for an HTTPS Analyzer.

# What is a proxy charm?

A proxy charm is a limited type of charm that does not interact with software running on the same host, such as controlling and configuring a remote device (a static VM image, a router/switch, etc.). It cannot take advantage of some of Juju's key features, such as [scaling], [relations], and [leadership].

Proxy charms are primarily a stop-gap, intended to prototype quickly, with the end goal being to develop it into a full-featured charm, which installs and executes code on the same machine as the charm is running.

# Usage

```bash
# Clone this repository
cd juju-charms

# Setup environment variables
source juju-env.sh

cd layers/analyzercharm
charm build

# Examine the built charm
cd ../../builds/analyzercharm
ls
actions       config.yaml  icon.svg    metadata.yaml     tests
actions.yaml  copyright    layer.yaml  reactive          tox.ini
bin           deps         lib         README.md         wheelhouse
builds        hooks        Makefile    requirements.txt

```

The `charm build` process combines this `analyzercharm` layer with each layer that it
has included in the `metadata.yaml` file, along with their various dependencies.

This built charm is what will then be used by the SO to communicate with the
VNF.

# Configuration

The `analyzercharm` charm has several configuration properties that can be set via
the SO:

- ssh-hostname
- ssh-username
- ssh-password
- ssh-private-key

The ssh-* keys are included by the `sshproxy` layer, and enable the charm to
connect to the VNF image.

Once those values are set, the `sshproxy.configured` state flag will be toggled.

# Reactive states

The layers will set the following states:

- `sshproxy.configured` This state is set when SSH credentials have been supplied to the charm.
- `analyzercharm.configured` This state is set after verifying the ssh credentials.

# Actions

In `reactive/analyzercharm.py`, you can add more logic to execute commands over SSH. The actual proxycharm has the following actions:

- `start- softflowd` -> Starts Softflowd – NetFlow network traffic analyzer.
- `stop- softflowd` -> Stops Softflowd – NetFlow network traffic analyzer.
- `restart- softflowd` -> Restarts Softflowd – NetFlow network traffic analyzer.
-	`start- analyzer` -> Starts the https analyzer.
-	`stop- analyzer` -> Stops the https analyzer.
-	`restart- analyzer` -> Restarts the https analyzer.
-	`forensic-mode` -> Changes tstat to realtime mode. It records one entry flow per completed transaction.
-	`realtime-mode` -> Changes tstat to realtime mode. It records multiple entry flows per only one transaction.
-	`change-network` -> Changes the path where the trained network for machine learning is placed.

Using OSM r4 interface, after instantiating, go to NS Instances -> Actions-> Exec NS Primitive.
A new window will appear, with four fields (Primitive / VNF Member index / Name / Value).
The first two are always complusory, you must write the name of the action and VNF Member index.
The other two are Primitive parameters, used for example in a `set` (change-network).

To run an action from the OSM terminal:

```
$ juju run-action mycharm/0 actionname
```

## Known Limitations and Issues

### Security issues

- Password and key-based authentications are supported, with the caveat that
both (password and private key) are stored plaintext within the Juju controller.
