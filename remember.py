#!/usr/bin/python3
import json
import logging
from time import sleep
from os.path import isfile
from phue import Bridge, PhueRegistrationException

logging.basicConfig(filename="remember.log",
                    level=logging.DEBUG)
log = logging.getLogger(__name__)
console_log = logging.StreamHandler()
console_log.setLevel = log.level
log.addHandler(console_log)

def connect_bridge():
    if isfile("config.python_hue"):
        log.debug("Using saved credentials to connect to bridge.")
        return Bridge(config_file_path="config.python_hue")
    else:
        log.debug("No saved credentials, connecting for the first time.")
        ip = input("Input the local IP address of your bridge: ")
        b = None
        try:
            b = Bridge(ip, config_file_path="config.python_hue")
        except PhueRegistrationException:
            log.debug("Prompting user to press bridge button to authenticate.")
            input("Press the button on the Hue Bridge and then Enter to continue...")
            b = Bridge(ip, config_file_path="config.python_hue")
        return b

def monitor(b):
    last_lighting = {}
    if isfile("last_lighting.json"):
        log.debug("Saved lighting detected, loading...")
        with open("last_lighting.json") as last_lighting_file:
            last_lighting = json.load(last_lighting_file)
        log.debug("Saved lighting loaded.")
    while True:
        log.debug("Beginning monitor check, fetching lights...")
        lights = b.get_light_objects()
        last_lighting_dirty = False
        changed_lights = False
        log.debug("Lights fetched, iterating...")
        for light in lights:
            last_light = None
            light_uid = b.get_light(light.light_id, "uniqueid")
            if not light_uid in last_lighting:
                log.debug("New light detected, adding to list...")
                last_lighting[light_uid] = {}
                last_light = last_lighting[light_uid]             
                last_light["xy"] = light.xy
                last_light["ct"] = light.colortemp
                last_light["hs"] = [light.hue, light.saturation]
                last_light["br"] = light.brightness
                last_light["on"] = light.on
                last_light["mode"] = light.colormode
                last_lighting_dirty = True
                log.debug("New light added to list.")
            else:
                last_light = last_lighting[light_uid]
                if light.colortemp == 366 and light.brightness == 254:
                    if last_light["ct"] == 366 and last_light["br"] == 254: 
                        continue
                    
                    log.debug("%s has triggered remember, changing lights back..." % light_uid)
                    light.brightness = last_light["br"]
                    if last_light["mode"] == "xy":
                        light.xy = last_light["xy"]
                    elif last_light["mode"] == "hs":
                        light.hue = last_light["hs"][0]
                        light.saturation = last_light["hs"][1]
                    elif last_light["mode"] == "ct":
                        light.colortemp = last_light["ct"]
                    light.on = last_light["on"]
                    changed_lights = True
                    log.debug("%s has been changed back.")
                else:
                    if (last_light["xy"] != light.xy or 
                        last_light["hs"][0] != light.hue or
                        last_light["hs"][1] != light.saturation or
                        last_light["ct"] != light.colortemp or
                        last_light["br"] != light.brightness or
                        last_light["on"] != light.on or
                        last_light["mode"] != light.colormode):

                        # Apparently this isn't redundant?
                        if light.colortemp == 366 and light.brightness == 254:
                            continue

                        log.debug("Light %s has changed, remembering..." % light_uid)
                        last_light["xy"] = light.xy
                        last_light["ct"] = light.colortemp
                        last_light["hs"] = [light.hue, light.saturation]
                        last_light["br"] = light.brightness
                        last_light["on"] = light.on
                        last_light["mode"] = light.colormode
                        last_lighting_dirty = True
                        log.debug("Light %s has change remembered." % light_uid)
        if last_lighting_dirty:
            log.debug("Lights have changed, saving changes to file...")
            with open("last_lighting.json", "w") as last_lighting_file:
                json.dump(last_lighting, last_lighting_file, indent=4)
            log.debug("The changes have been saved to file.")
        if changed_lights:
            log.debug("Monitor check done, lights changed, waiting for 10 seconds before the next.")
            sleep(10)
        else:
            log.debug("Monitor check done, waiting for 1 second before the next.")
            sleep(1)

if __name__ == "__main__":
    log.debug("Connecting to the bridge...")
    b = connect_bridge()
    log.debug("Starting lights monitor.")
    monitor(b)
