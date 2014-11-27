import etcd
from etcdocker import util


class Watcher(object):
    def __init__(self, container, key):
        self.key = key
        self.container = container
        self.param = key.rstrip('/')[-1]

    def watch(self):
        # Assuming default etcd connection settings for now
        client = etcd.Client()

        # Blocking
        for event in client.eternal_watch(self.key):
            container.set_or_create_param(self.param, event.value)
            container.ensure_running()


def __main__(*args, **kwargs):
    # Run watcher
    if not kwargs.get('key'):
        exit(2)
    watcher = Watcher(kwargs.get('key'))
    watcher.watch()
