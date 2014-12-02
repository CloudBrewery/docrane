import logging

from gevent import sleep

from etcdocker import util


LOG = logging.get_logger()


class ContainerWatcher(object):
    def __init__(self, container, container_key):
        self.container = container
        self.container_key = container_key

    def watch(self):
        """
        Watch a container's etcd path for changes and respawn if necessary
        """
        while True:
            cur_params = util.get_params(self.container_key)

            if self.container.update_params(cur_params):
                LOG.info("Container '%s' has changed. Respawning..." % (
                    self.container.name))
                self.container.ensure_running(force_restart=True)

            sleep(30)
