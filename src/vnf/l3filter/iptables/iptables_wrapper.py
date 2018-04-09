import iptc
import json
from common import settings


# The rules should be applied to the vnsf-forward chain of the FILTER table
def get_vnsf_forward_chain():
    table = iptc.Table(iptc.Table.FILTER)
    table.refresh()
    chain = iptc.Chain(table, settings.vnsf_forward_chain)
    return chain


def get_rule_dict(rule):
    rule_matches = rule.matches
    matches = {}
    for j in range(len(rule_matches)):
        matches[rule_matches[j].name] = {
            "sport": rule_matches[j].sport,
            "dport": rule_matches[j].dport
        }
    json_rule = {
        "src": rule.src,
        "dst": rule.dst,
        "protocol": rule.protocol,
        "matches": matches,
        "target": rule.target.standard_target
    }
    return json_rule


def get_iptables_rules():
    chain = get_vnsf_forward_chain()
    iptables_rules = chain.rules
    rules = {}
    # Exclude RETURN target rule
    for i in range(len(iptables_rules) - 1):
        rules[i] = get_rule_dict(iptables_rules[i])
    return json.dumps(rules)


def set_iptables_rules(rules):
    chain = get_vnsf_forward_chain()
    for rule in rules:
        chain.insert_rule(rule)
    return len(rules)


def append_iptables_rules(rules):
    chain = get_vnsf_forward_chain()
    for rule in rules:
        chain.append_rule(rule)
    return len(rules)


def delete_iptables_rule_by_id(rule_id):
    chain = get_vnsf_forward_chain()
    # If the rule is the RETURN target, do not delete it
    if(rule_id == (len(chain.rules) - 1)):
        return False
    rule = chain.rules[rule_id]
    rule_dict = get_rule_dict(rule)
    chain.delete_rule(rule)
    return json.dumps(rule_dict)


def flush_iptables_rules():
    chain = get_vnsf_forward_chain()
    chain.flush()
    # Re-add the RETURN target rule
    rule = iptc.Rule()
    target = iptc.Target(rule, "RETURN")
    rule.target = target
    chain.append_rule(rule)
    return True
