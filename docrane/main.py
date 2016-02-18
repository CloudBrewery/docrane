import gevent
import logging
import os
import sys

from argparse import ArgumentParser

from docrane import util
from docrane.container import Container
from docrane.watcher import ContainerWatcher, ImagesWatcher


LOG = logging.getLogger("docrane")


def run(base_key_dir):
    """
    Sets up all etcd watchers to bootstrap the process.

    args:
        base_key_dir (str) - etcd path to start looking for container
                             configurations
    """
    containers = util.get_etcd_container_names(base_key_dir)
    watchers = []

    LOG.info("Containers found:")
    LOG.info(containers)

    images_watcher = ImagesWatcher()
    watchers.append(gevent.spawn(images_watcher.watch))

    for container in containers:
        container_path = os.path.join(base_key_dir, container)

        params = util.get_params(container_path)

        if not (params.get('tag') and params.get('image')):
            LOG.warning(
                'Image/tag not specified for container %s.. skipping.' % (
                    container))
            continue

        cont = Container(container, params, images_watcher)
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
    parser.add_argument('-p', '--pre_boot',
                        help='Boot container before scanning etcd')
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

    LOG.warn('---- Starting docrane ----')

    if args.pre_boot:
        LOG.warn('Pre-booting %s' % args.pre_boot)
        util.start_docker_container(args.pre_boot)

    run(key_dir)


if __name__ == '__main__':
    main()
