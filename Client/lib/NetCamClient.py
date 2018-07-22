from uuid import getnode
import socket
from gi.repository import Gst, GObject
import configparser

from lib.GSTInstance import GSTInstance
import time

class NetCamClient():
    host = 0
    camType = ''
    config = 0
    cam_id = 0
    coreStreamer = 0
    shouldExit = False
    loop = 0

    def __init__(self):
        self.cam_id = self.get_self_id()
     

    def wait_for_core(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(('', 54545))
        print("Waiting for service announcement")
        while True:
            data, addr = self.socket.recvfrom(2048)
            print("Core found: ", addr)
            break
        self.socket.close()
        return addr

    def wait_for_config(self):
        core = self.wait_for_core()
        self.host, self.port = core
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((self.host, 5455))
        message = "{mac}".format(mac=self.cam_id)
        mesbytes = bytes(message,'UTF-8')
        len_sent = s.send(mesbytes)
        response = s.recv(2048).decode('UTF-8')
        print(response)
        self.coreStreamer = GSTInstance(response,self.loop)
        s.close()

    def run(self):
        self.loop = GObject.MainLoop()
        while True: # not self.shouldExit:
            try:
                self.wait_for_config()
                self.loop.run()
            except Exception as ex:
                print("Outer Exception: " + ex)
            print("Restarting NetCamClient")
        
    def get_self_id(self):
        """
            returns the ID of this camera
            after first execution, the ID should persist to a file
        """
        configfilepath="./camera.ini"

        config = configparser.ConfigParser()
        config.read(configfilepath)
        camid = ""
        if config.has_section("camera"):
            camid = config.get("camera","id")
            print("Found CamID in camera.ini: " + camid)
        else:
            config.add_section("camera")

        if (camid == ""):
            h = iter(hex(getnode())[2:].zfill(12))
            camid = ":".join(i + next(h) for i in h)
            config.set("camera","id",camid)
            with open(configfilepath, 'w') as configfile:
                config.write(configfile)
            print("Generated CamID and wrote to camera.ini: " + camid)
        
        return camid



    def end(self):
        global loop
        self.shouldExit = True
        loop.quit()
        