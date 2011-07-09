from unittest import TestCase
from threading import Thread, currentThread
from time import sleep

from zope.component import provideUtility
from zope.testing.cleanup import CleanUp

from collective.indexing.config import INDEX, REINDEX, UNINDEX
from collective.indexing.interfaces import IIndexQueue
from collective.indexing.interfaces import IIndexQueueProcessor
from collective.indexing.queue import getQueue
from collective.indexing.queue import IndexQueue
from collective.indexing.tests import utils


class QueueTests(CleanUp, TestCase):

    def setUp(self):
        self.queue = IndexQueue()

    def tearDown(self):
        self.queue.clear()

    def testInterface(self):
        self.failUnless(IIndexQueue.providedBy(self.queue))

    def testQueueHook(self):
        class CaptainHook:
            def __init__(self):
                self.hooked = 0
            def __call__(self):
                self.hooked += 1
        hook = CaptainHook()
        queue = self.queue
        queue.setHook(hook)
        self.assertEqual(hook.hooked, 0)
        queue.index('foo')
        queue.reindex('foo')
        queue.reindex('bar')
        self.assertEqual(len(queue.getState()), 3)
        self.assertEqual(hook.hooked, 3)
        self.assertEqual(queue.process(), 2)
        self.assertEqual(hook.hooked, 3)

    def testQueueState(self):
        queue = self.queue
        queue.index('foo')
        self.assertEqual(queue.getState(), [(INDEX, 'foo', None)])
        state = queue.getState()
        queue.reindex('bar')
        self.assertEqual(queue.getState(), [(INDEX, 'foo', None), (REINDEX, 'bar', None)])
        queue.setState(state)
        self.assertEqual(queue.getState(), [(INDEX, 'foo', None)])
        self.assertEqual(queue.process(), 1)

    def testQueueProcessor(self):
        queue = self.queue
        proc = utils.MockQueueProcessor()
        provideUtility(proc, IIndexQueueProcessor)
        queue.index('foo')
        self.assertEqual(queue.process(), 1)    # also do the processing...
        self.assertEqual(queue.getState(), [])
        self.assertEqual(proc.getState(), [(INDEX, 'foo', None)])
        self.assertEqual(proc.state, 'started') # the real queue won't update the state...
        queue.commit()
        self.assertEqual(proc.state, 'finished')

    def testMultipleQueueProcessors(self):
        queue = self.queue
        proc1 = utils.MockQueueProcessor()
        proc2 = utils.MockQueueProcessor()
        provideUtility(proc1, IIndexQueueProcessor, name='proc1')
        provideUtility(proc2, IIndexQueueProcessor, name='proc2')
        queue.index('foo')
        self.assertEqual(queue.process(), 1)    # also do the processing...
        self.assertEqual(queue.getState(), [])
        self.assertEqual(proc1.getState(), [(INDEX, 'foo', None)])
        self.assertEqual(proc2.getState(), [(INDEX, 'foo', None)])
        self.assertEqual(proc1.state, 'started')    # the real queue won't...
        self.assertEqual(proc2.state, 'started')    # update the state...
        queue.commit()
        self.assertEqual(proc1.state, 'finished')
        self.assertEqual(proc2.state, 'finished')

    def testQueueOperations(self):
        queue = self.queue
        proc = utils.MockQueueProcessor()
        provideUtility(proc, IIndexQueueProcessor)
        queue.index('foo')
        queue.reindex('foo')
        self.assertEqual(queue.process(), 1)
        self.assertEqual(queue.getState(), [])
        self.assertEqual(proc.getState(), [(INDEX, 'foo', None)])
        # the real queue won't update the state
        self.assertEqual(proc.state, 'started')
        queue.commit()
        self.assertEqual(proc.state, 'finished')

    def testQueueOptimization(self):
        queue = self.queue
        queue.index('foo')
        queue.reindex('foo')
        queue.unindex('foo')
        queue.index('foo', 'bar')
        queue.optimize()
        self.assertEqual(queue.getState(), [(INDEX, 'foo', None)])

    def testCustomQueueOptimization(self):
        def optimize(self):
            self.setState([op for op in self.getState() if not op[0] == UNINDEX])
        queue = self.queue
        queue.index('foo')
        queue.reindex('foo')
        queue.unindex('foo')
        queue.index('foo', 'bar')
        queue.optimize()
        self.assertEqual(queue.getState(), [(INDEX, 'foo', None)])
        queue.clear()
        # hook up the custom optimize
        orig_optimize = queue.optimize
        try:
            queue.optimize = optimize
            queue.index('foo')
            queue.reindex('foo')
            queue.unindex('foo')
            queue.index('foo', 'bar')
            queue.optimize(queue)
            self.assertEqual(queue.getState(), [(INDEX, 'foo', None), (REINDEX, 'foo', None), (INDEX, 'foo', 'bar')])
        finally:
            queue.optimize = orig_optimize

    def testQueueAbortBeforeProcessing(self):
        queue = self.queue
        proc = utils.MockQueueProcessor()
        provideUtility(proc, IIndexQueueProcessor)
        queue.index('foo')
        queue.reindex('foo')
        self.assertNotEqual(queue.getState(), [])
        queue.abort()
        self.assertEqual(queue.process(), 0)    # nothing left...
        self.assertEqual(queue.getState(), [])
        self.assertEqual(proc.getState(), [])
        self.assertEqual(proc.state, 'aborted')

    def testQueueAbortAfterProcessing(self):
        queue = self.queue
        proc = utils.MockQueueProcessor()
        provideUtility(proc, IIndexQueueProcessor)
        queue.index('foo')
        queue.reindex('foo')
        self.assertEqual(queue.process(), 1)
        self.assertNotEqual(proc.getState(), [])
        queue.abort()
        self.assertEqual(queue.getState(), [])
        self.assertEqual(proc.getState(), [])
        self.assertEqual(proc.state, 'aborted')

    def testOptimizeQueue(self):
        queue = self.queue
        queue.setState([(REINDEX, 'A', None), (REINDEX, 'A', None)])
        queue.optimize()
        self.failUnlessEqual(queue.getState(), [(REINDEX, 'A', None)])

        queue.setState([(INDEX, 'A', None), (REINDEX, 'A', None)])
        queue.optimize()
        self.failUnlessEqual(queue.getState(), [(INDEX, 'A', None)])

        queue.setState([(INDEX, 'A', None), (UNINDEX, 'A', None)])
        queue.optimize()
        self.failUnlessEqual(queue.getState(), [])

        queue.setState([(UNINDEX, 'A', None), (INDEX, 'A', None)])
        queue.optimize()
        self.failUnlessEqual(queue.getState(), [(REINDEX, 'A', None)])

    def testOptimizeQueueWithAttributes(self):
        queue = self.queue

        queue.setState([(REINDEX, 'A', None), (REINDEX, 'A', ('a', 'b'))])
        queue.optimize()
        self.failUnlessEqual(queue.getState(), [(REINDEX, 'A', None)])

        queue.setState([(REINDEX, 'A', ('a', 'b')), (REINDEX, 'A', None)])
        queue.optimize()
        self.failUnlessEqual(queue.getState(), [(REINDEX, 'A', None)])

        queue.setState([(REINDEX, 'A', ('a', 'b')), (REINDEX, 'A', ('b', 'c'))])
        queue.optimize()
        self.failUnlessEqual(queue.getState(), [(REINDEX, 'A', ('a', 'c', 'b'))])

        queue.setState([(INDEX, 'A', None), (REINDEX, 'A', None)])
        queue.optimize()
        self.failUnlessEqual(queue.getState(), [(INDEX, 'A', None)])

        queue.setState([(REINDEX, 'A', ('a', 'b')), (UNINDEX, 'A', None), (INDEX, 'A', None)])
        queue.optimize()
        self.failUnlessEqual(queue.getState(), [(REINDEX, 'A', None)])

    def testOptimizeQueueSortsByOpcode(self):
        queue = self.queue

        queue.setState([(INDEX, 'C', None), (UNINDEX, 'B', None)])
        queue.optimize()
        self.failUnlessEqual(queue.getState(),
            [(UNINDEX, 'B', None), (INDEX, 'C', None)])

        queue.setState([(REINDEX, 'A', None), (UNINDEX, 'B', None)])
        queue.optimize()
        self.failUnlessEqual(queue.getState(),
            [(UNINDEX, 'B', None), (REINDEX, 'A', None)])

        queue.setState([(REINDEX, 'A', None), (UNINDEX, 'B', None), (INDEX, 'C', None)])
        queue.optimize()
        self.failUnlessEqual(queue.getState(),
            [(UNINDEX, 'B', None), (REINDEX, 'A', None), (INDEX, 'C', None)])


class QueueThreadTests(TestCase):
    """ thread tests modeled after zope.thread doctests """

    def setUp(self):
        self.me = getQueue()
        self.failUnless(IIndexQueue.providedBy(self.me), 'non-queued indexer found')

    def tearDown(self):
        self.me.clear()

    def testLocalQueues(self):
        me = self.me                    # get the queued indexer...
        other = []
        def runner():                   # and a callable for the thread to run...
            me.reindex('bar')
            other[:] = me.getState()
        thread = Thread(target=runner)  # another thread is created...
        thread.start()                  # and started...
        while thread.isAlive():
            pass                        # wait until it's done...
        self.assertEqual(other, [(REINDEX, 'bar', None)])
        self.assertEqual(me.getState(), [])
        me.index('foo')                 # something happening on our side...
        self.assertEqual(other, [(REINDEX, 'bar', None)])
        self.assertEqual(me.getState(), [(INDEX, 'foo', None)])
        thread.join()                   # finally the threads are re-united...

    def testQueuesOnTwoThreads(self):
        me = self.me                    # get the queued indexer...
        first = []
        def runner1():                  # and callables for the first...
            me.index('foo')
            first[:] = me.getState()
        thread1 = Thread(target=runner1)
        second = []
        def runner2():                  # and second thread
            me.index('bar')
            second[:] = me.getState()
        thread2 = Thread(target=runner2)
        self.assertEqual(first, [])     # clean table before we start...
        self.assertEqual(second, [])
        self.assertEqual(me.getState(), [])
        thread1.start()                 # do stuff here...
        sleep(0.01)                     # allow thread to do work
        self.assertEqual(first, [(INDEX, 'foo', None)])
        self.assertEqual(second, [])
        self.assertEqual(me.getState(), [])
        thread2.start()                 # and there...
        sleep(0.01)                     # allow thread to do work
        self.assertEqual(first, [(INDEX, 'foo', None)])
        self.assertEqual(second, [(INDEX, 'bar', None)])
        self.assertEqual(me.getState(), [])
        thread1.join()                  # re-unite with first thread and...
        me.unindex('f00')               # let something happening on our side
        self.assertEqual(first, [(INDEX, 'foo', None)])
        self.assertEqual(second, [(INDEX, 'bar', None)])
        self.assertEqual(me.getState(), [(UNINDEX, 'f00', None)])
        thread2.join()                  # also re-unite the second and...
        me.unindex('f00')               # let something happening again...
        self.assertEqual(first, [(INDEX, 'foo', None)])
        self.assertEqual(second, [(INDEX, 'bar', None)])
        self.assertEqual(me.getState(), [(UNINDEX, 'f00', None), (UNINDEX, 'f00', None)])

    def testManyThreads(self):
        me = self.me                    # get the queued indexer...
        queues = {}                     # container for local queues
        def makeRunner(name, idx):
            def runner():
                for n in range(idx):    # index idx times
                    me.index(name)
                queues[currentThread()] = me.queue
            return runner
        threads = []
        for idx in range(99):
            threads.append(Thread(target=makeRunner('t%d' % idx, idx)))
        for thread in threads:
            thread.start()
            sleep(0.01)                 # just in case
        for thread in threads:
            thread.join()
        for idx, thread in enumerate(threads):
            tid = 't%d' % idx
            queue = queues[thread]
            names = [name for op, name, attrs in queue]
            self.assertEquals(names, [tid] * idx)
