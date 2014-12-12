import gevent
import logging
import os
import sys

from argparse import ArgumentParser

from etcdocker import util
from etcdocker.container import Container
from etcdocker.watcher import ContainerWatcher, ImagesWatcher


LOG = logging.getLogger("etcdocker")


def run(base_key_dir):
    # Main agent loop
    containers = util.get_etcd_container_names(base_key_dir)
    watchers = []

    LOG.info("Containers found:")
    LOG.info(containers)

    watcher = ImagesWatcher()
    watchers.append(gevent.spawn(watcher.watch))

    for container in containers:
        container_path = os.path.join(base_key_dir, container)

        params = util.get_params(container_path)

        if not (params.get('tag') and params.get('image')):
            LOG.warning(
                'Image/tag not specified for container %s.. skipping.' % (
                    container))
            continue

        cont = Container(container, params)
        cont.ensure_running()

        watcher = ContainerWatcher(cont, container_path)
        watchers.append(gevent.spawn(watcher.watch))

        LOG.info("Watching container '%s'" % container)

    gevent.joinall(watchers)

    LOG.warning("All watchers quit, exiting..")
    exit(0)


def main(*args, **kwargs):
    # Run app
    parser = ArgumentParser()

    parser.add_argument('base_dir', metavar='/etcd/path',
                        help='etcd key directory storing config.')
    parser.add_argument('-v', '--verbose', help='Enable verbose logging',
                        action="store_true")
    args = parser.parse_args()

    log_handler = logging.StreamHandler(sys.stdout)
    log_formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    log_handler.setFormatter(log_formatter)
    if args.verbose:
        LOG.setLevel(logging.INFO)
        log_handler.setLevel(logging.INFO)
    LOG.addHandler(log_handler)

    key_dir = args.base_dir

    LOG.warn('---- Starting etcdocker ----')
    run(key_dir)


if __name__ == '__main__':
    main()
