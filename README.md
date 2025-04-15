# Honeypot

The project's name is self describing. It is intended to be an honeypot, developped to learn some aspects of this security solution.

Most of the details have already been worked out, but many other still have to be clarified.

By now, the idea is about faking some services by opening ports and logging the connection attempts.

When log files are edited by this listening daemons, another process will read the new logs and send them to a `broker` (by now it's an MQTT broker).

Data on the broker is still to be minupulated and oriented to the right product, but the basic idea is to create alerts with these reports, which may contain also useful information about the connection attemp that has been done.

Another idea is to deploy some containers with vulnerables softwares in order to expose vulnerabilities but in a contained environment, and eventually after some operations, terminate the container and log all the activity performed in it.

The following is a first draft of the project:

![Screenshot 2025-04-15 161952](https://github.com/user-attachments/assets/3256e326-296a-4083-b134-45b62f099837)

## Components

- Log Collector 
- Container Handler
- Connection Listener
- MQTT Publisher

## Log Collector

Multiple **threads** can be launched to monitor a specific file path (or a single thread to monitor multiple file paths). When a the log file is modified, the new lines are read and sent to a `MQTT broker`. 

MQTT is used in the first version of the project, but it may be changed with `kafka` in later versions.
