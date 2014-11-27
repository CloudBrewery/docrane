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
