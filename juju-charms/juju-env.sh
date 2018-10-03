# Set the Juju env variables for building a layer
source deps.sh

release=$1

juju_charm=$(charm version | head -n 1 | cut -d" " -f2)

# Snap requires confinement on execution into own's home
if [[ $release -ge 4 && ${juju_charm} == *"2.3."* ]]; then
  export JUJU_REPOSITORY=$(echo $HOME)/vnsfs
  if [[ -f /bin/charm ]]; then
    sudo cp -p /bin/charm /bin/charm.bak
  fi
  sudo ln -sf /snap/bin/charm /bin/charm
else
  export JUJU_REPOSITORY=$(pwd)
fi
export INTERFACE_PATH=$JUJU_REPOSITORY/interfaces
export LAYER_PATH=$JUJU_REPOSITORY/layers

# Create directories in case these do not exist
mkdir -p $JUJU_REPOSITORY
mkdir -p $INTERFACE_PATH
mkdir -p $LAYER_PATH
