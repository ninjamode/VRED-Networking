import pyuv
import msgpack

v1 = (1,2,1)
v2 = (2,3,2)
v3 = (3,4,3)

# Sync packs ==
# Identifier (pack type) + List of
# ("Network ID", sequence counter, actual_data)
# actual data can be a tuple of 3 floats or a boolean

pos_msg = ("pos", [
    ("v1P", 121, v1),
    ("v2P", 122, v2),
    ("v3P", 123, v3),
])

rot_msg = ("rot", [
    ("v1R", 121, v1),
    ("v2R", 122, v2),
    ("v3R", 123, v3),
])

scale_msg = ("scale", [
    ("v1S", 121, v1),
    ("v2S", 122, v2),
    ("v3S", 123, v3),
])

state_msg = ("rot", [
    ("v1A", 121, True),
    ("v2A", 122, False),
    ("v3A", 123, True),
])


udp = pyuv.UDP(pyuv.Loop.default_loop())

udp.send(("127.0.0.1", 40306), msgpack.packb(pos_msg))
udp.send(("127.0.0.1", 40306), msgpack.packb(rot_msg))
udp.send(("127.0.0.1", 40306), msgpack.packb(scale_msg))
udp.send(("127.0.0.1", 40306), msgpack.packb(state_msg))
