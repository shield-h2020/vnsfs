# Deployment

The following steps indicate how to deploy this package.

## Onboarding

Follow the standard OSM procedure to onboard the packages for both the fl7filter NS and VNF descritpros.

## Instantiation

1. Point to the OSM dashboard and access the "Launchpad > Instantiate" section

2. Fill the form data
   * Name of the NS
   * Which VIM / DC to run the NS on (default is ORION VIM)
   * Juju agent
   * Virtual links: on the management network VLD, choose the `provider` name for the ORION VIM.

3. Click on "Launch" and wait for the NS to run

## Configuration

1. Point to the OSM dashboard and access the "Dashboard > Viewport Dashboard (on NS details) > Compute topology" section
2. Identify the MSPL (middle-level security policy) used by this package
3. Point to a running vNSFO instance for SHIELD and [send the MSPL](https://github.com/shield-h2020/nfvo/blob/master/README.md#execute-pre-defined-action-from-a-specific-vnsf)
3. Access "Dashboard > Viewport Dashboard > *fl7filter running instance* > Service Primitive", select the `set-policies` action and look for a change in the status for the latest request

## Testing

1. Execute the `set-policies` action from the OSM GUI, using the
 `mspl/vnf/fl7filter/sample.mspl` content.
2. Wait for the action to complete (green light).
3. If successful, verify the content of HTTPD and ModSecurity as follows:
# TODO
