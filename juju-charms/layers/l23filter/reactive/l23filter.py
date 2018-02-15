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
rest_ip = cfg.get("ssh-hostname")
rest_port = cfg.get("rest-port")
status_file = "l23filter_status.log"
policies_file = "policies"

@when("config.changed")
def config_changed():
    set_flag("l23filter.configured")
    status_set("active", "ready!")
    return


@when("l23filter.configured")
@when("actions.start")
def start():
    cmd = "touch ~/" + status_file + "; echo \"" + log_action("start") + "\" >> ~/" + status_file
    ssh_call("actions.start", cmd)

@when("l23filter.configured")
@when("actions.stop")
def stop():
    cmd = "touch ~/" + status_file + "; echo \"" + log_action("stop") + "\" >> ~/" + status_file
    ssh_call("actions.stop", cmd)

@when("l23filter.configured")
@when("actions.restart")
def restart():
    cmd = "touch ~/" + status_file + "; echo \"" + log_action("restart") + "\" >> ~/" + status_file
    ssh_call("actions.restart", cmd)

@when("l23filter.configured")
@when("actions.get-policies")
def get_policies():
    headers = {"Content-Type": "application/json"}
    args = [("actions.get-policies", "/getFlow/v2", "POST", headers)]
    ssh_curl_call(args)

@when("l23filter.configured")
@when("actions.set-policies")
def set_policies():
    policies = action_get("policies")
    policies = read_policies_content(policies)
    headers = {"Content-Type": "application/xml"}
    args = [("actions.set-policies", "/createFlowsXML/v2",
        "POST", headers, policies)]
    ssh_curl_call(args)

@when("l23filter.configured")
@when("actions.delete-policies")
def delete_policies():
    args = [("actions.delete-policies", "/deleteAllFlows/v2", "DELETE")]
    ssh_curl_call(args)

@when("l23filter.configured")
@when("actions.delete-policy")
def delete_policy():
    policy = action_get("policy")
    args = [("actions.delete-policy", "/deleteFlow/v2?id={}".format(policy), "DELETE")]
    ssh_curl_call(args)


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
        print("Direct content or invalid URL provided")
    # Unescape data so it can be directly sent to the vNSF
    if isinstance(contents, str):
        contents = contents.replace('\\"', '"')
        contents = contents.replace('\"', '"')
    return contents

def ssh_call(action_name, cmd):
    try:
        result, err = charms.sshproxy._run(cmd)
    except Exception as e:
        action_fail("command failed: {}, errors: {}".format(e, e.output))
    else:
        action_set({"stdout": result,
                    "errors": err})
    finally:
        remove_flag(action_name)

def ssh_curl_call(arg_list):
    for args in arg_list:
        try:
            curl_call(*args)
        except:
            pass

def curl_call(action_name, path, method, headers={}, data=""):
    try:
        import requests
        resp = None
        curl_url = "http://{}:{}{}".format(rest_ip, rest_port, path)
        request_method = getattr(requests, method.lower())
        resp = request_method(curl_url,
            headers=headers,
            data=data,
            verify=False)
        result = resp.text
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        action_fail("command failed: {}, endpoint: {}:{}, filename: {}, line: {}".format(e, rest_ip, rest_port, fname, exc_tb.tb_lineno))
    else:
        action_set({"stdout": result,
                    "errors": e})
    finally:
        remove_flag(action_name)

def log_action(action):
    now = datetime.datetime.now()
    message = "[{}] action={}".format(now.isoformat(), action)
    return message
