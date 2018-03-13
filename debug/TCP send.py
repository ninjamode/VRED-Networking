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
    print "Received data", data
    if data is None:
        tcp.handle.close()
        return

    split = data.split(b"\n")
    for message in split:
        if len(message) > 0:
            unp = msgpack.unpackb(message)
            print "Received:", unp

            if unp[0] == "rpc":
                globals()[unp[1]](*unp[2])

def on_connect(handle, error):
    global a
    print error
    handle.start_read(on_read)
    rpc("do_stuff", 1,2,34)
    rpc("do_stuff", 5,4,34)
    rpc("do_stuff", 1,2,"yolo")

def send_ping():
    tcp.write(msgpack.packb(("ping", 1)))


def rpc(fname, *args):
    """ Need to make sure args only contains vars msgpack can pack for transmission """
    tcp.write(msgpack.packb(("rpc", fname, args)) + "\n")


def do_stuff(one, two, three):
    print one, two, three


tcp = pyuv.TCP(pyuv.Loop.default_loop())
tcp.connect(("127.0.0.1", port), on_connect)
pyuv.Loop.default_loop().run()