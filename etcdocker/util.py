import docker


def get_containers():
    # Assume docker is local
    client = docker.Client()
    return client.containers(all=True)
