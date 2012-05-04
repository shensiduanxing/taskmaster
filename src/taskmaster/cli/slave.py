"""
taskmaster.cli.slave
~~~~~~~~~~~~~~~~~~~~

:copyright: (c) 2010 DISQUS.
:license: Apache License 2.0, see LICENSE for more details.
"""

from multiprocessing.managers import BaseManager


class QueueManager(BaseManager):
    pass


def run(target, host='0.0.0.0:3050', key='taskmaster', threads=1):
    QueueManager.register('get_queue')

    host, port = host.split(':')

    m = QueueManager(address=(host, int(port)), authkey=key)
    m.connect()
    queue = m.get_queue()

    mod_path, func_name = target.split(':', 1)
    module = __import__(mod_path, {}, {}, [func_name], -1)
    callback = getattr(module, func_name)

    pool = ThreadPool(queue, size=threads)

    # TODO: how do we know if we're done?
    pool.join()
    callback(queue.get)


def main():
    import optparse
    import sys
    parser = optparse.OptionParser()
    parser.add_option("--host", dest="host", default='0.0.0.0:3050')
    parser.add_option("--key", dest="key", default='taskmaster')
    parser.add_option("--threads", dest="threads", default=1, type=int)
    # parser.add_option("--procs", dest="procs", default=1, type=int)
    (options, args) = parser.parse_args()
    if len(args) != 1:
        print 'Usage: tm-slave <callback>'
        sys.exit(1)
    sys.exit(args[0], run(**options.__dict__))

if __name__ == '__main__':
    main()
