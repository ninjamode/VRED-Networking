"""
Try to initiate a TCP connection
"""

import pyuv
import signal
import msgpack
import time
import timeit
import sys

port = 40305
a = 0

def on_read(tcp_handle, data, error):
    print "Received:", msgpack.unpackb(data)
    print "took", timeit.default_timer() - a


def on_connect(handle, error):
    global a
    print error
    handle.start_read(on_read)
    msg = msgpack.packb(["hey"])
    size = sys.getsizeof(msg)
    print "msg size: ", size
    handle.write(msg)
    a = timeit.default_timer()

def send_ping():
    tcp.write(msgpack.packb(("ping", 1)))


tcp = pyuv.TCP(pyuv.Loop.default_loop())
tcp.connect(("127.0.0.1", port), on_connect)
pyuv.Loop.default_loop().run()