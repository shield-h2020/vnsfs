# Set the Juju env variables for building a layer
source deps.sh

# Snap requires confinement on execution into own's home
if [[ $(get_distro_code_major) -ge 17 ]]; then
  export JUJU_REPOSITORY=$(echo $HOME)
else
  export JUJU_REPOSITORY=$(pwd)
fi
export INTERFACE_PATH=$JUJU_REPOSITORY/interfaces
export LAYER_PATH=$JUJU_REPOSITORY/layers
