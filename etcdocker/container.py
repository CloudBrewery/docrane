import docker

from etcdocker import util


class Container:
    def __main__(self, name, params):
        self.name = name
        self.params = params

    def set_or_create_param(self, key, value):
        self.params[key] = value

    def ensure_running(self):
        # Ensure container is running with specified params
        containers = util.get_containers()
        found = False

        for pc in containers:
            if "/%s" % self.name in pc['Names']:
                found = True
                image = pc['Image'].split(':')
                if (pc['Status'].startswith('Up') and
                        image[0] == params['image'] and
                        image[2] == params['tag']):
                    return
                break

        client = docker.Client()
        # Start our container
        if found:
            # Shut down old container first
            client.stop(self.name, 5)
            client.remove_container(self.name)

        # Create container with specified args
        client.create_container(
            image=params.get('image'),
            detach=True,
            volumes_from=params.get('volumes_from'),
            volumes=params.get('volumes'),
            name=self.name)

        # Start 'er up
        client.start(
            container=self.name,
            port_bindings=params.get('ports'),
            privileged=params.get('privileged'))
