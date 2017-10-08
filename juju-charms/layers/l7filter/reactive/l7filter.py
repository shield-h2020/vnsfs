from charmhelpers.core.hookenv import (
    action_get,
    action_fail,
    action_set,
    config,
    status_set,
)
#from charmhelpers.contrib.openstack.utils import get_host_ip
from charms.reactive import (
    remove_state as remove_flag,
    set_state as set_flag,
    when,
)
import charms.sshproxy
import datetime
from subprocess import (
    Popen,
    CalledProcessError,
    PIPE,
)


cfg = config()
#host_ip = get_host_ip(unit_get("public-address"))
rest_ip = cfg.get("rest-ip", "127.0.0.1")
rest_port = cfg.get("rest-port", "8082")
status_file = "l7filter_status.log"
policies_file = "policies"

@when('config.changed')
def config_changed():
    set_flag('l7filter.configured')
    status_set('active', 'ready!')
    return


@when('l7filter.configured')
@when('actions.start')
def start():
    try:
        # Enter the command to start your service(s)
        cmd = "touch ~/" + status_file + "; echo \"" + log_action("start") + "\" >> ~/" + status_file
        result, err = charms.sshproxy._run(cmd)
    except Exception as e:
        err = "{}".format(e)
        action_fail('command failed: {}, errors: {}'.format(err, e.output))
        remove_flag('actions.start')
        return

@when('l7filter.configured')
@when('actions.stop')
def stop():
    try:
        # Enter the command to stop your service(s)
        cmd = "echo \"" + log_action("stop") + "\" >> ~/" + status_file + "; rm ~/" + status_file
        result, err = charms.sshproxy._run(cmd)
    except Exception as e:
        action_fail('command failed: {}, errors: {}'.format(e, e.output))
    else:
        action_set({'stdout': result,
                    'errors': err})
    finally:
        remove_flag('actions.stop')

@when('l7filter.configured')
@when('actions.restart')
def restart():
    try:
        # Enter the command to restart your service(s)
        cmd = "touch ~/" + status_file + "; echo \"" + log_action("restart") + "\" >> ~/" + status_file
        result, err = charms.sshproxy._run(cmd)
    except Exception as e:
        action_fail('command failed: {}, errors: {}'.format(e, e.output))
    else:
        action_set({'stdout': result,
                    'errors': err})
    finally:
        remove_flag('actions.restart')

@when("l7filter.configured")
@when("actions.set-policies")
def set_policies():
    try:
        curl_call("actions.set-policies", "/createDB", "GET")
    except:
        pass
    policies = read_policies_content(action_get('policies'))
    policies = """{}""".format(policies)
    headers = {"Content-Type": "application/xml"}
    curl_call("actions.set-policies", "/createFlowsXML/v2", 
        "POST", headers, str(policies))

@when("l7filter.configured")
@when("actions.get-policies")
def get_policies():
    headers = {"Content-Type": "application/json"}
    curl_call("actions.get-policies", "/getFlow/v2", "POST", headers)

@when("l7filter.configured")
@when("actions.delete-policy")
def delete_policy():
    policy = action_get('policy')
    curl_call("actions.delete-policy", "/deleteFlow/v2?id={}".format(policy), "DELETE")

@when("l7filter.configured")
@when("actions.delete-policies")
def delete_policies():
    curl_call("actions.delete-policies", "/deleteDB", "DELETE")


def read_policies_content(policies):
    import urllib.request
    from urllib.error import HTTPError, URLError
    contents = policies
    try:
        if not policies.startswith("http"):
            policies = "http://" + policies
        response = urllib.request.urlopen(policies)
        contents = response.read()
    except (HTTPError, URLError, ValueError) as e:
        print("No valid URL")
    return contents

def ssh_call(cmd):
    try:
        result, err = charms.sshproxy._run(cmd)
    except Exception as e:
        action_fail("command failed: {}, errors: {}".format(e, e.output))
    else:
        action_set({"stdout": result,
                    "errors": err})
    finally:
        remove_flag(action_name)

def curl_call(action_name, path, method, headers={}, data={}):
    try:
        import requests
        resp = None
        curl_url = "http://{}:{}{}".format(rest_ip, rest_port, path)
        if method == "GET":
            resp = requests.get(curl_url,
                headers=headers,
                verify=False)
        elif method == "POST":
            data = """{}""".format(data)
            resp = requests.post(curl_url,
                headers=headers,
                data=data,
                verify=False)
        elif method == "DELETE":
            resp = requests.delete(curl_url,
                headers=headers,
                verify=False)
        if resp:
            result = resp.text
    except Exception as e:
        action_fail("command failed: {}, errors: {}, endpoint: {}:{}".format(e, e.output, rest_ip, rest_port))
    else:
        action_set({"stdout": result,
                    "errors": err})
    finally:
        remove_flag(action_name)

def log_action(action):
    now = datetime.datetime.now()
    message = "[{}] (ip={},port={}) action={}".format(now.isoformat(), rest_ip, rest_port, action)
    return message
