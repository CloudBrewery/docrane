import logging

from docker import errors as docker_errors

from docrane import util


LOG = logging.getLogger("docrane")


class Container(object):
    def __init__(self, name, params, images_watcher):
        self.name = name
        self.params = params
        self.docker_params = {}
        self.images_watcher = images_watcher
        self.delay = 0

    def delay_tick(self):
        """
        Apply a tick to the watcher delay.
        """
        if self.delay > 0:
            self.delay = self.delay -1

    def update_params(self, etcd_params):
        """
        Checks if container's param keys have changed and
        makes changes to container if required.

        args:
            container (obj) - Container
            etcd_params (dict) - Current params in etcd

        Returns: (bool)
            Let us know if they have changed
        """

        diff = set(etcd_params.items()) ^ set(self.params.items())

        if len(diff):
            LOG.warning("Params on %s have changed." % self.name)
            LOG.info("Old params: %s" % self.params)
            LOG.info("New params: %s" % etcd_params)
            self.params = etcd_params
            return True

        return False

    def ensure_running(self, force_restart=False):
        """
        Ensure an up to date version of the container is running

        args:
            force_restart (bool) - restart even if already up
        """
        # Ensure container is running with specified params
        containers = util.get_containers()
        found = False

        for pc in containers:
            if "/%s" % self.name in pc['Names']:
                found = True
                full_image = "%s:%s" % (
                    self.params.get('image'), self.params.get('tag'))
                cur_images = util.get_docker_similar_images(
                    pc['Image'], self.images_watcher.get_images())
                if (pc['Status'].startswith('Up') and
                        full_image in cur_images and
                        not force_restart):
                    return
                elif full_image not in cur_images:
                    LOG.warning("Image ID has changed. Restarting container.")
                break

        try:
            image_found = util.pull_image(
                self.docker_params.get('image'), self.docker_params.get('tag'))
            assert image_found
        except AssertionError:
            # The image wasn't found
            LOG.warning("Couldn't find image %s:%s. Delaying next scan.. " % (
                self.docker_params.get('image'), self.docker_params.get('tag')))
            self.delay = 4
            return

        self.delay = 0

        if found:
            # Shut down old container first
            self.stop_and_rm()
        elif not force_restart:
            LOG.warning("Container %s not running." % self.name)

        self.docker_params = util.convert_params(self.params)
        self.create()
        self.start()

    def create(self):
        # Create container with specified args
        LOG.info("Creating %s..." % self.name)
        util.create_docker_container(self.name, self.docker_params)

    def start(self):
        # Start 'er up
        LOG.warning("Starting %s..." % self.name)
        util.start_docker_container(self.name, self.docker_params)

    def stop_and_rm(self):
        # Stop and remove
        LOG.warning("Stopping %s..." % self.name)
        util.stop_and_rm_docker_container(self.name)
