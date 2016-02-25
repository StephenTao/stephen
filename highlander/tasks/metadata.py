import os
import sys

from taskflow import engines
from taskflow import task
from taskflow.patterns import linear_flow as lf
from taskflow.types import futures

POSSIBLE_TOPDIR = os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir, os.pardir, os.pardir))

if os.path.exists(os.path.join(POSSIBLE_TOPDIR, 'highlander', '__init__.py')):
    sys.path.insert(0, POSSIBLE_TOPDIR)


class CreateMetaData(task.Task):
    def __init__(self, name):
        super(CreateMetaData, self).__init__(provides='metadata', name=name)

    def revert(self, result, flow_failures, **kwargs):
        if result:
            print 'meta data reverting'

    default_provides = 'metadata'

    def execute(self, *args, **kwargs):
        print 'Creating metadata'
        return 'metadata'


class CreateServer(task.Task):
    def __init__(self, name):
        super(CreateServer, self).__init__(provides='server', name=name)

    def execute(self, metadata, **kwargs):
        if metadata:
            print metadata
            print "Creating instance"


def create_flow():
    flow = lf.Flow("resilience_group").add(CreateMetaData("create_metadtata"),
                                           lf.Flow("create_server").add(CreateServer("create server"))
                                           )
    return flow


def main():
    executor = futures.GreenThreadPoolExecutor(5)
    engine = engines.load_from_factory(create_flow, engine='parallel', executor=executor)
    engine.run()


if __name__ == '__main__':
    main()
