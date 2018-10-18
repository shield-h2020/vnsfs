import xmltodict
import iptc
from common import settings


def xml_to_iptables(data):
    print "starting translation"
    print data
    xml_datas = []
    xml_rules = xmltodict.parse(
        data,
        dict_constructor=dict)["mspl-set"]["it-resource"]["configuration"]["rule"]

    if isinstance(xml_rules, list):
        for xml_rule in xml_rules:
            xml_datas.append(xml_rule)
    else:
        xml_datas.append(xml_rules)

    rate_limit = None
    rules = []

    for xml_data in xml_datas:
        print xml_data
        rule = iptc.Rule()
        match = None

        xml_src = getValIfKeyExists(
            xml_data["condition"]["packet-filter-condition"], "source-address")
        if xml_src is not None and xml_src != "*":
            rule.src = xml_src
        xml_dst = getValIfKeyExists(
            xml_data["condition"]["packet-filter-condition"],
            "destination-address")
        if xml_dst is not None and xml_dst != "*":
            rule.dst = xml_dst
        xml_proto = getValIfKeyExists(
            xml_data["condition"]["packet-filter-condition"],
            "protocol")
        if xml_proto is not None:
            rule.protocol = xml_proto

        xml_sport = getValIfKeyExists(
            xml_data["condition"]["packet-filter-condition"], "source-port")
        xml_dport = getValIfKeyExists(
            xml_data["condition"]["packet-filter-condition"],
            "destination-port")

        # Retrieve default target from MSPL
        default_target = getValIfKeyExists(xml_data, "action").upper()

        # Construct match
        # In case of packets/sec rate limit:
        if getValIfKeyExists(
                xml_data["condition"],
                "traffic-flow-condition") is not None:
            # It is a number of allowed packets or bits per unit of time
            # (seconds, minutes, hours or days).
            # -m limit --limit <rate-limit> --limit-burst <limit-burst> \
            # -j ACCEPT
            rate_limit = getValIfKeyExists(
                xml_data["condition"]["traffic-flow-condition"],
                "rate-limit")
            # The maximum number of connections per host.
            # -m connlimit --connlimit-above <max-connections> \
            # --connlimit-mask 32 -j REJECT
            max_connections = getValIfKeyExists(
                xml_data["condition"]["traffic-flow-condition"],
                "max-connections")

            if rate_limit is not None:
                match = iptc.Match(rule, "limit")
                match.limit = rate_limit
                match.limit_burst = settings.iptables_limit_burst
                if default_target is not "ACCEPT":
                    print '[WARN] Rate limit rule with target other' \
                        + 'than ACCEPT'
                    default_target = "ACCEPT"
            # In case of max connections:
            elif max_connections is not None:
                match = iptc.Match(rule, "connlimit")
                match.connlimit_above = max_connections
                match.connlimit_mask = "32"

        # If port is wildcard, remove the port matching
        if xml_sport is not None and xml_sport == '*':
            xml_sport = None
        if xml_dport is not None and xml_dport == '*':
            xml_dport = None

        # In case of specified ports:
        if xml_sport is not None or xml_dport is not None:
            if match is None:
                match = iptc.Match(rule, xml_proto.lower())
            if xml_sport is not None:
                match.sport = xml_sport
            if xml_dport is not None:
                match.dport = xml_dport

        # TODO: Manage priority
        priority = getValIfKeyExists(xml_data, "priority")

        # Set target
        target = iptc.Target(
            rule,
            default_target)
        rule.target = target

        # Set match
        if match is not None:
            rule.add_match(match)

        # Append rule
        rules.append(rule)

    return rules


def getValIfKeyExists(dict_var, key_var):
    if key_var in dict_var:
        return dict_var[key_var]
    else:
        if key_var[-5:] == "_list":
            return []
        else:
            return None
