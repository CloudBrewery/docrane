import ast
import docker
import etcd
import logging
from requests.exceptions import ConnectionError

from docrane.exceptions import ImageNotFoundError


LOG = logging.getLogger("docrane")


def _get_docker_client():
    # Assume docker is local
    return docker.Client()


def _get_etcd_client():
    # Assume docker is local
    return etcd.Client()


def get_containers():
    client = _get_docker_client()
    try:
        return client.containers(all=True)
    except ConnectionError:
        # If we can't connect to docker, log and return
        LOG.error("Unable to connect to docker. Skipping...")
        return


def get_container_names(containers):
    # Returns list of container names from etcd key list
    container_names = []
    for container in containers:
        container_names.append(container['key'].rsplit('/')[-1])

    return container_names


def get_etcd_container_names(base_key_dir):
    """
    Get container name list from etcd

    args:
        base_key_dir (str) - etcd path for docrane

    Returns: (list)
        List of container names
    """
    # Returns list of container names from etcd key list
    client = _get_etcd_client()
    # Get container key list
    containers = get_container_names(client.read(
        base_key_dir, recursive=True, sorted=True)._children)

    return containers


def get_params(container_path):
    """
    Get params for container from etcd

    args:
        container_path (str) - etcd path to container params

    Returns: (dict)
        Raw etcd params
    """
    client = _get_etcd_client()
    try:
        children = client.read(container_path)._children
    except KeyError:
        LOG.error("Missing etcd path %s" % container_path)
        return False

    params = {}

    for child in children:
        name = child['key'].rsplit('/')[-1]
        params[name] = child['value']

    return params


def _convert_ports(tcp_ports, udp_ports):
    """
    Make ports compat for both hostconfig and create

    args:
        params (dict) - ports to convert

    Returns: (list)
        Converted ports for create and hostconfig resepctively
    """
    try:
        create_ports = tcp_ports.keys()
    except AttributeError:
        return [], {}
    config_ports = tcp_ports

    if udp_ports:
        for hostport, contport in udp_ports.iteritems():
            create_ports.append((hostport, 'udp'))
            config_ports["%s/udp" % hostport] = contport

    return create_ports, config_ports


def convert_params(params):
    """
    Converts etcd params to docker params

    args:
        params (dict) - raw etcd key value pairs

    Returns: (dict)
        Converted docker params
    """
    c_params = {
        'ports': None,
        'udp_ports': None,
        'volumes_from': None,
        'volume_bindings': None,
        'volumes': None,
        'environment': None,
        'command': None,
        'links': None,
        'log_config': None,
        'networking_config': None}

    for param in params.iterkeys():
        if params.get(param) and param in c_params.keys():
            try:
                c_params[param] = ast.literal_eval(
                    params.get(param))
            except (ValueError, SyntaxError):
                LOG.error("Possible malformed param '%s'." % param)
                c_params[param] = params.get(param)
        else:
            if params.get(param) in ('True', 'true'):
                c_params[param] = True
            elif params.get(param) in ('False', 'false'):
                c_params[param] = False
            else:
                c_params[param] = params.get(param)

    c_params['image'] = "%s:%s" % (
        params.get('image'), params.get('tag'))

    (c_params['create_ports'], c_params['config_ports']) = _convert_ports(
        c_params.get('ports'), c_params.get('udp_ports'))

    return c_params


def create_docker_container(name, params):
    """
    Create a Docker container

    args:
        name (str) - Name of container
        params (dict) - Docker params

    Returns: (bool)
        Whether or not create was successful
    """
    client = _get_docker_client()

    LOG.info("Creating with params: %s" % params)

    hostconfig = client.create_host_config(
        port_bindings=params.get('config_ports'),
        volumes_from=params.get('volumes_from'),
        binds=params.get('volume_bindings', {}),
        links=params.get('links'),
        mem_limit=params.get('mem_limit'),
        privileged=params.get('privileged'),
        log_config=params.get('log_config'))

    try:
        client.create_container(
            image=params.get('image'),
            detach=True,
            volumes=params.get('volumes'),
            ports=params.get('create_ports'),
            environment=params.get('environment'),
            command=params.get('command'),
            hostname=params.get('hostname'),
            cpu_shares=params.get('cpu_shares'),
            networking_config=params.get('networking_config'),
            host_config=hostconfig,
            name=name)
        return True
    except docker.errors.APIError as e:
        LOG.error("Error creating container %s. (%s)\n\rContinuing..." % (
            name, e.message))

    return False


def start_docker_container(name):
    """
    Start a Docker container

    args:
        name (str) - Name of container
    """
    client = _get_docker_client()
    try:
        client.start(container=name)
    except docker.errors.APIError as e:
        LOG.error("Error starting container %s. (%s)\n\rContinuing..." % (
            name, e.message))


def stop_and_rm_docker_container(name):
    """
    Stop and remove a Docker container

    args:
        name (str) - Name of container
    """
    client = _get_docker_client()
    # Try to stop the container, kill after 5 secs
    client.stop(name, 5)
    client.remove_container(name)


def get_docker_images(filter=None):
    """
    Get a list of images

    args:
        filter (str) - Filter string

    Returns: (list)
        List of image IDs, optionally filtered
    """
    client = _get_docker_client()

    try:
        return client.images(name=filter)
    except ConnectionError:
        # If we can't connect to docker, log and return
        LOG.error("Unable to connect to docker. Skipping...")
        return


def get_docker_similar_images(image_name, images):
    """
    Get a list of image names that are the same

    args:
        image_name (str) - Latest image

    Returns: (list)
        List of image names
    """
    cur_image_id = None
    cur_images = []

    for i in images:
        for tag in i.get('RepoTags'):
            if tag == image_name:
                cur_image_id = i.get('Id')

    for i in images:
        if i.get('Id') == cur_image_id:
            for tag in i.get('RepoTags'):
                cur_images.append(tag)

    return cur_images


def pull_image(image, tag):
    """
    Pull an image down from repo

    args:
        image (str) - Image name
        tag (str) - Image tag
    """
    client = _get_docker_client()
    # TODO: Should have a setting for allowing insecure registries. Could be
    # insecure / not desired.
    LOG.info("Pulling %s:%s..." % (image, tag))
    image_found = client.pull(image, tag, insecure_registry=True).find("error")

    if image_found > -1:
        raise ImageNotFoundError(image, tag)
