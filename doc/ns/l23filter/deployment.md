# Deployment

The following steps indicate how to deploy this package.

## Onboarding

1. Generate the `$pkg_type_nsd.tar.gz` and `$pkg_type_vnfd.tar.gz` packages (follow instructions at root `README.md`)

2. Point to the OSM dashboard and access the "Catalog" section

3. Onboard the vNSF package, first, and the NS package after that
  * From the OSM dashboard: select the "Catalog", drag and drop the package on the designated area
  * From the OSM CLI:
    * Upload your package to the VM hosting the OSM instance
    * Access the `SO-ub` container
    * Run the following (replace values for your own environment):
      ```
      # Variable definition
      pkg_name="l23filter"
      ## Externally accessible IP of the VM hosting the OSM instance
      osm_ins="a.b.c.d"
      ## IP of the lxdbr0, inside the VM hosting the OSM instance
      osm_ins_lxdbr0="a2.b2.c2.d2"
      
      # Onboard your vNSF and NS packages from local to the OSM NFVO instance
      scp -r ${pkg_name}_*.tar.gz localadmin@${osm_ins}:/tmp/
       
      # Organise them into the common folder
      ssh localadmin@{osm_ins}
      sudo mv /tmp/${pkg_name}_*.tar.gz /opt/osm/
      
      # Enter the container
      lxc exec SO-ub bash
      pkg_name="something"
      
      # Copy the packages from within the container
      scp -r localadmin@${osm_ins_lxdbr0}:/opt/osm/${pkg_name}_*.tar.gz .
      
      # Onboard vNSF and NS packages
      /root/SO/rwlaunchpad/plugins/rwlaunchpadtasklet/scripts/onboard_pkg -s 127.0.0.1 -u ${pkg_name}_vnf.tar.gz
      /root/SO/rwlaunchpad/plugins/rwlaunchpadtasklet/scripts/onboard_pkg -s 127.0.0.1 -u ${pkg_name}_ns.tar.gz
      
      # In case of errors, check the log
      tailf /var/log/rift/rift.log
      ```

## Instantiation

1. Point to the OSM dashboard and access the "Launchpad > Instantiate" section

2. Fill the form data
   * Name of the NS
   * Which VIM / DC to run the NS on
   * Juju agent
   * Virtual links: on the management network (e.g., VLD1), select the network name used by the VIM (e.g., "provider" for ORION VIM)

3. Click on "Launch" and wait for the NS to run

## Configuration

1. Point to the OSM dashboard and access the "Dashboard > Viewport Dashboard (on NS details) > Compute topology" section
2. Identify the MSPL (middle-level security policy) used by this package
3. Point to a running vNSFO instance for SHIELD and [send the MSPL](https://github.com/shield-h2020/nfvo/blob/master/README.md#execute-pre-defined-action-from-a-specific-vnsf)
4. Access "Dashboard > Viewport Dashboard > l23filter > Service Primitive", select the `set-policies` action and look for a change in the status for the latest request

## Testing

1. Execute the `set-policies` action from the OSM GUI, using the `mspl/vnf/l23filter/sample.mspl` content
2. Wait for the action to complete (green light)
3. If successful, get the IP of the deployed VM and verify that the rule is shown in `http://${ip}:8082`
