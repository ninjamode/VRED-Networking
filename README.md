# VRED-Networking
Networking for Autodesk VRED 2018 and later. This is demonstration software and might break at any point (hopefully not).

**IMPORTANT NOTICE:<br>
DO NOT RUN THIS IN AN UNTRUSTED NETWORK! THERE IS NO ENCRPTION, AUTHENTICATION OR VERIFICATION! ATTACKERS COULD RUN ANY PYTHON CODE ON YOUR MACHINE!**

If you want to connect multiple VRED instanced over the internet, you could use a VPN tool like tinc (https://www.tinc-vpn.org) to handle security for you.
Alternatively, extend this plugin to include message authentication and encryption.

## What does this do?

This plugin enables you to synchronize multiple VRED instances over a network. You can synchronize node information and do remote procedure calls.
A central server application handles distribution of messages between VRED instances. The address of this server is the only thing you need to tell the plugin. No more configuration necessary to start!

Features:
- Really fast! Only transmits data which has changed, node synchronization is done over UDP
- You can select if you want to sync a nodes position, rotation, scale or active state (and also mix those)
- Easy usage! No need to code to sync nodes
- Remote procedure calls over TCP
- Initial state synchronazation (node position, rotation, scale and state)
- Dedicated server application (can also be run locally)
- Does not rely on any thrid party services
- Free!

## Whats in the box?

`Server.py` Server application

`Networking` A plugin to add networking capabilities to VRED. Distributed as a tool for VRED Toolkit.

`pyuv` and `msgpack` python 2.7 plugins, compiled with VS 2015 for VRED.

## Plugin setup 

1. Move the `pyuv` and `msgpack` folders to `*your_user_folder*/Autodesk/`
2. Add the plugin (the `Networking` file) to your VRED Toolkit `tools` folder. 

After you start VRED the next time, you will see an *Add Networking* button under the Toolkit menu entry. Press this button to add networking capabilities to your scene.  

### Server setup

The server (Server.py) requires Python 3 to run (tested with 3.6). The server can be run on a machine that also runs VRED, but it does not need to. It also requires the `msgpack` and `pyuv` packages (run this on a console):
```
pip3 install msgpack
pip3 install pyuv
```

## Usage

Usage is divided into two parts: Scene setup and actual networking.

### Scene setup

1. Add networking to your scene (from the toolbar menu item)
2. Node synchronization is done via tags. Add the tag `_Networking Position Sync` (and/or the rotation/scale/state) variant to all nodes you want to synchronize.
3. Press `alt + U` to update the networking plugin with your nodes. Remeber to always press this hotkey after you changed node tags! You can adjust this hotkey in the script editor.
4. In the script editor, adjust the automatically added code so that the address points to your servers network address.

### Run a networked session

0. Make sure all clients have the same version of the VRED scene file. Make sure all clients can reach the machine, on which the server application runs. Make sure the correct server address is entered in the Script Editor.
1. Start Server.py with python3. 
2. Start VRED.
3. Press the hotkey `alt + c` to connect. That's it!

## Adavanced Usage

You can use remote procedure calls, short `rpc` to execute methods on other nodes. Use this to synchronize your python code acress connected devices. Call the `rpc` method on the networking object with the target method name as the first argument. Subsequent arguments will be transmitted and passed to the method on execution.

```python

# This will call the method "my_method" with arguments 1 and "two" on all OTHER machines
# Will NOT call "my_method" on this machine!
net = Networking()
net.rpc("my_method", 1, "two")

def my_method(arg1, arg2):
    print arg1, arg2

```

### Configuration

Networking will try to read the file `Networking.cfg` at `~/Autodesk/` plus any file you supply to the `config_file` networking costructor parameter (also in the autodesk folder). Values from this per file config will override global values from `Networking.cfg`. Example config:

```
[Networking]
; This is an example config file
ip = 127.0.0.1 ; Server ip
name = Constantin ; Name of this machine
spawn = None ; Spawn a camera for this machine on connection
```

This file uses Python ConfigParser (https://docs.python.org/2/library/configparser.html) syntx.
Use this to identify different machines or apply different settings for special machines without modifying the scene.

## Caveats

This is demo software, use at your own risk. Feel free to adapt the scripts to your needs and provide pull requests if you fix things.
Again, this does not include any security features at the moment. Make sure you run all components on trusted networks behind a firewall.
Currently Windows only; Server is cross plattform. Might or might not work on Mac and Linux (pyuv and msgpack module is provided for these systems, you can try the official ones, but you might need to compile them yourself to ensure stable operation)
Only tested with VRED 2018.4!

## To Do

- Performance could be improved, especially when packing data
- (message) authentication
- Interpolation between synced state
- Strings that go over tcp (mainly rpc) can not contain \\n, as this is used to delimit msgpack messages. Could use something else here
- Could abstract communication channel more to easily implement other networking solution (pubsub etc.) 
