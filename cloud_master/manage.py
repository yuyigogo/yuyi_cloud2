#!/usr/bin/env python
import os
import sys
from cloud.settings import MQTT_CLIENT_CONFIG
from cloud_mqtt.mqtt_client import CloudMqtt

if __name__ == "__main__":

    SETTINGS = "cloud.settings"
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", SETTINGS)

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
    # cloud_mqtt_client = CloudMqtt(MQTT_CLIENT_CONFIG["cloud_client_id"]).run()