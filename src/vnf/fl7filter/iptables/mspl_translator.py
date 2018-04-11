import xmltodict
import iptc


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

        if getValIfKeyExists(
                xml_data["condition"],
                "traffic-flow-condition") is not None:
            rate_limit = getValIfKeyExists(
                xml_data["condition"]["traffic-flow-condition"], "rate-limit")

        rule = iptc.Rule()

        xml_src = getValIfKeyExists(
            xml_data["condition"]["packet-filter-condition"], "source-address")
        if xml_src is not None:
            rule.src = xml_src
        xml_dst = getValIfKeyExists(
            xml_data["condition"]["packet-filter-condition"],
            "destination-address")
        if xml_dst is not None:
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
        if xml_sport is not None or xml_dport is not None:
            match = iptc.Match()
            if xml_sport is not None:
                match.sport = xml_sport
            if xml_dport is not None:
                match.dport = xml_dport
            rule.add_match(match)

        # Target must exist
        target = iptc.Target(
            rule,
            getValIfKeyExists(xml_data, "action").upper())
        rule.target = target

        priority = getValIfKeyExists(xml_data, "priority")

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
