# Deployment

The following steps indicate how to deploy this package.

## Onboarding

1. Generate the `$pkg_type_nsd.tar.gz` and `$pkg_type_vnfd.tar.gz` packages (follow instructions at root `README.md`)

2. Point to the OSM dashboard and access the "Project > VNF Packages" section

3. Onboard the vNSF package
  * From the OSM dashboard: select the "Onboard VNFD", drag and drop the package on the designated area
  * From the OSM CLI:
    * Upload your package to the VM hosting the OSM instance
    * Run the following (replace values for your own environment):
      ```
      osm vnfd-create ${pkg_name}
      osm vnfd-list
      ```
4. Do the same with the NS Packages

## Instantiation

1. Point to the OSM dashboard and access the "Project > Overview > Dashboard > NS Instances > New NS" section

2. Fill the form data
   * Name of the NS
   * Nsd Id
   * Vim Account Id
   * Other configurations if needed such as SSH Key

3. Click on "Create" and wait for the NS to run

## Configuration

1. Access "Project > Overview > NS Instances > *proxytls running instance* > Actions > Exec NS Primitive", write the `set-policies` action, write the VNF Member index and look for a change in the status for the latest request

## Testing

1. Execute the `set-policies` action from the OSM GUI.
2. Wait for the action to complete.
3. If successful, verify that the content was added to block and monitor lists.
4. Execute the `delete-policies` action from the OSM GUI.
5. Wait for the action to complete.
6. If successful, the file block and monitor lists would be empty.
