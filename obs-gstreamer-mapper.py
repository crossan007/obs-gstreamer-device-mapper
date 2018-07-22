import obspython as obs
import urllib.request
import urllib.error
from lib.NetCamClientHandler import NetCamClientHandler
from lib.NetCamMasterAdvertisementService import NetCamMasterAdvertisementService
from lib.NetCamMasterServer import NetCamMasterServer
from threading import Thread

url         = ""
interval    = 30
source_name = ""

# ------------------------------------------------------------

def update_gst_source(source_name, pipeline):
	source = obs.obs_get_source_by_name(source_name)
	settings = obs.obs_data_create()
	obs.obs_data_set_string(settings, "pipeline", pipeline)
	obs.obs_source_update(source, settings)
	obs.obs_data_release(settings)
	obs.obs_source_release(source)

def update_text():
	global url
	global interval
	global source_name

	source = obs.obs_get_source_by_name(source_name)
	if source is not None:
		try:
			with urllib.request.urlopen(url) as response:
				data = response.read()
				text = data.decode('utf-8')

				settings = obs.obs_data_create()
				obs.obs_data_set_string(settings, "text", text)
				obs.obs_source_update(source, settings)
				obs.obs_data_release(settings)

		except urllib.error.URLError as err:
			obs.script_log(obs.LOG_WARNING, "Error opening URL '" + url + "': " + err.reason)
			obs.remove_current_callback()

		obs.obs_source_release(source)

# ------------------------------------------------------------

def script_description():
	return ("Automatically maps network cameras to OBS Sources using GStreamer.\n\n"
	"List entries are in the format:\n"
	"<DeviceID>:<RemoteGStreamerPipeline>\n\n"
	
	"All remote pipelines must output to .video and .audio\n\n"
	"Source matching <DeviceID> must exist"
	)

def script_load(settings):
	global AdvertismentServiceThread
	global ClientConfigurationServerThread
	AdvertismentServiceThread = NetCamMasterAdvertisementService('0.0.0.0',54545)
	AdvertismentServiceThread.daemon = True
	AdvertismentServiceThread.start()
	myserver = NetCamMasterServer(('0.0.0.0',5455),NetCamClientHandler)
	ClientConfigurationServerThread =Thread(target=myserver.serve_forever)
	ClientConfigurationServerThread.daemon = True  # don't allow this thread to capture the keyboard interrupt
	ClientConfigurationServerThread.start()
	obs.script_log(obs.LOG_INFO,"test")
	update_gst_source("GStreamer Source","tcpserversrc host=0.0.0.0 port=8675 ! matroskademux ! tee name=t t. ! video.")

def script_unload():
	obs.script_log(obs.LOG_INFO,"test")
	#AdvertismentServiceThread.stop()
	#ClientConfigurationServerThread.shutdown()

def script_update(settings):
	global url
	global interval
	global source_name

	url         = obs.obs_data_get_string(settings, "url")
	interval    = obs.obs_data_get_int(settings, "interval")
	source_name = obs.obs_data_get_string(settings, "source")

	obs.timer_remove(update_text)

	if url != "" and source_name != "":
		obs.timer_add(update_text, interval * 1000)

def script_defaults(settings):
	obs.obs_data_set_default_int(settings, "interval", 30)

def script_properties():
	props = obs.obs_properties_create()

	obs.obs_properties_add_editable_list(props, "list", "GStreamer Pipelines List", obs.OBS_EDITABLE_LIST_TYPE_STRINGS,'','')

	return props