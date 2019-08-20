#!/usr/bin/env python

# iSpindelTool test client

import socket
import sys
import json

HOST, PORT = "localhost", 9999

DATA = json.dumps({ 'ID': 'ABCDEF', 'name':'iSpindel000', 'angle':25.5 },
                  separators=(',', ':'))
DATA2 = 'request type 02'

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    sock.connect((HOST,PORT))

    sent = sock.sendall(str.encode(DATA + '\n'))
    if sent == 0:
        raise RuntimeError("socket connection broken")

    received = sock.recv(1024)
    print("Sent:     {}".format(DATA))
    print("Received: {}".format(received))

    sent = sock.sendall(str.encode(DATA2 + '\n'))
    if sent == 0:
        raise RuntimeError("socket connection broken")

    received = sock.recv(1024)
    print("Sent:     {}".format(data))
    print("Received: {}".format(received))

except Exception as e:
    print("ERROR >>>", e)

finally:
    sock.close()
