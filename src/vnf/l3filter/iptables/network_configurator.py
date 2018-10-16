import iptc
import subprocess
from common import settings


# This method calls the init_networking.sh script, which sets up the bridge and
# flushes iptables data before starting the application
def init_networking():
    subprocess.call(["init_networking", settings.ingress_interface,
                    settings.egress_interface, settings.br_name])


def run():
    init_networking()
    print '[DEBUG] vNSF networking initialised'
