#!/usr/bin/env python
# To run this REST server, execute the following command:
# sudo XTABLES_LIBDIR=/usr/lib64/xtables PATH=$PATH python run.py 

import sys
from rest_api import rest
from common import settings
from iptables import network_configurator

# Fix issues with decoding HTTP responses
reload(sys)
sys.setdefaultencoding('utf8')


def main(argv):
    network_configurator.run()
    rest.rest_server(settings.rest_api_port)


if __name__ == '__main__':
    main(sys.argv[1:])
