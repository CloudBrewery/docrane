import etcd

from gevent import sleep


class Watcher(object):
    def __init__(self, container, key):
        self.key = key
        self.container = container
        self.param = key.rsplit('/')[-1]

    def watch(self):
        # Assuming default etcd connection settings for now
        client = etcd.Client()

        while True:
            cur_val = client.get(self.key).value

            if cur_val != self.container.params.get(self.param):
                print "Value for '%s' has changed on '%s'. Respawning" % (
                    self.param, self.container.name)
                self.container.set_or_create_param(self.param, cur_val)
                self.container.ensure_running(force_restart=True)

            sleep(10)


def __main__(*args, **kwargs):
    # Run watcher
    if not kwargs.get('key'):
        exit(2)
    watcher = Watcher(kwargs.get('key'))
    watcher.watch()
