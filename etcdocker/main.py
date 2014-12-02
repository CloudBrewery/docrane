import gevent
import logging
import os

from argparse import ArgumentParser

from etcdocker import util
from etcdocker.container import Container
from etcdocker.watcher import ContainerWatcher


LOG = logging.get_logger()


def run(base_key_dir):
    # Main agent loop
    containers = util.get_etcd_container_names(base_key_dir)
    watchers = []

    for container in containers:
        container_path = os.path.join(base_key_dir, container)

        params = util.get_params(container_path)

        if not (params.get('tag') or params.get('image')):
            LOG.warning(
                'Image/tag not specified for container %s.. skipping.' % (
                    container))

        cont = Container(container, params)
        cont.ensure_running()

        watcher = ContainerWatcher(cont, container_path)
        watchers.append(gevent.spawn(watcher.watch()))

    gevent.joinall(watchers)

    LOG.warning("All watchers quit, exiting..")
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
