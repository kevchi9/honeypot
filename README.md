# Honeypot

The project's name is self describing. It is intended to be an honeypot, developped to learn some aspects of this security solution.

Most of the details have already been worked out, but many other still have to be clarified.

By now, the idea is about faking some services by opening ports and logging the connection attempts.

When log files are edited by this listening daemons, another process will read the new logs and send them to a `broker` (by now it's an MQTT broker).

Data on the broker is still to be minupulated and oriented to the right product, but the basic idea is to create alerts with these reports, which may contain also useful information about the connection attemp that has been done.

Another idea is to deploy some containers with vulnerables softwares in order to expose vulnerabilities but in a contained environment, and eventually after some operations, terminate the container and log all the activity performed in it.

The following is a first draft of the project:

![immagine](https://github.com/user-attachments/assets/9fd28086-2c0e-4b81-a697-2dc9319dffa3)

## Components

- Log Collector
  - Log Collector
  - Log Parser
  - MQTT Publisher
- Container Handler
- Connection Listener


## Log Collector

Multiple **threads** can be launched to monitor a specific file path (or a single thread to monitor multiple file paths). When a the log file is modified, the new lines are read and sent to a `MQTT broker`. 

MQTT is used in the first version of the project, but it may be changed with `kafka` in later versions.
