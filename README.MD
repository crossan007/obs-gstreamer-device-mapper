# Overview
Provides an in-application UI to manage remote GStreamer pipeline, and map the pipeline into OBS sources.

A backgroun daemon runs inside the OBS script host.  This daemon advertises the presence of the OBS device server.

When remote devices receive the presence advertisment, they connect to the OBS server.
The clients supply their device id, and OBS server cross-reference the device id with the pre-configured list.
If a matching device id is found, then the pipeline is executed on the remote device

## Sources Editor
Many different devices can be configured in the Script's properties pane:
![image](https://user-images.githubusercontent.com/11679900/43042292-f008424c-8d47-11e8-846f-1ef09ee0a13a.png)

Devices are configured in the format `<DeviceID>~<GStreamerPipeline>`
So, the following would remotely execute `videotestsrc` and map the pipeline to the local OBS source named `08:00:27:c5:f3:c1`:
```
08:00:27:c5:f3:c1~videotestsrc pattern=18 ! matroskamux ! queue ! tcpclientsink host=127.0.0.1 port=8675
```


## Auto Mapping
Devices listed in the scirpt properties pane are automatically mapped to the corresponding source in OBS
![image](https://user-images.githubusercontent.com/11679900/43042303-176b2d72-8d48-11e8-83b8-f0a9056b7f51.png)





![image](https://user-images.githubusercontent.com/11679900/43042169-147f27e8-8d44-11e8-8870-3c6b83cd7deb.png)

