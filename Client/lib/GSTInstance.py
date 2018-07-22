from gi.repository import Gst

class GSTInstance():
    pipeline = 0

    def __init__(self, pipelineText, clock=None):
        print("Starting GSTInstance local pipeline: {pipelineText}".format(pipelineText=pipelineText))
        
        self.pipeline = Gst.parse_launch(pipelineText)
        self.pipeline.bus.add_signal_watch()
        self.pipeline.bus.connect("message::error", self.on_error)
        self.pipeline.bus.connect("message::eos", self.on_eos)
        self.pipeline.bus.connect("message::state-changed", self.on_state_changed)
        self.pipeline.bus.connect("message::application", self.on_application_message)
        if clock != None:
            print("Using remote clock")
            self.pipeline.use_clock(clock)
        else:
            print("Using device clock")
        print("playing...")
        self.pipeline.set_state(Gst.State.PLAYING)

    def on_error(self,bus,msg):
        err, dbg = msg.parse_error()
        print("ERROR:", msg.src.get_name(), ":", err.message)
        print("Debug info:", dbg)


    def on_eos(self,bus,msg):
        print("End-Of-Stream reached")
        #self.pipeline.set_state(Gst.State.READY)

    def on_state_changed(self,bus,msg):
        print("State Changed")
        old, new, pending = msg.parse_state_changed()
        print("State changed from {0} to {1}".format(
            Gst.Element.state_get_name(old), Gst.Element.state_get_name(new)))

    def on_application_message(self,bus,msg):
        print("Application Message")


    def end(self):
        print('Shutting down GSTInstance')
        self.pipeline.set_state(Gst.State.NULL)