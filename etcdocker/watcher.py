import etcd

from etcdocker import util
from gevent import sleep


class ContainerWatcher(object):
    def __init__(self, container, container_key):
        self.container = container
        self.container_key = container_key

    def watch(self):
        # Assuming default etcd connection settings
        client = etcd.Client()

        while True:
            cur_cont_dir = client.get(self.container_key)
            cur_params = util.get_params(cur_cont_dir)

            if util.params_changed(self.container, cur_params):
                print "Container '%s' has changed. Respawning..." % (
                    self.container.name)
                self.container.ensure_running(force_restart=True)

            sleep(30)
