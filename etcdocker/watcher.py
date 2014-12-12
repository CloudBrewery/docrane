import logging

from gevent import sleep

from etcdocker import util


LOG = logging.getLogger("etcdocker")


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
            else:
                self.container.ensure_running()

            sleep(30)


class ImagesWatcher(object):
    IMAGES = []

    def __init__(self):
        # Make sure to pre-populate so we always have images
        self.IMAGES = util.get_docker_images()

    def watch(self):
        """
        Update image list every so often
        """
        while True:
            self.IMAGES = util.get_docker_images()

            sleep(120)
