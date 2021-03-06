#!/bin/bash

p_path="$1"
r_no="$2"

error() {
  printf "Error: $1\n"
  exit 0
}

[[ ! -f $p_path ]] && error "Could not find package in file system"
[[ -z $r_no ]] && error "The number of the OSM release must be provided"

p_name=$(basename $p_path)
p_id="${p_name%.tar.gz}"

[[ -z $p_id  || -z $p_path ]] && error "The path to an OSM package must be provided"

# Apply regexp and capture name and type for package
if [[ "$p_id" =~ ([a-zA-Z0-9]{1,})_([a-zA-Z0-9]{1,})[_(?:.*)]* ]]; then
  p_id_s=${BASH_REMATCH[1]}
  p_type=${BASH_REMATCH[2]}
  # Replace OSM-specific naming
  p_type="${p_type/vnfd/vnf}"
  p_type="${p_type/nsd/ns}"
fi

[[ -z $p_id_s ]] && error "Could not determine name of the package"
[[ -z $p_type ]] && error "Could not determine package type (NS or VNF). Expected formats: \${pkg_name}_ns.tar.gz, \${pkg_name}_vnf.tar.gz"

repo_root=$PWD

manifest_path="${repo_root}/security-manifest/${p_type}/${p_id_s}/manifest.yaml"
[[ ! -f $manifest_path ]] && error "Could not find SHIELD security manifest for this package"

pkg_tmp=$(mktemp -d)

# Copy package and corresponding security manifest
cp -Rp $p_path $pkg_tmp/
cp -p $manifest_path $pkg_tmp/
cd $pkg_tmp

juju_in=$(dpkg -l | grep juju)
if [[ -z $juju_in || $juju_in != *"ii"* ]]; then
  error "Juju and charms must be installed first: sudo add-apt-repository ppa:juju/stable; sudo apt update; sudo apt install -y juju charm"
fi

clear

# Fill in missing fields for manifest

gen_hash_for_pkg() {
  ns_pkg=$(sed -n -e '/package/ s/.*\: *//p' manifest.yaml)
  sha256_p_ns=$(sha256sum $ns_pkg)
  sha256_p_ns=$(echo $sha256_p_ns | awk '{print $1;}')
  sed -i -e "s/hash: <sha256-based hash of the .tar.gz package defined above>/hash: $sha256_p_ns/g" manifest.yaml
}

gen_version_for_pkg() {
  osm_release="OSM-R${r_no}"
  sed -i -e "s/type: <package data model format (OSM-R2, OSM-R4, ...)>/type: $osm_release/g" manifest.yaml
}

gen_target_for_pkg() {
  if [[ $p_name == *"docker"* ]]; then
    pkg_target="docker"
  else
    pkg_target="KVM"
  fi
  sed -i -e "s/target: <instantiation target (KVM, docker, ...)>/target: $pkg_target/g" manifest.yaml
}

att_file=""
copy_att_file() {
  att_file=$(sed -n -e '/attestation_filename/ s/.*\: *//p' manifest.yaml)
  att_path="${repo_root}/security-manifest/${p_type}/${p_id_s}/${att_file}"
  cp -p $att_path $pkg_tmp/
}

gen_hash_for_att() {
  if [[ ! -z $att_file ]]; then
    sha256_att_f=$(sha256sum $att_file)
    sha256_att_f=$(echo $sha256_att_f | awk '{print $1;}')
  fi
  sed -i -e "s/hash: <sha256-based hash of the .json attestation file defined above>/hash: $sha256_att_f/g" manifest.yaml
}

# Compute the hash for the VDU
if [[ $p_type == "ns" || $p_type == "vnf" ]]; then
  gen_hash_for_pkg
fi

# Select the OSM release of the package (default: OSM-R4)
gen_version_for_pkg

# Fill in missing fields for manifest
if [[ $p_type == "ns" ]]; then
  gen_target_for_pkg
fi

if [[ $p_type == "vnf" ]]; then
  copy_att_file
fi

# Compute the hash for the attestation file
if [[ $p_type == "vnf" ]]; then
  gen_hash_for_att
fi

if [[ ! -z $att_file ]]; then
  tar -zcf ${p_id}_shield.tar.gz manifest.yaml $att_file $p_name
  rm -rf $p_name $att_file manifest.yaml
else
  tar -zcf ${p_id}_shield.tar.gz manifest.yaml $p_name
  rm -rf $p_name manifest.yaml
fi

printf "\n\nNote\tSHIELD package for ${p_type} with name=${p_id_s} are available under ${pkg_tmp}\n\n"
