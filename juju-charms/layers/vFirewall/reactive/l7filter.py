from charmhelpers.core.hookenv import (
    action_get,
    action_fail,
    action_set,
    config,
    status_set,
)

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
    policies = read_policies_content(action_get('policies'))
    curl_call("actions.set-policies", "/createFlowsXML", "POST", str(policies))

@when("l7filter.configured")
@when("actions.get-policies")
def get_policies():
    curl_call("actions.get-policies", "/getFlow", "GET", None)

@when("l7filter.configured")
@when("actions.delete-policy")
def delete_policy():
    flow_id = action_get("policy")
    curl_call("actions.delete-policy", "/deleteFlow?id=<%flow_id%>", "DELETE", str(flow_id))

@when("l7filter.configured")
@when("actions.delete-policies")
def delete_policies():
    curl_call("actions.delete-policies", "/deleteAllFlows", "DELETE", None)


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

def curl_call(action_name, path, method, data=None):
    try:
        cmd = format_curl(path, method, data)

        result, err = charms.sshproxy._run(cmd)
    except Exception as e:
        action_fail("command failed: {}, errors: {}, endpoint: {}:{}".format(e, e.output, rest_ip, rest_port))
    else:
        action_set({"stdout": result,
                    "errors": err})
    finally:
        remove_flag(action_name)

def format_curl(path, method, data=None):
    """ A utility function to build the curl command line. """
    cmd = ["curl", "-k", "-i"]

    if method == "GET":
        cmd += ["-H", "\"Content-Type: application/json\""]
    elif method == "POST" and data:
        cmd += ["-H", "\"Content-Type: application/xml\""]

    cmd += ["-X", method]

    if method == "POST" and data:
        cmd += ["-d", "\"{}\"".format(data)]
    elif method == "DELETE" and data:
        path = path.replace("<%flow_id%>", data)

    cmd.append(
        "https://{}:{}{}".format(rest_ip, rest_port, path)
    )
    return cmd

def log_action(action):
    now = datetime.datetime.now()
    message = "[{}] (ip={},port={}) action={}".format(now.isoformat(), rest_ip, rest_port, action)
    return message
