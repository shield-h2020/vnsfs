from charmhelpers.core.hookenv import (
    action_get,
    action_fail,
    action_set,
    status_set,
    config,
    log
)

from charms.reactive import (
    remove_state as remove_flag,
    set_state as set_flag,
    when,
    when_not
)

import charms.sshproxy
import datetime
import os
import sys

# from subprocess import (
#     Popen,
#     CalledProcessError,
#     PIPE,
# )

cfg = config()
rest_api_hostname = cfg.get("ssh-hostname")
rest_api_port = 8080
#rest_api_hostname = "0.0.0.0"
#rest_api_port = cfg.get("rest-api-port")
#status_file = "proxycharm_status.log"


@when_not('proxycharm.configured')
def not_configured():
    """Check the current configuration.

    Check the current values in config to see if we have enough
    information to continue.
    """
    config_changed()


@when('config.changed')
@when_not('sshproxy.configured')
def invalid_credentials():
    status_set('blocked','Waiting for SSH credentials.')
    pass


@when('config.changed','sshproxy.configured')
def config_changed():
    try:
        status_set('maintenance','Verifying configuration data...')

        (validated, output) = charms.sshproxy.verify_ssh_credentials()
        if not validated:
            status_set(
                'blocked',
                'Unable to verify SSH credentials: {}'.
                format(output))
            return

        run_api()
        set_flag("proxycharm.configured")
        status_set("active","ready!")

        return
    except Exception as err:
        status_set(
            'blocked',
            'Waiting for valid configuration ({})'.
            format(err))


def run_api():
    try:
        log("Starting API")
        cmd = "sudo systemctl start restful.service"
        result, err = charms.sshproxy._run(cmd)
        log("API started")
    except:
        action_fail("command failed:" + err)


#"python3 /home/vnsf-proxy/secured-psa-reencrypt/PSA/scripts/restful.py &"
#"sudo fuser -k 8080/tcp"


@when('proxycharm.configured')
@when('actions.start')
def start():
    cmd = "sudo systemctl start restful.service"
    print("start: " + cmd)
    ssh_call("actions.start", cmd)
    log("Proxy started")


@when("proxycharm.configured")
@when("actions.stop")
def stop():
    cmd = "sudo systemctl stop restful.service"
    print("stop: " + cmd)
    ssh_call("actions.stop", cmd)
    log("Proxy stopped")


@when("proxycharm.configured")
@when("actions.restart")
def restart():
    cmd = "sudo systemctl restart restful.service"
    print("restart: " + cmd)
    ssh_call("actions.restart", cmd)
    log("Proxy restarted")


@when("proxycharm.configured")
@when("actions.start-proxy")
def start_proxy():
    args = [("actions.start-proxy","/start","GET")]
    ssh_curl_call(args)


@when("proxycharm.configured")
@when("actions.stop-proxy")
def stop_proxy():
    args = [("actions.stop-proxy","/stop","GET")]
    ssh_curl_call(args)


@when("proxycharm.configured")
@when("actions.restart-proxy")
def restart_proxy():
    args = [("actions.restart-proxy","/restart","GET")]
    ssh_curl_call(args)


@when("proxycharm.configured")
@when("actions.start-collector")
def start_collector():
    cmd = "sudo systemctl start collector.service"
    print("start: " + cmd)
    ssh_call("actions.start-collector", cmd)
    log("Collector started")


@when("proxycharm.configured")
@when("actions.stop-collector")
def stop_collector():
    cmd = "sudo systemctl stop collector.service"
    print("stop: " + cmd)
    ssh_call("actions.stop-collector", cmd)
    log("Collector stopped")


@when("proxycharm.configured")
@when("actions.restart-collector")
def restart_collector():
    cmd = "sudo systemctl restart collector.service"
    print("restart: " + cmd)
    ssh_call("actions.restart-collector", cmd)
    log("Collector restarted")


@when("proxycharm.configured")
@when("actions.get-policies")
def get_policies():
    args = [("actions.get-policies","/get-policies","GET")]
    ssh_curl_call(args)


@when("proxycharm.configured")
@when("actions.set-policies")
def set_policies():
    policies = action_get("policies")
    #policies_xml = read_policies_content(policies)
    headers = {"Content-Type":"text/plain"}
    args = [("actions.set-policies","/set-policies","POST",headers,policies)]
    ssh_curl_call(args)


@when("proxycharm.configured")
@when("actions.delete-policies")
def delete_policies():
    args = [("actions.delete-policies","/delete-policies","GET")]
    ssh_curl_call(args)


@when("proxycharm.configured")
@when("actions.delete-policy")
def delete_policy():
    policy = action_get("policy")
    #policies_xml = read_policies_content(policy)
    headers = {"Content-Type":"text/plain"}
    args = [("actions.delete-policy", "/delete-policy","POST",headers,policy)]
    ssh_curl_call(args)


@when("proxycharm.configured")
@when("actions.add-url")
def add_url():
    url = action_get("url")
    #urls_xml = read_policies_content(url)
    headers = {"Content-Type":"text/plain"}
    args = [("actions.add-url", "/add-url","POST",headers,url)]
    ssh_curl_call(args)


@when("proxycharm.configured")
@when("actions.delete-url")
def delete_url():
    url = action_get("url")
    #urls_xml = read_policies_content(url)
    headers = {"Content-Type":"text/plain"}
    args = [("actions.delete-url", "/delete-url","POST",headers,url)]
    ssh_curl_call(args)


#def read_policies_content(policies):
#    import urllib.request
#    from urllib.error import HTTPError, URLError
#    contents = policies
#    try:
#        if not policies.startswith("http"):
#            policies = "http://" + policies
#        response = urllib.request.urlopen(policies)
#        contents = response.read()
#    except (HTTPError, URLError, ValueError):
#        print("read_policies_content: direct content or invalid URL provided")
#    # Unescape data so it can be directly sent to the vNSF
#    if isinstance(contents, str):
#        contents = contents.replace('\\"', '"')
#        contents = contents.replace('\"', '"')
#    return contents


def ssh_call(action_name, cmd):
    try:
        result, err = charms.sshproxy._run(cmd)
    except Exception as e:
        log("ssh_call: " + str(e))
        action_fail("command failed: {}, errors: {}".format(e, str(e)))
    else:
        action_set({"stdout": result,
                    "errors": err})
    finally:
        remove_flag(action_name)


def ssh_curl_call(arg_list):
    for args in arg_list:
        try:
            curl_call(*args)
        except Exception as e:
            action_set({"stdout": str(e)})


def curl_call(action_name, path, method, headers={}, data=""):
    #log("curl_call: start")
    try:
        import requests
        resp = None
        curl_url = "http://{}:{}{}".format(
                rest_api_hostname,
                rest_api_port,
                path)
        log("curl_call: URL is " + curl_url + " and method is " + method)
        request_method = getattr(requests, method.lower())
        resp = request_method(
                curl_url,
                headers=headers,
                data=data,
                verify=False)
        result = resp.text
        log("curl_call: result " + result)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        action_fail("command failed: {}, endpoint: {}:{}, filename: {}, \
                line: {}".format(e,
                    rest_api_hostname,
                    rest_api_port,
                    fname,
                    exc_tb.tb_lineno))
    else:
        action_set({"stdout": result})
    finally:
        remove_flag(action_name)


#def log_action(action):
#    now = datetime.datetime.now()
#    message = "[{}] action={}".format(now.isoformat(), action)
#    return message
