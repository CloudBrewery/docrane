import docker
import etcd


def get_containers():
    # Assume docker is local
    client = docker.Client()
    return client.containers(all=True)


def get_params(container_path):
    client = etcd.Client()
    children = client.read(container_path)._children
    params = {}

    for child in children:
        name = child['key'].rsplit('/')[-1]
        params[name] = child['value']

    return params


def params_changed(container, params):
    """
    Checks if containers param keys have changed and
    makes changes to container if required.

    TODO: Only handles adds right now (swat30)

    args:
        container (obj) - Container
        params (dict) - New params to check

    Returns: (bool)
        Let us know if they have changed
    """
    has_changed = False

    for param, val in params.iteritems():
        # Check for new or changed params
        if (param not in container.params.keys() or
                val != container.params.get(param)):
            container.set_or_create_param(param, val)
            has_changed = True

    return has_changed
