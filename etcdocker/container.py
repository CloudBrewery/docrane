import ast
import docker

from etcdocker import util


class Container:
    def __init__(self, name, params):
        self.name = name
        self.params = params

    def set_or_create_param(self, key, value):
        self.params[key] = value

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

        # Convert our ports into a dict if necessary
        ports = ast.literal_eval(self.params.get('ports'))

        # Create container with specified args
        client.create_container(
            image=self.params.get('image'),
            detach=True,
            volumes_from=self.params.get('volumes_from'),
            volumes=self.params.get('volumes'),
            ports=ports.keys(),
            name=self.name)

        # Start 'er up
        client.start(
            container=self.name,
            port_bindings=ports,
            privileged=self.params.get('privileged'))
