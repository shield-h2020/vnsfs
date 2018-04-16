import urllib
import urllib2
import subprocess
from iptables import iptables_wrapper
from iptables import mspl_translator



def get_rules(handler):
    try:
		#result = iptables_wrapper.get_iptables_rules()
		result = None
		return result
    except Exception as e:
        print e
        return False
		# return subprocess.check_output(["sudo", "iptables", "-L"])


def set_rules(handler):
    try:
		payload = handler.get_payload()
		result = None
		#rules = mspl_translator.xml_to_iptables(payload)
		#result = iptables_wrapper.set_iptables_rules(rules)
		
		# write payload to mspl.xml file
		file = open("/home/centos/utils/fl7filter_mspltranslator/mspl.xml", 'w')
		file.write(payload)
		file.close()
		
		# execute configuration installation
		result = subprocess.check_output(["sudo", "/home/centos/utils/fl7filter_mspltranslator/mspl_install_conf.sh"])
		return result
    except Exception as e:
		print e
		return False


def flush_rule(handler):
    rule_id = int(urllib.unquote(handler.path[14:]))
    try:
		result = None
        #result = iptables_wrapper.delete_iptables_rule_by_id(rule_id)
		return result
    except Exception as e:
        print e
        return False


def flush_rules(handler):
    try:
		result = None
        #result = iptables_wrapper.flush_iptables_rules()
		# execute configuration restore
		result = subprocess.check_output(["sudo", "/home/centos/utils/fl7filter_mspltranslator/reset_conf.sh"])
		return result
    except Exception as e:
        print e
        return False
