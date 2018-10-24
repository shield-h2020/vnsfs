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
status_file = "ids_status.log"
rule_file = "rule"

@when("config.changed")
def config_changed():
    set_flag("ids.configured")
    status_set("active", "ready!")
    return


@when("ids.configured")
@when("actions.start")
def start():
    cmd = "touch ~/" + status_file + "; echo \"" + log_action("start") + "\" >> ~/" + status_file
    ssh_call("actions.start", cmd)

@when("ids.configured")
@when("actions.stop")
def stop():
    cmd = "touch ~/" + status_file + "; echo \"" + log_action("stop") + "\" >> ~/" + status_file
    ssh_call("actions.stop", cmd)

@when("ids.configured")
@when("actions.restart")
def restart():
    cmd = "touch ~/" + status_file + "; echo \"" + log_action("restart") + "\" >> ~/" + status_file
    ssh_call("actions.restart", cmd)

@when("ids.configured")
@when("actions.get-rules")
def get_rules():
    headers = {"Content-Type": "application/json"}
    args = [("actions.get-rules", "/get_snort_rule", "POST", headers, "{\"snort_rule\":{}}")]
    ssh_curl_call(args)

@when("ids.configured")
@when("actions.set-rule")
def set_rule():
    rule = action_get("rule")
#    rule = read_rule_content(request_url)
    headers = {"Content-Type": "application/json"}
    args = [("actions.set-rule", "/register_snort_rule",
        "POST", headers, rule)]
    ssh_curl_call(args)

@when("ids.configured")
@when("actions.delete-rule")
def delete_rule():
    rule_id = action_get("rule")
    args = [("actions.delete-rule", "/delete_snort_rule?id={}".format(rule_id), "DELETE")]
    ssh_curl_call(args)

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
