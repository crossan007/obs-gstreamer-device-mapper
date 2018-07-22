#!/usr/bin/env python3


from threading import Thread
import gi
gi.require_version('Gst', '1.0')
gi.require_version('GstNet', '1.0')
from gi.repository import Gst, GstNet, GObject
import configparser

from lib.NetCamClient import NetCamClient


def exit_master():
    global args, mainloop, t, master, myserver, camera, shouldExit
    print("exit_master invoked")
    print("Cleaning Up client")
    camClient.end()
    shouldExit = True
    print("Exiting")


def main():
    global args, mainloop, t, master, myserver, camClient, shouldExit
    Gst.init([])
    camClient = NetCamClient()
    t = Thread(target=camClient.run)
    t.daemon = True
    t.start()

if __name__ == '__main__':
    mainloop = GObject.MainLoop()
    try:
        main()
        mainloop.run()
    except KeyboardInterrupt:
        exit_master()
