import obspython as obs
import socketserver
import io
import time

class NetCamClientHandler(socketserver.BaseRequestHandler):

    device_supplied_id =''
    pipeline = ''
    def __init__(self, request, client_address, server):
        self.video_port = server.clients_connected -1 + server.base_port # this could be hardcoded to MAC<->Port correlation
        self.plugin_settings = server.plugin_settings
        socketserver.BaseRequestHandler.__init__(self, request,
                                                 client_address,
                                                 server)
        return      

    def find_obs_device_pipeline(self):
        gst_raw_list = obs.obs_data_get_array(self.plugin_settings, "list")
        num_gst_raw = obs.obs_data_array_count(gst_raw_list)

        self.devices = {}
        for i in range(num_gst_raw):  # Convert C array to Python list
            gst_raw_object = obs.obs_data_array_item(gst_raw_list, i)
            device_id,pipeline = obs.obs_data_get_string(gst_raw_object, "value").split("~")
            self.devices[device_id]=pipeline

        for device_id,pipeline in self.devices.items():
                print("{device_id}: {pipeline}".format(device_id=device_id,pipeline=pipeline))
        if self.device_supplied_id in  self.devices:
            obs.script_log(obs.LOG_INFO,"Device entry found for {device_id}".format(device_id=self.device_supplied_id))
            self.pipeline =  self.devices[self.device_supplied_id] #"videotestsrc ! matroskamux ! queue ! tcpclientsink host=127.0.0.1 port=8675"
        else:
            obs.script_log(obs.LOG_INFO,"No device entry for {device_id}".format(device_id=self.device_supplied_id))
        return
    
    def update_gst_source(self,source_name, pipeline):
        
        source = obs.obs_get_source_by_name(source_name)

        settings = obs.obs_data_create()
        obs.obs_data_set_string(settings, "pipeline", pipeline)

        if source is None:
            obs.script_log(obs.LOG_INFO,"Creating non-existant GStreamer source: {source_name}".format(source_name=source_name))
            source = obs.obs_source_create("gstreamer-source",source_name,None,None) # TODO - this doesn't seem to create sources

        else:
            obs.script_log(obs.LOG_INFO,"Updating {source_name} pipeline to: {pipeline}".format(source_name=source_name,pipeline=pipeline))
            
        obs.obs_source_update(source, settings)
        obs.obs_data_release(settings)
        obs.obs_source_release(source)

    def handle(self):
        global config 
        self.device_supplied_id = self.request.recv(1024).strip().decode('UTF-8')
        obs.script_log(obs.LOG_INFO,"Device requesting configuration: {device_id}".format(device_id=self.device_supplied_id))
        self.find_obs_device_pipeline()
        if self.pipeline : # we know about this device
            obs.script_log(obs.LOG_INFO,"Config found for {device_id}".format(device_id=self.device_supplied_id))
            self.update_gst_source(self.device_supplied_id,"tcpserversrc host=127.0.0.1 port=8675 ! queue ! matroskademux ! tee name=t t. ! video.")
            time.sleep(1)
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

   