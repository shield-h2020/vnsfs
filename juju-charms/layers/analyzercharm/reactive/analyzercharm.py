#@when_not('analyzercharm.installed')
#def install_analyzercharm():
    # Do your setup here.
    #
    # If your charm has other dependencies before it can install,
    # add those as @when() clauses above., or as additional @when()
    # decorated handlers below
    #
    # See the following for information about reactive charms:
    #
    #  * https://jujucharms.com/docs/devel/developer-getting-started
    #  * https://github.com/juju-solutions/layer-basic#overview
    #
#    set_flag('analyzercharm.installed')

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
#rest_api_port = 8080
#rest_api_hostname = "0.0.0.0"
#rest_api_port = cfg.get("rest-api-port")
#status_file = "analyzercharm_status.log"


@when_not('analyzercharm.configured')
def not_configured():
    """Check the current configuration.

    Check the current values in config to see if we have enough
    information to continue.
    """
    config_changed()


@when('config.changed')
@when_not('analyzercharm.configured')
def invalid_credentials():
    status_set('blocked','Waiting for SSH credentials.')
    pass


@when('config.changed','analyzercharm.configured')
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

#        run_api()
        set_flag("analyzercharm.configured")
        status_set("active","ready!")

        return
    except Exception as err:
        status_set(
            'blocked',
            'Waiting for valid configuration ({})'.
            format(err))


#def run_api():
#    try:
#        log("Starting API")
#        cmd = "sudo systemctl start restful.service"
#        result, err = charms.sshproxy._run(cmd)
#        log("API started")
#    except:
#        action_fail("command failed:" + err)


#"python3 /home/cognet/restful.py &"
#"sudo fuser -k 8080/tcp"


@when('analyzercharm.configured')
@when("actions.start-softflowd")
def start_softflowd():
    cmd = "sudo /etc/init.d/softflowd start"
    print("start: " + cmd)
    ssh_call("actions.start-softflowd", cmd)
    log("Softflowd started")


@when('analyzercharm.configured')
@when("actions.stop-softflowd")
def stop_softflowd():
    cmd = "sudo /etc/init.d/softflowd stop"
    print("stop: " + cmd)
    ssh_call("actions.stop-softflowd", cmd)
    log("Softflowd stopped")


@when('analyzercharm.configured')
@when("actions.restart-softflowd")
def restart_softflowd():
    cmd = "sudo /etc/init.d/softflowd restart"
    print("restart: " + cmd)
    ssh_call("actions.restart-softflowd", cmd)
    log("Softflowd restarted")


@when('analyzercharm.configured')
@when("actions.start-analyzer")
def start_analyzer():
    cmd = "sudo systemctl start netflow-SHIELD.service"
    print("start: " + cmd)
    ssh_call("actions.start-analyzer", cmd)
    log("Analyzer started")


@when('analyzercharm.configured')
@when("actions.stop-analyzer")
def stop_analyzer():
    cmd = "sudo systemctl stop netflow-SHIELD.service"
    print("stop: " + cmd)
    ssh_call("actions.stop-analyzer", cmd)
    log("Analyzer stopped")


@when('analyzercharm.configured')
@when("actions.restart-analyzer")
def restart_analyzer():
    cmd = "sudo systemctl restart netflow-SHIELD.service"
    print("restart: " + cmd)
    ssh_call("actions.restart-analyzer", cmd)
    log("Analyzer restarted")


@when('analyzercharm.configured')
@when("actions.forensic-mode")
def forensic_mode():
    cmd = "sudo bash /home/cognet/modify-SHIELD.sh MODE forensic"
    log(cmd)
    ssh_call("actions.forensic-mode", cmd)
    cmd = "sudo systemctl restart netflow-SHIELD.service"
    log(cmd)
    ssh_call("actions.forensic-mode", cmd)
    log("Changed tstat to forensic mode")


@when('analyzercharm.configured')
@when("actions.realtime-mode")
def realtime_mode():
    cmd = "sudo bash /home/cognet/modify-SHIELD.sh MODE realtime"
    log(cmd)
    ssh_call("actions.realtime-mode", cmd)
    cmd = "sudo systemctl restart netflow-SHIELD.service"
    log(cmd)
    ssh_call("actions.realtime-mode", cmd)
    log("Changed tstat to realtime mode")


@when('analyzercharm.configured')
@when("actions.change-network")
def change_network():
    network = action_get("network")
    cmd = "sudo bash /home/cognet/modify-SHIELD.sh NETWORK " + network
    log(cmd)
    ssh_call("actions.change-network", cmd)
    cmd = "sudo systemctl restart netflow-SHIELD.service"
    log(cmd)
    ssh_call("actions.change-network", cmd)
    log("Changed the path where the trained network in tstat")


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
