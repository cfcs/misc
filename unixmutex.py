#!/usr/bin/env python3
import socket
from socket import AF_UNIX, SOCK_STREAM, SOL_SOCKET, SO_RCVBUF, SO_SNDBUF
from time import sleep
import asyncio

times = {
    'wait_for_lock': 0.01,
}

class UnixSocketLock():
    '''Inter-process Mutex implemented by exploiting
    exclusive binding of Abstract Unix Sockets.

    The lock is released on unlock() or if the lock holding process crashes.
    Potentially interesting features:
    - Does not require shared memory, unlike futex locks (pthread_mutex etc)
    - Detects crashes, ?unlike semaphores?
    - Isn't filesystem/mount namespace-bound, unlike lockf/fcntl/semaphores

    Python impl supports interleaved async/non-async use
    through lock() and lock_async().

    Waiting is implemented by issuing a blocking send() to the lock holder,
    and detecting when the connection is severed.

    An interesting (not implemented) optimization would be to handle
    graceful unlock() by accepting one of the pending listeners and using
    SCM_RIGHTS to transfer the bound file descriptor.

    There is an unfortunate busy loop in between the lock holder's
    bind() and listen() where lock takers won't know if the lock is held or not
    and thus have to retry taking the lock. This implementation waits for
    times['wait_for_lock'] seconds as implemented in _wait_for_lock()
    and _wait_for_lock_async(). That looks like this (chronologically):

    1. A: bind() -> lock held

    2. B: bind() -> lock not held
    3. B: connect() -> fails, go to 2 [wait_for_lock sleeps here]

    4. A: listen() -> now connect() is possible
    5. B: bind() -> lock not held
    6. B: connect() -> succeeds
    7. B: send() -> blocks because we fill the buffer. we use sendall as a
                    convenience, which translates to a for loop until it blocks.

    '''
    def __init__(self, name:bytes):
        # abstract unix sockets, as opposed to named unix sockets, are not bound
        # in the filesystem namespace, and are created by prefixing a "filename"
        # with a nullbyte:
        self.abstract_name = b'\x00' + name
        self._new_sock()

    def __copy__(self):
        '''not tested, when copying we should allocate new sockets'''
        assert False, 'not tested'
        return self.__class__()(self.abstract_name[1:])
    __deepcopy__ = __copy__

    def _new_sock(self):
        self.listener = socket.socket(AF_UNIX, SOCK_STREAM)
        self.connector = socket.socket(AF_UNIX, SOCK_STREAM)
        # minimize socket buffers:
        self.connector.setsockopt(SOL_SOCKET, SO_SNDBUF, 1) # eg 4608
        self.connector.setsockopt(SOL_SOCKET, SO_RCVBUF, 1) # eg 4608
        self.listener.setsockopt(SOL_SOCKET, SO_SNDBUF, 1) # eg 2304
        self.listener.setsockopt(SOL_SOCKET, SO_RCVBUF, 1) # eg 2304
        # it might block before, but definitely at this point:
        self.block = b'x' * (
            1 + self.connector.getsockopt(SOL_SOCKET, SO_SNDBUF))

    async def _block_connected_async(self):
        '''see self._block_connected()'''
        try:
            await asyncio.get_event_loop().sock_sendall(
                self.connector, self.block)
        except BrokenPipeError:
            self._new_sock()
        except ConnectionResetError:
            pass

    def _block_connected(self):
        '''Blocking (non-async) wait.'''
        try:
            self.connector.sendall(self.block)
        except BrokenPipeError:
            # when the lock holder is killed (non-gracefully)
            # connect() and sendall() will return instantly.
            # technically just need to recreate the connector:
            self._new_sock()
        except ConnectionResetError:
            pass # when the lock holder closes the socket?

    def try_lock(self):
        '''Tries to take the lock, immediately returning True when waiting
        and False when the lock is acquired.'''
        try:
            self.listener.bind(self.abstract_name) # take lock
        except OSError:
            return True # still waiting

        # should make the backlog configurable by providing
        # the optional arg to listen()?'''
        self.listener.listen()
        # Since we never accept() connections, the number of listeners is
        # capped to the default backlog.
        # We could accept(), but that would require code to handle that.

        return False # now has lock

    def unlock(self):
        '''Releases a held lock. Returns None.'''
        self.listener.close()

    async def _wait_for_lock_async(self):
        '''See _wait_for_lock()'''
        try:
            self.connector.connect(self.abstract_name)
        except ConnectionRefusedError:
            await asyncio.sleep(times['wait_for_lock'])
            return
        except OSError as e:
            if e.errno == 106: # if e.errno == 106: # already connected
                pass
            else:
                raise e
        await self._block_connected_async()

    def _wait_for_lock(self):
        '''Blocking wait for the lock to be released.
        Returns early when connect fails.
        Always returns None.
        '''
        try:
            self.connector.connect(self.abstract_name)
        except ConnectionRefusedError:
            # NB: ConnectionRefusedError is a subclass of OSError
            sleep(times['wait_for_lock'])
            # happens after bind, before listen() in try_lock
            # also happens if the lock holder crashed, so we need to retry
            # acquiring the lock.
            return
        except OSError as e:
            if e.errno == 106: # if e.errno == 106: # already connected
                pass
            else:
                raise e
        self._block_connected()

    async def lock_async(self):
        '''Blocking wait for lock (async).
        Returns when the lock has been acquired.'''
        is_waiting = self.try_lock()
        while is_waiting:
            await self._wait_for_lock_async()
            is_waiting = self.try_lock()

    def lock(self):
        '''Blocking wait for lock.
        Returns when the lock has been acquired.'''
        is_waiting = self.try_lock()
        while is_waiting:
            self._wait_for_lock()
            is_waiting = self.try_lock()

async def test_async(lck):
    await lck.lock_async()
    print('have lock, thanks')
    await asyncio.sleep(5)
    print('releasing')
    lck.unlock()
    await asyncio.sleep(5)
    print('reacquiring')
    await lck.lock_async()
    print('got it')
    await asyncio.sleep(5)

if __name__ == '__main__':
    import sys
    lck = UnixSocketLock(b'xtest')
    if 'async' in sys.argv:
        asyncio.run(test_async(lck))
    else:
        lck.lock()
        print('have lock, thanks')
        sleep(5)
        print('releasing')
        lck.unlock()
        sleep(5)
        print('reacquiring')
        lck.lock()
        print('got it')
        sleep(5)
