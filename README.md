# vNSFs

Repository for OSM-based NS and vNSF packages, as used in [SHIELD](https://www.shield-h2020.eu):

## Structure definition

This repository contains placeholders, to be filled per NS and/or vNSF packages.

* Package descriptors and resources for NSs and vNSFs (see [*OSM samples*](https://osm.etsi.org/gitweb/?p=osm/devops.git;a=tree;f=descriptor-packages))
* Package documentation (deployment guide, required resources, interfaces)
* Juju charms for vNSFs (see [*OSM samples*](https://osm.etsi.org/gitweb/?p=osm/devops.git;a=tree;f=juju-charms))
* MSPL sample/s for each vNSF (ideally with scaped double quotes)
* SHIELD security manifests (see samples for [*vNSF*](https://github.com/shield-h2020/store/blob/master/docs/vnsf/packaging.md#datamodel) and [*NS*](https://github.com/shield-h2020/store/blob/master/docs/ns/packaging.md#security-manifest-manifestyaml))
* Sources and data required for vNSF and NS operation

The high-level layout and a brief description is provided below.

```
.
+-- descriptor-packages          # <-- NS and vNSF descriptors and static resources
|   +-- nsd
|   |   +-- ${pkg_name}_ns
|   +-- vnfd
|       +-- ${pkg_name}_vnf
+-- doc                          # <-- NS and vNSF documentation: guide, resources, interfaces
|   +-- ns
|       +-- ${pkg_name}
|   +-- vnf
|       +-- ${pkg_name}
+-- juju-charms                  # <-- vNSF charms (e.g., policy-to-configuration translation)
|   +-- layers
|       +-- ${pkg_name}
+-- mspl                         # <-- vNSF sample/s for MSPL (medium-level security policies)
|   +-- vnf
|       +-- ${pkg_name}
+-- security-manifest            # <-- NS and vNSF security manifests (used to generate SHIELD package)
|   +-- ns
|   |   +-- ${pkg_name}
|   +-- vnf
|       +-- ${pkg_name}
+-- src                          # <-- vNSF source code: internal logic
    +-- vnf
        +-- ${pkg_name}
```

## Preparing the OSM package

An OSM package can contain the data for either a vNSF or NS.

To prepare a new package (assume it's called `$pkg_name`), carry on with the following steps.

1. Identify `$pkg_type`; that is, whether you are creating a package for a vNSF or a NS. Possible values: `vnfd`, `nsd`

2. Define the structure for your package and place the descriptors for your vNSF and NS, as well as the specific resources needed (icon, cloud_init scripts, etc) by it

  ```
${pkg_name}_${pkg_type}/
+-- cloud_init                         # <-- Optional
|   +-- ${pkg_name}_cloud_init.cfg
+-- icons                              # <-- Optional
|   +-- ${pkg_name}.png
+-- ...                                # <-- Optional
+-- ${pkg_name}_nsd.yaml               # <-- Mandatory
```

  Note: the root directory must be named `${pkg_name}_${pkg_type}`.
  Note: the only mandatory file is the descriptor itself (the YAML file).

3. Place the directory with the package structure under `descriptor-packages/${pkg_type}`

  ```
.
+-- descriptor-packages
|   +-- nsd                      # <-- Place the NS package under this directory
|       +-- ${pkg_name}_ns
|   +-- vnfd                     # <-- Place the vNSF package under this directory
|       +-- ${pkg_name}_vnf
...
```

4. Define the structure for the Juju charms used by your vNSF package

  ```
${pkg_name}/
+-- actions                  # <-- Minimum actions required for SHIELD
|   +-- ...
|   +-- delete-policies
|   +-- delete-policy
|   +-- get-policies
|   +-- set-policies
|   +-- ...
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
  Note: other actions may be provided -- the above ones are the minimum required in order to allow configuration from vNSFO.

5. Place the directory with the specific Juju charms under `juju-charms/layers`

  ```
.
...
+-- juju-charms                  # <-- Place the vNSF charms here
|   +-- layers
|       +-- ${pkg_name}
...
```

6. Run the generation script, using the package name as argument:

  ```
sudo ./generate_osm_package.sh ${pkg_name}
```

  The script will download the needed packages, build the Juju charms and invoke the OSM built-in scripts to generate the OSM package.

## Documenting the package

For certification purposes, the NS and vNSF developer may want to document each package. A certified-to-be SHIELD package must provide the following data:

* **Deployment guide**: clear steps for deployment via OSM
* **Resource requirements**: minimum and expected resources needed (memory, hard disk, network interfaces, etc)
* **Interfaces**: clear definition of the vNSF management interfaces

Also, for operational purposes there should be enough information to be able to externally interact with the vNSF and its contained services:

* **Services**: Define services and access per vNSF and VDU

```
...
+-- doc
|   +-- ns                        # <-- Documentation per NS
|       +-- ${pkg_name}
|           +-- deployment.md     # <-- Deployment guide
|           +-- interfaces.md     # <-- Details on ifaces (min: management)
|           +-- requirements.md   # <-- Minimum & expected required resources
|   +-- vnf                       # <-- Documentation per vNSF
|       +-- ${pkg_name}
|           +-- ${vnsf_name}      # <-- Name for specific vNSF
|               +-- services.md   # <-- Definition of services and access per VDU
...
```

## Testing the package

For certification purposes, the NS and vNSF developer may want to test each package. A certified-to-be SHIELD package must test the following:

* Non-functional testing procedures:
 * Durability: Continuous running for periods of 4hs, 8hs, 24hs, 48hs
 * Failure recovery: show report incident and recovery process in the following cases:
   * VM restart
   * Platform restart
   * VM shutdown
   * Platform shutdown
 * vNSF hardening as defined in D2.2, NF09
* Functional testing procedures:
 * Actual package functionality
 * Interface with DARE is able to send collected data
 * Interface with vNSFO is able to receive medium-level security policies
 * Performance: ensure throughput targets are met by the package. Testing includes different packet sizes (including IMIX) and protocols (UDP and TCP). For each target, delay, packet loss and jitter should be measured.

## Preparing the SHIELD package

**Work in progress**

A SHIELD package contains some extra meta-data (mostly for security attestation purposes), stored in its security `manifest.yml`.
Specific scripts will be provided in time to generate this kind of package.

1. Add the SHIELD security manifest for each vNSF and NS in the following folder:

  ```
  ...
  +-- security-manifest            # <-- NS and vNSF security manifests (used to generate SHIELD package)
  |   +-- ns
  |   |   +-- ${pkg_name}
  |   +-- vnf
  |       +-- ${pkg_name}
  ...
  ```

2. Run the generation script, using the absolute path to the (vNSF and NS) package and the OSM release (numeric) as argument:

  ```
  sudo ./generate_shield_package.sh ${path_to_package} ${release_number}
  ```

  The script will fetch the OSM package, compute its SHA-256 hash and insert it into the `manifest.yml` (security manifest), then generate the SHIELD package.
  Note: for the vNSF package, extra hashes or keys may be needed for attestation purposes. Manually modify these beforehand, in the `security-manifest` directory.

