#!/bin/bash

# restore previous configuration
sudo rm -f /etc/httpd/conf.d/default-site.conf
sudo \cp -f /etc/httpd/conf.d.old/conf.d/* /etc/httpd/conf.d/
sudo \cp -f /etc/httpd/modsecurity.d.old/modsecurity.d/* /etc/httpd/modsecurity.d/ 
sudo rm -rf /etc/httpd/conf.d.old/
sudo rm -rf /etc/httpd/modsecurity.d.old/

# restart apache
sudo service httpd restart
