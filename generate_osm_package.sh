#!/bin/bash

source "juju-charms/deps.sh"

v_id="$1"
v_type="$2"
r_no="$3"
d_path="$4"

min_r=2
max_r=5
user=$SUDO_USER
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

[[ -z $v_id ]] && error "The name of a vNSF or NS must be provided"
[[ -z $r_no ]] && error "The number of the OSM release must be provided"
[[ "$r_no" -lt ${min_r} || "$r_no" -gt ${max_r} ]] && error "Invalid number for OSM release (expected: ${min_r}-${max_r})"
[[ -z $v_type ]] && error "The type of package (vNSF or NS) must be provided"
[[ ! -d $v_id_vnfd ]] && error "Provided vNSF has a name different to ${v_id}_vnf in the descriptor-packages folder"
[[ ! -d $v_id_nsd ]] && error "Provided NS has a name different to ${v_id}_ns in the descriptor-packages folder"
[[ ! -f ${v_id_vnfd}/${v_id}_vnfd.r${r_no}.yaml ]] && error "Provided vNSF has a name different to ${v_id}_vnfd.r${r_no}.yaml in the descriptor-packages folder"
[[ ! -f ${v_id_nsd}/${v_id}_nsd.r${r_no}.yaml ]] && error "Provided NS has a name different to ${v_id}_nsd.r${r_no}.yaml in the descriptor-packages folder"

clear

if [[ ${v_type} == "vnf" ]]; then
  # Build charm
  cd juju-charms
  source juju-env.sh ${r_no}
  if [[ -d layers/${v_id}/r${r_no} ]]; then
    mkdir -p ${JUJU_REPOSITORY}/${v_id}
    cp -Rp layers/${v_id}/r${r_no}/* ${JUJU_REPOSITORY}/${v_id}/
    user_perm=$(basename $HOME)
    chown ${user_perm}:${user_perm} -R ${JUJU_REPOSITORY}/${v_id}/
    cd ${JUJU_REPOSITORY}/${v_id}
    charm build -l DEBUG
    
    # Place charm into vNSF
    mkdir -p ${v_id_vnfd}/charms
    cd ../
    mv builds/${v_id} ${v_id_vnfd}/charms/
  fi
fi

pkg_dst=${pkg_tmp}
if [[ ! -z ${d_path} ]]; then
  pkg_dst=${d_path}
fi

if [[ ${v_type} == "vnf" ]]; then
  # Generate OSM package for vNSF
  cd ${pkg_tmp}/descriptor-packages/vnfd
  mv ${pkg_tmp}/descriptor-packages/vnfd/${v_id}_vnf/*.yaml ${pkg_tmp}/
  [[ -f ${pkg_tmp}/${v_id}_vnfd.r${r_no}.yaml ]] && cp -p ${pkg_tmp}/${v_id}_vnfd.r${r_no}.yaml ${v_id}_vnf/${v_id}_vnfd.yaml
  $PWD/../../tools/r${r_no}/generate_descriptor_pkg.sh -t vnfd ${v_id}_vnf
  sudo mv ${v_id}_vnf.tar.gz $pkg_dst/
  sudo chown ${user}:${user} -R $pkg_dst/
fi

if [[ ${v_type} == "ns" ]]; then
  # Generate OSM package for NS
  cd ${pkg_tmp}/descriptor-packages/nsd
  mv ${pkg_tmp}/descriptor-packages/nsd/${v_id}_ns/*.yaml ${pkg_tmp}/
  [[ -f ${pkg_tmp}/${v_id}_nsd.r${r_no}.yaml ]] && cp -p ${pkg_tmp}/${v_id}_nsd.r${r_no}.yaml ${v_id}_ns/${v_id}_nsd.yaml
  $PWD/../../tools/r${r_no}/generate_descriptor_pkg.sh -t nsd ${v_id}_ns
  sudo mv ${v_id}_ns.tar.gz $pkg_dst/
  sudo chown ${user}:${user} -R $pkg_dst/
fi

rm -rf ${pkg_tmp}/{*.yaml,descriptor-packages,juju-charms,tools}

printf "\n\nNote\tPackage for ${v_type^^} with name=${v_id} is available under ${pkg_dst}\n\n"
