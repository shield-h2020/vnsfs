import iptc
import subprocess
from common import settings


# This method calls the init_networking.sh script, which sets up the routes and
# flushes iptables data before starting the application
def init_networking():
    subprocess.call(["init_networking", settings.wan_interface])


def init_vnsf_forward_chain():
    # sudo iptables -t nat -A POSTROUTING --out-interface eth2 -j MASQUERADE
    table = iptc.Table(iptc.Table.NAT)
    chain = iptc.Chain(table, "POSTROUTING")
    chain.flush()
    rule = iptc.Rule()
    rule.out_interface = settings.wan_interface
    target = iptc.Target(rule, "MASQUERADE")
    rule.target = target
    chain.insert_rule(rule)

    # iptables -N vnsf-forward
    table = iptc.Table(iptc.Table.FILTER)
    vnsf_forward_chain = table.create_chain(settings.vnsf_forward_chain)

    # iptables -A vnsf-forward -j RETURN
    rule = iptc.Rule()
    target = iptc.Target(rule, "RETURN")
    rule.target = target
    vnsf_forward_chain.append_rule(rule)

    # iptables -A FORWARD --in-interface eth1 -j vnsf-forward
    chain = iptc.Chain(table, "FORWARD")
    chain.flush()
    rule = iptc.Rule()
    rule.in_interface = settings.lan_interface
    target = iptc.Target(rule, settings.vnsf_forward_chain)
    rule.target = target
    chain.insert_rule(rule)

    # iptables -A FORWARD --in-interface eth1 --out-interface eth2 -j ACCEPT
    rule = iptc.Rule()
    rule.in_interface = settings.lan_interface
    rule.out_interface = settings.wan_interface
    target = iptc.Target(rule, "ACCEPT")
    rule.target = target
    chain.append_rule(rule)

    # iptables -A FORWARD --in-interface eth2 --out-interface eth1 -m state \
    #   --state ESTABLISHED, RELATED -j ACCEPT
    rule = iptc.Rule()
    rule.in_interface = settings.wan_interface
    rule.out_interface = settings.lan_interface
    match = iptc.Match(rule, "state")
    match.state = "RELATED,ESTABLISHED"
    target = iptc.Target(rule, "ACCEPT")
    rule.target = target
    rule.add_match(match)
    chain.append_rule(rule)


def run():
    init_networking()
    print '[DEBUG] vNSF networking initialised'
    init_vnsf_forward_chain()
    print '[DEBUG] vNSF forward chain ready'
