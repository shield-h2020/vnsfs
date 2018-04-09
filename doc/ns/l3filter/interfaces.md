# Interfaces

## Management

### VLD1

* Virtual link
  * ID: `l3filter_nsd_vld1`
  * Type: provider
* vNSF
  * Connection point: vNSF #1
  * Connection point ID: `l3filter_vnfd`
  * Interface on vNSF: `eth0`
* Allows to
  * Access to each constituent vNSF
  * Receive MSPL from the vNSFO
* Configuration: during instantiation, a network name (used by OpenStack) must be provided

## Others

### VLD2

* Virtual link
  * ID: `l3filter_nsd_vld2`
  * Type: none
* vNSF
  * Connection point: vNSF #1
  * Connection point ID: `l3filter_vnfd`
  * Interface on vNSF: `eth1`
* Allows to
  * -
* Configuration: -

### VLD3

* Virtual link
  * ID: `l3filter_nsd_vld3`
  * Type: none
* vNSF
  * Connection point: vNSF #1
  * Connection point ID: `l3filter_vnfd`
  * Interface on vNSF: `eth2`
* Allows to
  * -
* Configuration: -
