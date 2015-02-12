# docrane #

![docrane](https://raw.githubusercontent.com/CloudBrewery/docrane/master/images/logo.png)

docrane is a Docker container manager that relies on etcd to provide relevant configuration details. It watches for changes in configuration and automatically stops, removes, recreates, and starts your Docker containers.

## Installation ##

Installation is as simple as running `pip install -r requirements.txt && python setup.py install`.

## Usage ##

```
usage: docrane [-h] /etcd/path

positional arguments:
  /etcd/path  etcd key directory storing config.

optional arguments:
  -h, --help  show this help message and exit
```

## etcd Key Structure##

The etcd key directory structure is crucial to ensure that docrane can properly read configuration details for Docker.

Here is the general layout:
```
/docrane
   /container_name1
      /image
      /tag
      /ports
   /container_name2
      /image
      /tag
      /volumes
```

Since docrane uses [docker-py](http://docker-py.readthedocs.org/en/latest/) to interact with Docker, etcd value formatting should be consistent with what docker-py expects. For example, to attach a volume to a container, the following structure should be used:
```
$ etcdctl mk /docrane/mycontainer/volumes "['/mnt']"
```

Likewise, to map ports:
```
$ etcdctl mk /docrane/mycontainer/ports "{'3306': '3306'}"
```

The `/image` and `/tag` keys are used to create a combined image name in the format of image:tag. This enables you to simply change the tag when pushing a new version, rather than updating the entire image string every time.

**Note:** Using latest for your tag is not recommended.

## Issues / Feature Requests ##

Let us know if you run into any issues, or have any feature requests by using [GitHub's issue tracker](https://github.com/CloudBrewery/docrane/issues). We always welcome community feedback!
