from etcdocker import util


class Container(object):
    def __init__(self, name, params):
        self.name = name
        self.params = params
        self.docker_params = {}

    def set_or_create_param(self, key, value):
        self.params[key] = value
        print "Set param '%s' on '%s'" % (key, self.name)

    def update_params(self, params):
        """
        Checks if container's param keys have changed and
        makes changes to container if required.

        TODO: Only handles adds right now (swat30)

        args:
            container (obj) - Container
            params (dict) - New params to check

        Returns: (bool)
            Let us know if they have changed
        """
        has_changed = False

        for param, val in params.iteritems():
            # Check for new or changed params
            if (param not in self.params.keys() or
                    val != self.params.get(param)):
                self.set_or_create_param(param, val)
                has_changed = True

        return has_changed

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
                if (pc['Status'].startswith('Up') and
                        pc['Image'] == full_image and
                        not force_restart):
                    return
                break

        if found:
            # Shut down old container first
            util.stop_and_rm_docker_container(self.name)

        self.docker_params = util.convert_params(self.params)
        self.create()
        self.start()

    def create(self):
        # Create container with specified args
        util.create_docker_container(self.name, self.docker_params)

    def start(self):
        # Start 'er up
        util.start_docker_container(self.name, self.docker_params)
