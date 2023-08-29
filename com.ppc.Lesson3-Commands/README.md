# Lesson 3 : Commands

By the end of this lesson, you will know how to send commands to controllable devices.

**Don't have a controllable device?** Use a virtual device instead. See the `virtual_devices` directory in this git repository, and run the light bulb Python application.

    cd virtual_devices
    python virtual_light_bulb.py -b <brand>

## Sending commands to devices

Commands are provided through methods that are directly through device objects. 

Explore the `com.ppc.Bot/devices/` directory for a list of devices. A subset of these devices provide commands:

* **com.ppc.Bot/devices/camera/camera_peoplepower_presence.py**     - Provides control methods for all cameras provided by your smartphone app (use your spare smartphone as a security camera).
    * play_sound(self, botengine, sound)
    * play_countdown(self, botengine, audio_seconds, visual_seconds)
    * play_sound_and_countdown(self, botengine, sound, audio_seconds, visual_seconds)
    * beep(self, botengine, times)
    * alarm(self, botengine, on)
    * capture_image(self, botengine, send_alert=False)
    * set_motion_detection(self, botengine, on)
    * set_motion_sensitivity(self, botengine, sensitivity)
    
* **com.ppc.Bot/devices/light/light.py**                            - Base class for lighting controls (on / off / save / restore / hue / saturation / brightness)
    * save(self, botengine)
    * restore(self, botengine)
    * toggle(self, botengine)
    * on(self, botengine)
    * off(self, botengine)
    * set_brightness(self, botengine, percent)
    * set_saturation(self, botengine, saturation)
    * set_hue(self, botengine, hue)
    * set_red(self, botengine)
    * set_green(self, botengine)
    * set_blue(self, botengine)
    
* **com.ppc.Bot/devices/lock/lock.py**                              - Control smart locks (i.e. Kwikset 916 Smart Lock) (lock / unlock)
    * lock(self, botengine)
    * unlock(self, botengine)

* **com.ppc.Bot/devices/siren/siren_linkhigh.py**                   - Controls People Power sirens (play sounds, blink lights)
    * squawk(self, botengine, warning=False)
    * alarm(self, botengine, on)
    * play_sound(self, botengine, sound_id, strobe, duration_sec)

* **com.ppc.Bot/smartplug/smartplug.py**                            - Base class for smart plug devices (on / off / save / restore)
    * save(self, botengine)
    * restore(self, botengine, reliably=False)
    * on(self, botengine, reliably=False)
    * off(self, botengine, reliably=False)

* **com.ppc.Bot/thermostat/thermostat.py**                          - Base class for thermostat devices (control modes, set points, energy efficiency and demand response policies)
    * set_system_mode(self, botengine, system_mode, reliably=True)
    * set_cooling_setpoint(self, botengine, setpoint_celsius, reliably=True)
    * set_heating_setpoint(self, botengine, setpoint_celsius, reliably=True)
    * record_preferred_home_setpoint(self, botengine)
    * record_preferred_sleep_offset(self, botengine)
    * record_preferred_away_offset(self, botengine)
    * set_demand_response(self, botengine, active, identifier, offset_c)
    * set_energy_efficiency(self, botengine, active, identifier, offset_c=2.4)
    * set_energy_efficiency_away(self, botengine, identifier)
    * set_energy_efficiency_sleep(self, botengine, identifier)
    * increment_energy_efficiency(self, botengine, identifier, max_offset_c=2.4)
    * cancel_all_energy_efficiency(self, botengine)

* **com.ppc.Bot/touchpad/touchpad_peoplepower.py**                  - Touchpad (play sounds, send notifications to the touchpad)
    * play_sound(self, botengine, sound, command_timeout_ms=5000)
    * play_countdown(self, botengine, audio_seconds, visual_seconds, command_timeout_ms=5000)
    * play_sound_and_countdown(self, botengine, sound, audio_seconds, visual_seconds, command_timeout_ms=5000)
    * beep(self, botengine, times, command_timeout_ms=5000)
    * alarm(self, botengine, on, command_timeout_ms=10000)
    * notify_mode_changed(self, botengine, mode, command_timeout_ms=10000)
    * notify(self, botengine, push_content, push_sound, command_timeout_ms=5000)
    
## Retrieving device objects to control

Inside some microservice events, a `device_object` is passed in as an argument when a device does something. This `device_object` can be used directly to send that device a command. 

For example, in a *device microservice* for a light bulb, if the light turns on then and the `device_measurements_updated()` method is called and it passes in a `device_object` as an argument.  This `device_object` would be guaranteed to be a light bulb device because of the nature of how device microservices work. In this device microservice, the `device_object` argument *is* `self.parent`. They're the same thing, and you can use them interchangeably.

Although it's not recommended you control other devices from within a device microservice, you do have access to all other devices in the location by referencing `self.parent.location_object.devices`. The `Location` object's `devices` variable is a Dictionary where the key is a device ID and the object is the device object.

Location microservices are where you should coordinate activities amongst multiple devices within the location. Again, retrieve device objects from the Location object (which is your `self.parent` in the context of a location microservice) by referencing `self.parent.devices`. 


### Explore more

Read through and understand the code and comments in `intelligence/lesson3/location_doorsandlighting_microservice.py`. Copy this bot to your own directory, commit it to the server, and run it.

Run it in the cloud:

    cp -r com.ppc.Lesson3-Commands com.yourname.Lesson3
    botengine --commit com.yourname.Lesson3 -b <brand> -u <user@email.com> -p <password>
    botengine --purchase com.yourname.Lesson3 -b <brand> -u <user@email.com> -p <password>

Watch it run locally:

    botengine --run com.yourname.Lesson3 -b <brand> -u <user@email.com> -p <password>
    
The lesson assumes your account will have lights and/or smart plugs connected at a minimum. Entry sensors are desirable as well.

Tap into AWAY mode from your mobile app or web UI. The microservice will save the state of all your lights and smart plugs, and then turn them off.

Next, tap into HOME mode from your mobile app or web UI. The microservice will then restore all your lights and smart plugs to how they were before you left.

If you open a door, the lights and smart plugs will turn on.  If you close the door, the lights and smart plugs will turn off.

Pause it when you're ready to move on:

    botengine --pause com.yourname.Lesson3 -b <brand> -u <user@email.com> -p <password>