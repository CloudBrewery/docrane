import gevent
import os

from argparse import ArgumentParser

from etcdocker import util
from etcdocker.container import Container
from etcdocker.watcher import ContainerWatcher


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

        if not (params.get('tag') or params.get('image')):
            print 'Image/tag not specified for container %s.. skipping.' % (
                container)

        cont = Container(container, params)
        cont.ensure_running()

        watcher = ContainerWatcher(cont, container_path)
        watchers.append(gevent.spawn(watcher))

    gevent.joinall(watchers)

    print "All watchers quit, exiting.."
    exit(0)


def main(*args, **kwargs):
    # Run app
    parser = ArgumentParser()

    parser.add_argument('base_dir', metavar='/etcd/path',
                        help='etcd key directory storing config.')
    args = parser.parse_args()
    key_dir = args.base_dir

    run(key_dir)


if __name__ == '__main__':
    main()
