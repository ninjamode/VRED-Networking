"""
Server application for VRED-Networking
"""

import timeit
import pyuv
import msgpack
import signal
import logging

# TODO: argparse ports and ip

TCP_PORT = 40305
UDP_PORT = 40306
SELF = "0.0.0.0"

# Don't try to send sync packs to udp connections older than that (value in sec)
# TODO: Also kill the corresponding tcp connection??
UDP_TIMEOUT = 10

# Safe last sync message for each net id and supply it to everyone who connects (initial state sync)
KEEP_STATE = True


##### TCP stuff #####
# TODO: Do something useful on error
def tcp_read(client, data, error):
    # No data means the client has closed the connection
    if data is None:
        logging.info(f"{client.getpeername()} disconnected")
        close_tcp(client)
        # TODO: Also remove this clients UDP connection
        return

    logging.debug(f"Got TCP data {data} from {client.getpeername()}")

    try:
        answer = parse(data)
    except Exception as e:
        # TODO: Less broad exception
        logging.error(f"Parsing message failed with {e}")
        return

    if answer["distribute"]:
        for c in tcp_connections:
            if c != client:
                c.write(answer["data"])
    else:
        client.write(answer["data"])


def close_tcp(client):
    client.close()
    tcp_connections.remove(client)


def tcp_connect(server, error):
    client = pyuv.TCP(server.loop)
    server.accept(client)
    tcp_connections.append(client)
    client.start_read(tcp_read)
    client.nodelay(True)
    logging.info(f"{client.getpeername()} connected")


##### UDP Stuff #####

def udp_read(handle, ip_port, flags, data, error):
    """ Read UDP messages, parse them and answer based on the message contents

    Also put every connection in a dict, so we know who to send sync packs to.
    """
    if data is not None:
        logging.debug(f"Got UDP data {data} from {ip_port}")
        udp_connections[ip_port] = timeit.default_timer()

        try:
            answer = parse(data)
        except Exception as e:
            # TODO: Less broad exception
            logging.error(f"Parsing message failed with {e}")
            return

        if answer["distribute"]:
            for address in udp_connections:
                if address != ip_port:
                    handle.send(address, answer["data"])
        else:
            handle.send(ip_port, answer["data"])


##### Stuff #####

def parse(data):
    """ Parse a message to look for state, and save it if so

    Hey -> Answer with Ho and initial state, if available
    RPC -> Distribute to everyone else
    Ping -> answer with Pong packet
    Sync Pack -> Send to all udp connections
                 also add to initial state map if newest for its node
    """
    message = msgpack.unpackb(data, use_list = True, raw = False)
    logging.debug(f"Parsed message: {message}")
    msg_type = message[0]
    if msg_type == "hey":
        answer = {"distribute": False, "data": msgpack.packb(("ho", last_state))}
    elif msg_type == "rpc":
        answer = {"distribute": True, "data": data}
    elif msg_type == "ping":
        message[0] = "pong"
        answer = {"distribute": False, "data": msgpack.packb(message)}
    elif msg_type == "pos" or msg_type == "rot" or msg_type == "scale" or msg_type == "state":
        answer = {"distribute": True, "data": data}
        save_state(message)
    else:
        raise LookupError(f"Unknown message type {message[0]}")

    return answer


def save_state(message):
    """ Put the newest sync data for each node in a dict for inital setup """
    if KEEP_STATE:
        tpe = message[0]
        for pack in message[1]:
            net_id = pack[0]
            seq = pack [1]
            if not net_id in last_state[tpe] or last_state[tpe][net_id][0] < seq:
                last_state[tpe][net_id] = (seq, pack[2])


def check_udp(timer):
    """ Check all recent udp connections, remove if dead """
    now = timeit.default_timer()
    for ip_port, time in list(udp_connections.items()):
        if now - time > UDP_TIMEOUT:
            logging.warning(f"{ip_port} for {now - time}s over timeout ({UDP_TIMEOUT})")
            del(udp_connections[ip_port])


def signal_cb(handle, signum):
    """ Handle shutdown signals for graceful shutdown """
    logging.debug("Shutting things down")
    [c.close() for c in tcp_connections]
    handle.close()
    tcp.close()
    udp.close()
    loop.stop()
    logging.info("Shutdown complete")


logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', level=logging.DEBUG)

tcp_connections = []
udp_connections = {}
last_state = {"pos": {}, "rot": {}, "scale": {}, "state": {}}

loop = pyuv.Loop.default_loop()

# TCP Connection
tcp = pyuv.TCP(loop)
tcp.bind((SELF, TCP_PORT))
tcp.listen(tcp_connect)
tcp.nodelay(True)

# UDP Connection
udp = pyuv.UDP(loop)
udp.bind((SELF, UDP_PORT))
udp.start_recv(udp_read)

# Handle shutdown gracefully (listen to ctrl c / SIGINT)
signal_handle = pyuv.Signal(loop)
signal_handle.start(signal_cb, signal.SIGINT)

# Remove dead UDP connections (Heartbeat timeout)
heartbeat_timer = pyuv.Timer(loop)
heartbeat_timer.start(check_udp, 1, 1)

logging.info("Server startup complete")
loop.run()
