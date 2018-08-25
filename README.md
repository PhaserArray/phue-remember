# phue-remember
A simple python script for my raspberry pi to make the philips hue lights remember what state they were in when power is toggled for the bulbs. This should also work if both the pi and lights lose power due to an outage as the lighting is saved to a file, you just have to make sure the python script auto-runs.


# Warning
Due to the fact that it takes reachable up to 10 seconds to update, I had to check for the light color temperature and brightness instead. That means you can't use color temperature 366 and brightness 254 as your normal lighting, legitimatelly switching to that will still make the script change the lights back to whatever they were before. **The work around is simple, either your color temp or brightness has to be different by at least 1. I don't use that temperature anyways as it is too warm in my opinion so it works fine for me.