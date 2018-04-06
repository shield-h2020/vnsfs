#!/bin/bash

p_path="$1"

error() {
  printf "Error: $1\n"
  exit 0
}

[[ ! -f $p_path ]] && error "Could not find package in file system"

p_name=$(basename $p_path)
#p_id="${p_name%.tar.gz}"
p_id=$p_name

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
echo $manifest_path
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

# Uncompress package to verify contents
#tar -zxf $p_name
#rm $p_id

gen_hash_for_pkg() {
  ns_pkg=$(sed -n -e '/package/ s/.*\: *//p' manifest.yaml)
  sha256_p_ns=$(sha256sum $ns_pkg)
  sha256_p_ns=$(echo $sha256_p_ns | awk '{print $1;}')
#  grep -l "hash: <sha256-based hash of the .tar.gz package defined above>" manifest.yaml | xargs sed -i -e "s|hash: <sha256-based hash of the .tar.gz package defined above>|hash: $sha256_p_ns|"
  sed -i -e "s/hash: <sha256-based hash of the .tar.gz package defined above>/hash: $sha256_p_ns/g" manifest.yaml
}

# Fill in missing fields for manifest
if [[ $p_type == "ns" ]]; then
  gen_hash_for_pkg
elif [[ $p_type == "vnf" ]]; then
  gen_hash_for_pkg
fi

tar -zcf ${p_id}_shield.tar.gz manifest.yaml $p_name
rm -rf $p_name manifest.yaml

printf "\n\nNote\tSHIELD package for ${p_type} with name=${p_id_s} are available under ${pkg_tmp}\n\n"
