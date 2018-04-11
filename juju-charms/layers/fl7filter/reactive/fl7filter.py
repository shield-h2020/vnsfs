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
    when_not
)
import charms.sshproxy
import datetime
from subprocess import (
    Popen,
    CalledProcessError,
    PIPE,
)

cfg = config()
rest_api_hostname = cfg.get("ssh-hostname")
rest_api_port = cfg.get("rest-api-port")
status_file = "fl7filter_status.log"


@when_not('fl7filter.configured')
def not_configured():
    """Check the current configuration.

    Check the current values in config to see if we have enough
    information to continue.
    """
    config_changed()


@when('config.changed')
def config_changed():
    try:
        status_set('maintenance', 'Verifying configuration data...')

        (validated, output) = charms.sshproxy.verify_ssh_credentials()
        if not validated:
            status_set(
                'blocked',
                'Unable to verify SSH credentials: {}'.
                format(output))
            return

        set_flag("fl7filter.configured")
        status_set("active", "ready!")

        return
    except Exception as err:
        status_set(
            'blocked',
            'Waiting for valid configuration ({})'.
            format(err))


@when('config.changed')
@when_not('sshproxy.configured')
def invalid_credentials():
    status_set('blocked', 'Waiting for SSH credentials.')
    pass


@when('fl7filter.configured')
@when('actions.start')
def start():
    cmd = "sudo PATH=$PATH XTABLES_LIBDIR=/usr/lib64/xtables/ \
        nohup utils/run.py >/dev/null 2>&1 & \
        while ! timeout 1 bash -c 'echo > /dev/tcp/localhost/" + rest_api_port\
        + "'; do sleep 1; done ; touch ~/" + status_file \
        + "; echo '" + log_action("start") + "' >> ~/" + status_file
    print("start: " + cmd)
    ssh_call("actions.start", cmd)


@when("fl7filter.configured")
@when("actions.stop")
def stop():
    cmd = "touch ~/" + status_file + "; echo \"" + log_action("stop") \
            + "\" >> ~/" + status_file \
            + "; sudo kill $( sudo lsof -i:" + rest_api_port + " -t )"
    print("stop: " + cmd)
    ssh_call("actions.stop", cmd)


@when("fl7filter.configured")
@when("actions.restart")
def restart():
    cmd = "touch ~/" + status_file + "; echo \"" + log_action("restart") \
            + "\" >> ~/" + status_file \
            + "; sudo kill $( sudo lsof -i:" + rest_api_port + " -t )" \
            + "; sudo PATH=$PATH XTABLES_LIBDIR=/usr/lib64/xtables/ \
            nohup utils/run.py >/dev/null 2>&1 & \
            while ! timeout 1 bash -c 'echo > /dev/tcp/localhost/" \
            + rest_api_port\
            + "'; do sleep 1; done"
    print("restart: " + cmd)
    ssh_call("actions.restart", cmd)


@when("fl7filter.configured")
@when("actions.get-policies")
def get_policies():
    headers = {"Content-Type": "application/json"}
    args = [("actions.get-policies", "/getRules/v1", "GET", headers)]
    ssh_curl_call(args)


@when("fl7filter.configured")
@when("actions.set-policies")
def set_policies():
    policies = action_get("policies")
    policies_xml = read_policies_content(policies)
    headers = {"Content-Type": "application/xml"}
    args = [("actions.set-policies", "/setRules/v1",
            "POST", headers, policies_xml)]
    ssh_curl_call(args)


@when("fl7filter.configured")
@when("actions.delete-policies")
def delete_policies():
    args = [("actions.delete-policies", "/flushRules/v1", "DELETE")]
    ssh_curl_call(args)


@when("fl7filter.configured")
@when("actions.delete-policy")
def delete_policy():
    policy = action_get("policy")
    args = [("actions.delete-policy", "/flushRule/v1/{}".format(policy),
            "DELETE")]
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
        print("read_policies_content: direct content or invalid URL provided")
    # Unescape data so it can be directly sent to the vNSF
    if isinstance(contents, str):
        contents = contents.replace('\\"', '"')
        contents = contents.replace('\"', '"')
    return contents


def ssh_call(action_name, cmd):
    try:
        result, err = charms.sshproxy._run(cmd)
    except Exception as e:
        print("ssh_call: " + e.output)
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
        except Exception as e:
            action_set({"stdout": e.output})


def curl_call(action_name, path, method, headers={}, data=""):
    print("curl_call: start")
    try:
        import requests
        resp = None
        curl_url = "http://{}:{}{}".format(
                rest_api_hostname,
                rest_api_port,
                path)
        print("curl_call: URL is " + curl_url + " and method is " + method)
        request_method = getattr(requests, method.lower())
        resp = request_method(
                curl_url,
                headers=headers,
                data=data,
                verify=False)
        result = resp.text
        print("curl_call: result " + result)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        action_fail("command failed: {}, endpoint: {}:{}, filename: {}, \
                line: {}".format(e,
                    rest_ip,
                    rest_port,
                    fname,
                    exc_tb.tb_lineno))
    else:
        action_set({"stdout": result})
    finally:
        remove_flag(action_name)


def log_action(action):
    now = datetime.datetime.now()
    message = "[{}] action={}".format(now.isoformat(), action)
    return message
