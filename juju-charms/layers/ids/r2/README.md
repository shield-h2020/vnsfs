# Overview

This repository contains the [Juju] layer that represents a working example of a proxy charm.

# What is a proxy charm?

A proxy charm is a limited type of charm that does not interact with software running on the same host, such as controlling and configuring a remote device (a static VM image, a router/switch, etc.). It cannot take advantage of some of Juju's key features, such as [scaling], [relations], and [leadership].

Proxy charms are primarily a stop-gap, intended to prototype quickly, with the end goal being to develop it into a full-featured charm, which installs and executes code on the same machine as the charm is running.

# Usage

```bash
current=$PWD
# Clone this repository
git clone https://github.com/shield-h2020/vnsfs.git
cd vnsfs/juju-charms

# Setup environment variables
source juju-env.sh

cd layers/l23filter
charm build

# Examine the built charm
cd builds/l23filter
ls
actions       config.yaml  icon.svg    metadata.yaml     tests
actions.yaml  copyright    layer.yaml  reactive          tox.ini
bin           deps         lib         README.md         wheelhouse
builds        hooks        Makefile    requirements.txt

```

The `charm build` process combines this l23filter layer with each layer that it
has included in the `metadata.yaml` file, along with their various dependencies.

This built charm is what will then be used by the SO to communicate with the
VNF.

# Configuration

The l23filter charm has several configuration properties that can be set via
the SO:

- ssh-hostname
- ssh-username
- ssh-password
- ssh-private-key
- rest-ip
- rest-port

The ssh-* keys are included by the `sshproxy` layer, and enable the charm to
connect to the VNF image.

# Integration

Copy the built charm into the appropriate folder within the VNF. From the `builds/l23filter` folder:

```bash
cd ../../
l23filter_vnfd=../../../descriptor-packages/vnfd/vFirewall_vnf
mkdir -p $l23filter_vnfd/charms
mv builds/l23filter $l23filter_vnfd/charms/
rm -r builds
cd $l23filter_vnfd
```

Once placed in the VNF package, the VNF descriptor must be configured appropriately, and the
OSM package is to be re-created:

```bash
cd ..
../generate_descriptor_pkg.sh vFirewall_vnf
```
