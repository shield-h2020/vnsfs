#!/bin/bash

source "juju-charms/deps.sh"

v_id="$1"
r_no="$2"

min_r=2
max_r=4
repo_root=$PWD
pkg_tmp=$(mktemp -d)
v_id_vnfd="${pkg_tmp}/descriptor-packages/vnfd/${v_id}_vnf"
v_id_nsd="${pkg_tmp}/descriptor-packages/nsd/${v_id}_ns"
cp -Rp $repo_root/{descriptor-packages,juju-charms,tools} $pkg_tmp/
cd $pkg_tmp
#sudo chown $(whoami):$(whoami) $pkg_tmp -R

error() {
  printf "Error: $1\n"
  exit 0
}

[[ -z $v_id ]] && error "The name of a vNSF must be provided"
[[ -z $r_no ]] && error "The number of release must be provided"
[[ "$r_no" -lt ${min_r} || "$r_no" -gt ${max_r} ]] && error "Invalid number for release (expected: ${min_r}-${max_r})"
[[ ! -d $v_id_vnfd ]] && error "Provided vNSF has a name different to ${v_id}_vnf in the descriptor-packages folder"
[[ ! -d $v_id_nsd ]] && error "Provided NS has a name different to ${v_id}_ns in the descriptor-packages folder"
[[ ! -f ${v_id_vnfd}/${v_id}_vnfd.r${r_no}.yaml ]] && error "Provided vNSF has a name different to ${v_id}_vnfd.r${r_no}.yaml in the descriptor-packages folder"
[[ ! -f ${v_id_nsd}/${v_id}_nsd.r${r_no}.yaml ]] && error "Provided NS has a name different to ${v_id}_nsd.r${r_no}.yaml in the descriptor-packages folder"

clear

# Build charm
cd juju-charms
source juju-env.sh
if [ -d layers/${v_id} ]; then
  cd layers/${v_id}
  charm build -l DEBUG
  
  # Place charm into vNSF
  mkdir -p ${v_id_vnfd}/charms
  cd ../../
  mv builds/${v_id} ${v_id_vnfd}/charms/
fi

# Generate OSM package for vNSF
cd ${pkg_tmp}/descriptor-packages/vnfd
mv ${pkg_tmp}/descriptor-packages/vnfd/${v_id}_vnf/*.yaml ${pkg_tmp}/
[[ -f ${pkg_tmp}/${v_id}_vnfd.r${r_no}.yaml ]] && cp -p ${pkg_tmp}/${v_id}_vnfd.r${r_no}.yaml ${v_id}_vnf/${v_id}_vnfd.yaml
$PWD/../../tools/r${r_no}/generate_descriptor_pkg.sh -t vnfd ${v_id}_vnf
mv ${v_id}_vnf.tar.gz $pkg_tmp/

# Generate OSM package for NS
cd ${pkg_tmp}/descriptor-packages/nsd
mv ${pkg_tmp}/descriptor-packages/nsd/${v_id}_ns/*.yaml ${pkg_tmp}/
[[ -f ${pkg_tmp}/${v_id}_nsd.r${r_no}.yaml ]] && cp -p ${pkg_tmp}/${v_id}_nsd.r${r_no}.yaml ${v_id}_ns/${v_id}_nsd.yaml
../../tools/r${r_no}/generate_descriptor_pkg.sh -t nsd ${v_id}_ns
mv ${v_id}_ns.tar.gz $pkg_tmp/

rm -rf ${pkg_tmp}/{*.yaml,descriptor-packages,juju-charms,tools}

printf "\n\nNote\tPackages for vNSF and NS with name=${v_id} are available under ${pkg_tmp}\n\n"
