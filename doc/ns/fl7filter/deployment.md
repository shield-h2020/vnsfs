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
4. Access "Dashboard > Viewport Dashboard > *fl7filter running instance* > Service Primitive", select the `set-policies` action and look for a change in the status for the latest request

## Testing

1. Execute the `set-policies` action from the OSM GUI, using the
 `mspl/vnf/fl7filter/sample.mspl` content.
2. Wait for the action to complete (green light).
3. If successful, verify the content of HTTPD and ModSecurity as follows:
   1. connect to running instance by using VNC console
   2. show the content of `/etc/httpd/conf.d/default-site.conf`, it should contain:

```
<VirtualHost *:80>
    ServerName www.example.com


  <Location /path1>
    ProxyPass http://192.168.45.90:80/public
    ProxyPassReverse http://192.168.45.90:80/public

    #SecuRuleInheritance Off
    SecRuleEngine On
    SecDefaultAction "phase:2,deny,log,status:403"

    SecRequestBodyAccess On
    SecRequestBodyLimit 1024
    SecResponseBodyAccess Off

    #SSL
    #SSLEngine SSLEngine on
    #SSLCertificateFile      SSLCertificateFile /
    #SSLCertificateKeyFile   SSLCertificateKeyFile /




  </Location>
  <Location /path2>
    ProxyPass http://192.168.45.90:80/private
    ProxyPassReverse http://192.168.45.90:80/private

    #SecuRuleInheritance Off
    SecRuleEngine On
    SecDefaultAction "phase:2,deny,log,status:400"

    SecRequestBodyAccess On
    SecRequestBodyLimit 1024
    SecResponseBodyAccess Off

    #SSL
    #SSLEngine SSLEngine on
    #SSLCertificateFile      SSLCertificateFile /
    #SSLCertificateKeyFile   SSLCertificateKeyFile /


    IncludeOptional modsecurity.d/activated_rules/modsecurity_crs_21_protocol_anomalies.conf
    IncludeOptional modsecurity.d/activated_rules/modsecurity_crs_35_bad_robots.conf
    IncludeOptional modsecurity.d/activated_rules/modsecurity_crs_45_trojans.conf
    IncludeOptional modsecurity.d/activated_rules/modsecurity_crs_40_generic_attacks.conf
    IncludeOptional modsecurity.d/activated_rules/modsecurity_crs_50_outbound.conf
    IncludeOptional modsecurity.d/activated_rules/modsecurity_crs_47_common_exceptions.conf
    IncludeOptional modsecurity.d/activated_rules/modsecurity_crs_20_protocol_violations.conf
    IncludeOptional modsecurity.d/activated_rules/modsecurity_crs_41_sql_injection_attacks.conf
    IncludeOptional modsecurity.d/activated_rules/modsecurity_crs_41_xss_attacks.conf
    IncludeOptional modsecurity.d/activated_rules/modsecurity_crs_23_request_limits.conf
    IncludeOptional modsecurity.d/activated_rules/modsecurity_crs_42_tight_security.conf


  </Location>
</VirtualHost>
```   

4. Execute the `delete-policies` action from the OSM GUI.
5. Wait for the action to complete (green light).
6. If successful, the file `/etc/httpd/conf.d/default-site.conf` (that contains HTTPD and ModSecurity configuration) must be deleted
