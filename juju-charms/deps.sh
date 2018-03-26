#!/bin/bash

error() {
  printf "Error: $1\n"
  exit 0
}

get_distro() {
  echo $(lsb_release --i | cut -f2)
}
get_distro_code() {
  echo $(lsb_release --release | cut -f2)
}
get_distro_code_major() {
  code=$(get_distro_code)
  echo "${code%.*}"
}
get_distro_code_minor() {
  code=$(get_distro_code)
  echo "${code##*.}"
}

max_allow_code=17

[[ ($(get_distro) != "Debian" && $(get_distro) != "Ubuntu") ]] && error "Must run on a Debian/Ubuntu system"
# Temporary restriction (note: "charm build" from snap fails with the current charm structure) 
[[ $(get_distro) == "Ubuntu" && $(get_distro_code_major) -ge $max_allow_code ]] && error "Must run on Ubuntu version prior to 17"

juju_in=$(which charm)
if [[ -z $juju_in ]]; then
  if [[ $(get_distro_code_major) -ge 17 ]]; then
    error "Juju and charms must be installed first: sudo apt update; sudo snap install charm"
  else
    error "Juju and charms must be installed first: sudo add-apt-repository ppa:juju/stable; sudo apt update; sudo apt install -y juju charm"
  fi
fi
