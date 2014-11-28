import ast
import docker

from etcdocker import util


class Container:
    def __init__(self, name, params):
        self.name = name
        self.params = params

    def set_or_create_param(self, key, value):
        self.params[key] = value
        print "Set param '%s' on '%s'" % (key, self.name)

    def ensure_running(self, force_restart=False):
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

        client = docker.Client()
        # Start our container
        if found:
            # Shut down old container first
            client.stop(self.name, 5)
            client.remove_container(self.name)

        # Convert params into proper types
        converted_params = {
            'ports': None,
            'volumes_from': None,
            'volumes': None}

        for param in self.params.iterkeys():
            if self.params.get(param) and param in converted_params.keys():
                converted_params[param] = ast.literal_eval(
                    self.params.get(param))

        # Create container with specified args
        client.create_container(
            image=self.params.get('image'),
            detach=True,
            volumes=converted_params.get('volumes'),
            ports=converted_params.get('ports').keys(),
            name=self.name)

        # Start 'er up
        client.start(
            container=self.name,
            port_bindings=converted_params.get('ports'),
            volumes_from=converted_params.get('volumes_from'),
            privileged=self.params.get('privileged'))
