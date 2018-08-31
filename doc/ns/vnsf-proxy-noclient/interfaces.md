# Interfaces

## Management

### VLD1

* Virtual link
  * ID: `vld-1`
  * Type: ELAN
* vNSF
  * Connection point: vNSF #1
  * Connection point ID: `proxy-vnf`
  * Interface on vNSF: `eth2`
* Allows to
  * Access to each constituent vNSF
* Configuration: during instantiation, a network name (used by OpenStack) must be provided

## Others

### VLD2

* Virtual link
  * ID: `vld-2`
  * Type: ELAN
  * vNSF
    * Connection point: vNSF #1
    * Connection point ID: `proxy-vnf`
    * Interface on vNSF: `eth0`
* Allows to
  * -
* Configuration: -

### VLD3

* Virtual link
  * ID: `vld-3`
  * Type: ELAN
* vNSF
  * Connection point: vNSF #1
  * Connection point ID: `proxy-vnf`
  * Interface on vNSF: `eth1`
* Allows to
  * -
* Configuration: during instantiation, a network name (used by OpenStack) must be provided
