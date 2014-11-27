import os
import gevent

from etcdocker import util, Watcher


def get_container_names(containers):
    # Returns list of container names from etcd key list
    container_names = []
    for container in containers:
        container_names.append(container['key'].rsplit('/')[-1])

    return container_names


def run(base_key_dir):
    # Main agent loop
    import etcd
    client = etcd.Client()
    # Get container key list
    containers = get_container_names(client.read(
        base_key_dir, recursive=True, sorted=True)._children)
    watchers = []

    for container in containers:
        container_path = os.path.join(base_key_dir, container)

        params = util.get_params(container_path)

        for param in params.iterkeys():
            try:
                params[param] = client.read(
                    os.path.join(container_path, param)).value
            except etcd.KeyValue:
                continue

        if not (params.get('tag') or params.get('image')):
            print 'Image/tag not specified for container %s.. skipping.' % (
                container)

        cont = Container(container, params)
        cont.ensure_running()

        for param in params.iterkeys():
            key_path = os.path.join(container_path, param)
            watcher = Watcher(cont, key_path)
            watchers.append(gevent.spawn(watcher.watch))

    gevent.joinall(watchers)

    print "All watchers quit, exiting.."
    exit(0)


def __main__(*args, **kwargs):
    # Run app
    key_dir = kwargs.get('base_dir')
    if not key_dir:
        print 'Please specify a key directory with --base_dir='
        exit(1)

    run(key_dir)
