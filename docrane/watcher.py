import logging

from gevent import sleep

from docrane import util


LOG = logging.getLogger("docrane")


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

            if not cur_params:
                # Don't do anything if we don't have params from etcd
                pass
            elif self.container.update_params(cur_params):
                LOG.info("Container '%s' has changed. Respawning..." % (
                    self.container.name))
                self.container.ensure_running(force_restart=True)
            else:
                self.container.ensure_running()

            sleep(5)


class ImagesWatcher(object):
    images = []

    def __init__(self):
        # Make sure to pre-populate so we always have images
        self.images = util.get_docker_images()

    def watch(self):
        """
        Update image list every so often
        """
        while True:
            images = util.get_docker_images()
            if images is not None:
                self.images = images

            sleep(5)

    def get_images(self):
        """
        Return list of images
        """
        return self.images
