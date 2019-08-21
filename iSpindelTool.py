#!/usr/bin/env python3

# simple iSpindel monitoring tool

# MIT License
#
# Copyright (c) 2019 Charles Fourneau
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from datetime import datetime
import json
import logging
import queue
import socketserver
import sys
from threading import Thread
from time import sleep
import tkinter as tk
from tkinter import ttk

APP_NAME = "iSpindel Tool"

# server settings
HOST, PORT = "0.0.0.0", 9901

# control characters (as bytes)
ACK = chr(0x06).encode()
NAK = chr(0x15).encode()

# queue used to share data between threads
data_queue = queue.SimpleQueue()

# logging
log = logging.getLogger(__name__)
log.setLevel(logging.INFO) # reduce to INFO or DEBUG for more verbose
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# log to console
ch = logging.StreamHandler(sys.stdout)
log.addHandler(ch)
# ... and to file
fh = logging.FileHandler(r'ispindel.log')
fh.setFormatter(formatter)
log.addHandler(fh)


class ISpindelTCPHandler(socketserver.StreamRequestHandler):
    def handle(self):
        """
        Handle TCP requests
        If received data is valid json, send ACK and store in queue
        If not, send NAK
        """
        self.data = self.rfile.readline().strip()
        log.debug("[RAW] {} wrote: {}".format(self.client_address[0], self.data.decode()))
        try:
            ispindel_data = json.loads(self.data.decode())
            log.info("[JSON] received from {}: \n{}".format(self.client_address[0], ispindel_data))
            data_queue.put((datetime.now().isoformat(' ', 'seconds'), ispindel_data))
            self.wfile.write(ACK)
        except json.JSONDecodeError as e:
            log.error("[JSON] DecodeError:", e)
            self.wfile.write(NAK)


class SocketServerThread(Thread):
    """
    Encapsulate a SocketServer in a thread
    """
    def __init__(self, addr=('localhost',9999), handler=None):
        Thread.__init__(self)
        self._server = socketserver.TCPServer(addr, handler)
    
    def run(self):
        log.info("Starting server")
        self._server.serve_forever()
    
    def stop(self):
        log.info("Stopping server")
        self._server.shutdown()


class ISpindelQueueHandler(Thread):
    """
    Manage the data queue

    If data is added to the queue, it is used to update the device
    representation in the Treeview.
    """
    def __init__(self, data_queue):
        Thread.__init__(self)
        self._queue = data_queue
        self._stop = False

    def run(self):
        log.info("Starting Queue Handler")
        ispindel_data = {}
        while not self._stop:
            if not self._queue.empty():
                log.debug("Something in the queue \o/")
                try:
                    time, ispindel_data = self._queue.get(block=False)
                except queue.Empty:
                    log.error("Nothing found in the queue")
                    continue
            else:
                sleep(1)
                continue
            device_id = "{}.{}".format(ispindel_data["name"], ispindel_data["ID"])
            if not app.treeview.exists(device_id):
                # new device
                app.treeview.insert("", "end", iid=device_id, text="{} [{}]".format(ispindel_data["name"], ispindel_data["ID"]), tags=('device'))
                for parameter, value in ispindel_data.items():
                    app.treeview.insert(device_id, "end", iid="{}.{}".format(device_id, parameter), text=parameter, values=(value))
                app.treeview.insert(device_id, "end", iid="{}.{}".format(device_id, "time"), text="Last update", values=(time,)) # comma is used to avoid considering the string as an iterable
            else:
                # known device - update values
                for parameter, value in ispindel_data.items():
                    app.treeview.item("{}.{}".format(device_id, parameter), values=(value))
                app.treeview.item("{}.{}".format(device_id, "time"), values=(time,))

    def stop(self):
        log.info("Stopping Queue Handler")
        self._stop = True


class ISpindelGUI(ttk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        self._build_gui()

    def _build_gui(self):
        self.treeview = ttk.Treeview(self)
        self.treeview.heading('#0', text="Device/Parameter")
        self.treeview["columns"] = ("value")
        self.treeview.column("value", width=150)
        self.treeview.heading("value", text="Value")
        # styling
        ttk.Style().configure("Treeview", font=("TkDefaultFont", 10))
        self.treeview.tag_configure("device", font=("TkDefaultFont", 10, 'bold'))
        # layout
        self.rowconfigure(0, weight=1)      # give non-zero weights to allow resizing
        self.columnconfigure(0, weight=1)
        self.treeview.grid(row=0, column=0, sticky='nswe')
        self.pack(fill=tk.constants.BOTH, expand=1)


if __name__ == "__main__":
    log.info("*** Welcome to {}".format(APP_NAME))
        
    tk_root = tk.Tk()
    tk_root.title(APP_NAME)

    server_thread = SocketServerThread((HOST, PORT), ISpindelTCPHandler)
    server_thread.start()

    queue_handler_thread = ISpindelQueueHandler(data_queue)
    queue_handler_thread.start()

    app = ISpindelGUI(tk_root)
    app.mainloop()



