#!/bin/bash

source "juju-charms/deps.sh"

v_id="$1"

repo_root=$PWD
pkg_tmp=$(mktemp -d)
v_id_vnfd="${pkg_tmp}/descriptor-packages/vnfd/${v_id}_vnf"
v_id_nsd="${pkg_tmp}/descriptor-packages/nsd/${v_id}_ns"
cp -Rp $repo_root/{descriptor-packages,juju-charms} $pkg_tmp/
cd $pkg_tmp
#sudo chown $(whoami):$(whoami) $pkg_tmp -R

error() {
  printf "Error: $1\n"
  exit 0
}

[[ -z $v_id ]] && error "The name of a vNSF must be provided"
[[ ! -d $v_id_vnfd ]] && error "Provided vNSF has a name different to ${v_id}_vnf in the descriptor-packages folder"
[[ ! -d $v_id_nsd ]] && error "Provided NS has a name different to ${v_id}_ns in the descriptor-packages folder"

clear

# Build charm
cd juju-charms
source juju-env.sh
cd layers/${v_id}
charm build -l DEBUG

# Place charm into vNSF
mkdir -p ${v_id_vnfd}/charms
cd ../../
mv builds/${v_id} ${v_id_vnfd}/charms/

# Generate OSM package for vNSF
cd ${pkg_tmp}/descriptor-packages/vnfd
../generate_descriptor_pkg.sh ${v_id}_vnf
mv ${v_id}_vnf.tar.gz $pkg_tmp/

# Generate OSM package for NS
cd ${pkg_tmp}/descriptor-packages/nsd
../generate_descriptor_pkg.sh ${v_id}_ns
mv ${v_id}_ns.tar.gz $pkg_tmp/

rm -rf ${pkg_tmp}/{descriptor-packages,juju-charms}

printf "\n\nNote\tPackages for vNSF and NS with name=${v_id} are available under ${pkg_tmp}\n\n"
