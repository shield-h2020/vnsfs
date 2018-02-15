import subprocess

def getValIfKeyExists(dict_var, key_var):
    if key_var in dict_var:
        return dict_var[key_var]
    else:
        if key_var[-5:] == "_list":
            return []
        else:
            return None

def reload_service(name):
    command = ['/usr/sbin/service', name, 'reload'];
    #shell=FALSE for sudo to work.
    subprocess.call(command, shell=False)
