# vNSFs

Repository for NF packages, as used in [SHIELD](https://www.shield-h2020.eu):

* Package descriptors for vNSFs and NSs (see [*OSM samples*](https://osm.etsi.org/gitweb/?p=osm/devops.git;a=tree;f=descriptor-packages))
* Juju charms for vNSFs (see [*OSM samples*](https://osm.etsi.org/gitweb/?p=osm/devops.git;a=tree;f=juju-charms))
* Sources and data required for vNSF and NS operation

# Preparing the OSM package

An OSM package can contain the data for either a vNSF or NS.

To prepare a new package (assume it's called `$pkg_name`), you must first place the descriptors for your vNSF and NS, as well as the Juju charms for your vNSF, in the proper subdirectories:

```
.
+-- descriptor-packages
|   +-- nsd
|   |   +-- ${pkg_name}_ns
|   +-- vnfd
|       +-- ${pkg_name}_vnf
+-- juju-charms
|   +-- layers
|       +-- ${pkg_name}
+-- src
    +-- vnf
        +-- ${pkg_name}
```

Now, you may simply pass the package name to the generation script:
```
generate_osm_package.sh ${pkg_name}
```

The script will download the needed packages, build the Juju charms and invoke the OSM built-in scripts to generate the package.
