import urllib
import urllib2
from iptables import iptables_wrapper
from iptables import mspl_translator


def get_rules(handler):
    try:
        result = iptables_wrapper.get_iptables_rules()
        return result
    except Exception as e:
        print e
        return False
    # return subprocess.check_output(["sudo", "iptables", "-L"])


def set_rules(handler):
    try:
        payload = handler.get_payload()
        rules = mspl_translator.xml_to_iptables(payload)
        result = iptables_wrapper.set_iptables_rules(rules)
        return result
    except Exception as e:
        print e
        return False


def flush_rule(handler):
    rule_id = int(urllib.unquote(handler.path[14:]))
    try:
        result = iptables_wrapper.delete_iptables_rule_by_id(rule_id)
        return result
    except Exception as e:
        print e
        return False


def flush_rules(handler):
    try:
        result = iptables_wrapper.flush_iptables_rules()
        return result
    except Exception as e:
        print e
        return False
