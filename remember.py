from phue import Bridge, PhueRegistrationException
import json
from os.path import isfile
from time import sleep

def connect_bridge():
    if isfile("config.python_hue"):
        return Bridge(config_file_path="config.python_hue")
    else:
        ip = input("Input the local IP address of your bridge: ")
        b = None
        try:
            b = Bridge(ip, config_file_path="config.python_hue")
        except PhueRegistrationException:
            input("Press the button on the Hue Bridge and then Enter to continue...")
            b = Bridge(ip, config_file_path="config.python_hue")
        return b

# {
#     "id": 
#     {
#         xy = 0 # [x, y] color value
#         ct = 0 # color temperature
#         hs = 0 # [hue, saturation]
#         br = 0 # brightness
#         mode = hs|xy|ct # light mode
#         reachable = True # whether the light was reachable the last time
#     }  
# }

def monitor(b):
    last_lighting = {}
    if isfile("last_lighting.json"):
        with open("last_lighting.json") as last_lighting_file:
            last_lighting = json.load(last_lighting_file)
    while True:
        print("here")
        lights = b.get_light_objects()
        last_lighting_dirty = False
        for light in lights:
            last_light = None
            light_uid = b.get_light(light.light_id, "uniqueid")
            if not light_uid in last_lighting:
                last_lighting[light_uid] = {}
                last_light = last_lighting[light_uid]             
                last_light["xy"] = light.xy
                last_light["ct"] = light.colortemp
                last_light["hs"] = [light.hue, light.saturation]
                last_light["br"] = light.brightness
                last_light["on"] = light.on
                last_light["mode"] = light.colormode
                last_lighting_dirty = True
            else:
                last_light = last_lighting[light_uid]
                if light.colortemp == 366 and light.brightness == 254:
                    if last_light["ct"] == 366 and last_light["br"] == 254: 
                        continue

                    light.brightness = last_light["br"]
                    if last_light["mode"] == "xy":
                        light.xy = last_light["xy"]
                    elif last_light["mode"] == "hs":
                        light.hue = last_light["hs"][0]
                        light.saturation = last_light["hs"][1]
                    elif last_light["mode"] == "ct":
                        light.colortemp = last_light["ct"]
                    light.on = last_light["on"]
                else:
                    if (last_light["xy"] != light.xy or 
                        last_light["hs"][0] != light.hue or
                        last_light["hs"][1] != light.saturation or
                        last_light["ct"] != light.colortemp or
                        last_light["br"] != light.brightness or
                        last_light["on"] != light.on or
                        last_light["mode"] != light.colormode):

                        if light.colortemp == 366 and light.brightness == 254:
                            continue

                        last_light["xy"] = light.xy
                        last_light["ct"] = light.colortemp
                        last_light["hs"] = [light.hue, light.saturation]
                        last_light["br"] = light.brightness
                        last_light["on"] = light.on
                        last_light["mode"] = light.colormode
                        last_lighting_dirty = True
        if last_lighting_dirty:
            with open("last_lighting.json", "w") as last_lighting_file:
                json.dump(last_lighting, last_lighting_file, indent=4)
        sleep(1)

if __name__ == "__main__":
    b = connect_bridge()
    monitor(b)