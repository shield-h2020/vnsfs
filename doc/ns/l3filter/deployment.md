# Deployment

The following steps indicate how to deploy this package.

## Onboarding

Follow the standard OSM procedure to onboard the packages for both the L3Filter NS and VNF descritpros.

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
4. Access "Dashboard > Viewport Dashboard > *L3Filter running instance* > Service Primitive", select the `set-policies` action and look for a change in the status for the latest request

## Testing

1. Execute the `set-policies` action from the OSM GUI, using the
 `mspl/vnf/l3filter/sample.mspl` content.
2. Wait for the action to complete (green light).
3. If successful, verify the content of `iptables` as follows:
  1. Execute `get-policies` action and verify the `iptables` rule-set from the
     logs of the Juju proxy charm
  2. Execute `sudo iptables -L -v` locally on the vNSF instance.

The result in the second case, given the test MSPL, should be similar to the
following one:

```
Chain vnsf-forward-chain (1 references)
target     prot opt source               destination         
ACCEPT     tcp  --  10.0.0.40            anywhere             limit: avg 50/sec burst 20
REJECT     tcp  --  10.0.0.30            anywhere             tcp dpt:http-alt reject-with icmp-port-unreachable
DROP       tcp  --  10.0.0.20            anywhere             #conn src/32 > 500
REJECT     udp  --  10.0.0.10            anywhere             reject-with icmp-port-unreachable
RETURN     all  --  anywhere             anywhere         
```
