# vNSFs

Repository for NF packages, as used in [SHIELD](https://www.shield-h2020.eu):

* Package descriptors for vNSFs and NSs (see [*OSM samples*](https://osm.etsi.org/gitweb/?p=osm/devops.git;a=tree;f=descriptor-packages))
* Juju charms for vNSFs (see [*OSM samples*](https://osm.etsi.org/gitweb/?p=osm/devops.git;a=tree;f=juju-charms))
* Sources and data required for vNSF and NS operation

# Preparing the OSM package

An OSM package can contain the data for either a vNSF or NS.

To prepare a new package (assume it's called `$pkg_name`), carry on with the following steps.

1. Identify `$pkg_type`; that is, whether you are creating a package for a vNSF or a NS. Possible values: `vnfd`, `nsd`

2. Define the structure for your package and place the descriptors for your vNSF and NS, as well as the specific resources needed (icon, cloud_init scripts, etc) by it

  ```
${pkg_name}_${pkg_type}/
+-- cloud_init
|   +-- ${pkg_name}_cloud_init.cfg
+-- icons
|   +-- ${pkg_name}.png
+-- ...
+-- ${pkg_name}_nsd.yaml
  ```

  Note: the root directory must be named `${pkg_name}_${pkg_type}`.
  Note: the only mandatory file is the descriptor itself (the YAML file).

3. Place the directory with the package structure under `descriptor-packages/${pkg_type}`

  ```
.
+-- descriptor-packages
|   +-- nsd                      # <-- Place the NS package here
|   |   +-- ${pkg_name}_ns
|   +-- vnfd                     # <-- Place the vNSF package here
|       +-- ${pkg_name}_vnf
+-- juju-charms
|   +-- layers
|       +-- ${pkg_name}
+-- src
    +-- vnf
        +-- ${pkg_name}
  ```

4. Define the structure for the Juju charms used by your vNSF package

  ```
${pkg_name}/
+-- actions
|   +-- delete-policies
|   +-- delete-policy
|   +-- get-policies
|   +-- set-policies
+-- actions.yaml
+-- config.yaml
+-- icon.svg
+-- layer.yaml
+-- metadata.yaml
+-- reactive
|   +-- ${pkg_name}.py
+-- README.md
+-- tests
    +-- 00-setup
    +-- 10-deploy
  ```

  Note: the root directory must be named `${pkg_name}`.
  Note: there may be other actions allowed -- these ones are the minimum required in order to allow configuration from vNSFO.

5. Place the directory with the specific Juju charms under `juju-charms/layers`

  ```
.
+-- descriptor-packages
|   +-- nsd
|   |   +-- ${pkg_name}_ns
|   +-- vnfd
|       +-- ${pkg_name}_vnf
+-- juju-charms                  # <-- Place the vNSF charms here
|   +-- layers
|       +-- ${pkg_name}
+-- src
    +-- vnf
        +-- ${pkg_name}
  ```

6. Run the generation script, using the package name as argument:

  ```
generate_osm_package.sh ${pkg_name}
  ```

  The script will download the needed packages, build the Juju charms and invoke the OSM built-in scripts to generate the package.
