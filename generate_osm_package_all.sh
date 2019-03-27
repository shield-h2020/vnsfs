#!/bin/bash

r_no="$1"
d_path="$2"

min_r=2
max_r=5
pkg_tmp=$(mktemp -d)

error() {
  printf "Error: $1\n"
  exit 0
}

[[ -z $r_no ]] && error "The number of the OSM release must be provided"
[[ "$r_no" -lt ${min_r} || "$r_no" -gt ${max_r} ]] && error "Invalid number for OSM release (expected: ${min_r}-${max_r})"

pkg_dst=${pkg_tmp}
if [[ ! -z ${d_path} ]]; then
  pkg_dst=${d_path}
fi

pkt_type=( vnf ns )

for ns in $(ls $PWD/descriptor-packages/nsd); do
    ns_name=${ns%_*}
    printf "Generating vNSF and NS package for ${ns_name}\n\n\n"
    for ns_type in "${pkt_type[@]}"; do
        sudo ./generate_osm_package.sh ${ns_name} ${ns_type} ${r_no} ${pkg_dst}
    done
    printf "\n\n----------\n\n"
done
