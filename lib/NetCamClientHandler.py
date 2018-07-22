import obspython as obs
import socketserver
import io

class NetCamClientHandler(socketserver.BaseRequestHandler):

    device_supplied_id =''
    pipeline = ''
    def __init__(self, request, client_address, server):
        self.video_port = server.clients_connected -1 + server.base_port # this could be hardcoded to MAC<->Port correlation
        socketserver.BaseRequestHandler.__init__(self, request,
                                                 client_address,
                                                 server)
        return

    def find_obs_device_pipeline(self):
        self.pipeline = "videotestsrc ! matroskamux ! tcpclientsink host=127.0.0.1 port=8675"
        return

    def handle(self):
        global config 
        self.device_supplied_id = self.request.recv(1024).strip().decode('UTF-8')
        obs.script_log(obs.LOG_INFO,"Device requesting configuration: {device_id}".format(device_id=self.device_supplied_id))
        self.find_obs_device_pipeline()
        if self.pipeline : # we know about this device
            obs.script_log(obs.LOG_INFO,"Config found for {device_id}".format(device_id=self.device_supplied_id))
            self.signal_client_start()
          
        else: # We don't know about this device
            obs.script_log(obs.LOG_INFO,"Config not found for {device_id}".format(device_id=self.device_supplied_id))
            return
        #self.print_self()
        #obs.script_log(obs.LOG_INFO,"{} connected:".format(self.client_address[0]))
        #self.setup_core_listener()
        #self.signal_client_start()

    def print_self(self):
        obs.script_log(obs.LOG_INFO,"Cam ID: {id}".format(id=self.cam_id))
        obs.script_log(obs.LOG_INFO,"Cam Name: {name}".format(name=self.cam_config.get(self.cam_id,"name")))
        obs.script_log(obs.LOG_INFO,"Cam Core_Port: {core_port}".format(core_port=self.cam_config.get(self.cam_id,"core_port")))
        obs.script_log(obs.LOG_INFO,"Cam Encoded Port: {video_port}".format(video_port=self.cam_config.get(self.cam_id,"video_port")))

    def signal_client_start(self):
        print ("Telling {client}: {pipeline}".format(client=self.device_supplied_id, pipeline=self.pipeline))
        self.request.sendall(self.pipeline.encode())

   