# Lesson 7 : Sunrise / Sunset

By the end of this lesson you will know:

* How to include microservices from external microservices packages.
* How to listen and react to sunrise / sunset data stream messages in your microservices.

## Daylight microservice package

The sunrise and sunset events are powered by a `daylight` microservice package, found in `com.ppc.Microservices/intelligence/daylight`. This is a self-describing microservice package, because it has a `runtime.json`, a `structure.json`, and an `index.py`.

The `daylight` microservice is currently powered by a Python package called `ephem`. This Python package contains some native libraries, so it must be compiled on the native architecture it will run on. If you look at `com.ppc.Microservices/intelligence/daylight/structure.json`, you'll see that `ephem` is included as a Python package to be installed remotely (at the server) with `pip_install_remotely`. The cloud server will automatically download, compile, and install the Python package into your bot remotely to complete the commit process. Because the `daylight` microservice self-describes which Python packages it needs to run, you don't need to think about it elsewhere. 

Include the entire `daylight` microservice package in your `structure.json` file:
    
    {
      # This bot extends a foundational bot framework for microservices
      "extends": "com.ppc.Bot",
    
      # Share microservices across multiple bots by copying the target end-directory into the local /intelligence directory
      "microservices": [
            "com.ppc.Microservices/intelligence/daylight"
      ],
    
      # Locally install the following Python package dependencies when using this microservice
      # Do not include any Python packages in this list that will compile .so/.dll library files natively
      # because they may not be able to run on the Linux-based server environment.
      "pip_install": [
      ],
    
      # Remotely install the following Python package dependencies
      # This will compile library files at the server in a Linux environment.
      # Note that when installed on Linux, some Python packages may get significantly inflated (like scipy and numpy)
      # due to the addition of hidden .libs directories that end up exceeding the maximum size of a bot
      # (50MB compressed / 250MB uncompressed).
      "pip_install_remotely": [
      ]
    
    }

You can open the local `structure.json` file to see this self-describing microservice being imported into the project.


### How we find sunrise and sunset

Each device that directly connects to the cloud server has an external IP address which the server can read. The server looks up the approximate geographic location of that IP address, which produces a latitude and longitude accurate to approximately a 5-10 mile radius. Latitude and Longitude is then injected into the `ephem` Python library to calculate today's sunrise and sunset timestamps. Alarms are set inside the `daylight` microservice for those absolute times, and then data stream messages are distributed inside your bot to any microservice that cares to listen and react to them.

### Sunrise and Sunset data stream messages

The data stream messages distributed by the `daylight` microservice will contain a `proxy_id` in the content dictionary. A gateway is a proxy which other devices connect through to talk to the server. 

Because you can have multiple gateways in your account, and those gateways could physically be located in different parts of the world, it's important to make sure each device that may react to sunrise or sunset are actually connecting through the gateway that is experiencing sunrise or sunset. Check this by comparing the proxy_id of your device with the proxy_id provided by the sunrise/sunset data stream messages.


#### sunrise_fired
Data Stream Message declaring it is sunrise at the location of one of your gateways. Message contents include:

* `content['proxy_id']` : The ID of the proxy (gateway) where sunrise is taking place right now.
    
#### sunset_fired
Data Stream Message declaring it is sunset at the location of one of your gateways. Message contents include:

* `content['proxy_id']` : The ID of the proxy (gateway) where sunset is taking place right now.
    

## Reacting to Sunrise / Sunset

First fill in your `datastream_updated(...)` method to forward data stream messages to internal methods if they exist.


    def datastream_updated(self, botengine, address, content):
        """
        Data Stream Message Received
        :param botengine: BotEngine environment
        :param address: Data Stream address
        :param content: Content of the message
        """
        # Forward 'sunrise_fired' and 'sunset_fired' data stream messages to the appropriate methods in this class
        if hasattr(self, address):
            getattr(self, address)(botengine, content)


Then create methods for the `sunrise_fired` and `sunset_fired` data stream messages:


    def sunrise_fired(self, botengine, content=None):
        """
        Data stream message from the internal 'daylight' microservice indicating it is now sunrise.
        :param botengine: BotEngine environment
        :param content: Data stream message content - a dictionary containing "proxy_id"
        """
        
        # It's always good practice to write defensive code like this.
        if 'proxy_id' not in content:
            # Malformed data stream message.
            return

        # DO SOMETHING


    def sunset_fired(self, botengine, content=None):
        """
        Data stream message from the internal 'daylight' microservice indicating it is now sunset.
        :param botengine: BotEngine environment
        :param content: Data stream message content - a dictionary containing "proxy_id"
        """
        
        # It's always good practice to write defensive code like this.
        if 'proxy_id' not in content:
            # Malformed data stream message.
            return

        # DO SOMETHING
        
        
You should verify the device that might react to sunrise or sunset events has the same proxy_id as described in the data stream messages:

    # DEVICE MICROSERVICE EXAMPLE : Checking the proxy_id of your parent device
    # Your device microservice's parent is a single device object. Check its proxy_id.
    if self.parent.proxy_id == content['proxy_id']:
        # It is sunrise or sunset where your device is located.
        self.parent.do_something(botengine)
 
    # LOCATION MICROSERVICE EXAMPLE : Checking proxy_id's of each device in the location
    # Loop through each device in your location and check its proxy_id.
    for device_id in self.parent.devices:
        if self.parent.devices[device_id].proxy_id == content['proxy_id']:
            # It is sunrise or sunset where this device is located.
            self.parent.do_something(botengine)
            

## Explore More

Check out the following microservices in this lesson:

* `intelligence/lesson7/device_lighting_microservice.py` : Turns on each light at sunset, turns off each light at sunrise

* `intelligence/lesson7/location_lighting_microservice.py` : Sends you a single push notification when it is sunrise or sunset


Run it in the cloud: 
    
    cp -r com.ppc.Lesson7-SunriseSunset com.yourname.Lesson7
    botengine --commit com.yourname.Lesson7 -b <brand> -u <user@email.com> -p <password>
    botengine --purchase com.yourname.Lesson7 -b <brand> -u <user@email.com> -p <password>
    
Watch it run locally:

    botengine --run com.yourname.Lesson7 -b <brand> -u <user@email.com> -p <password>
    
This one requires you to just let it run and play out until a sunrise or sunset event happens. Remember that if you leave it running in the cloud, as a developer you'll have 24 hours before the bot automatically pauses. You can `botengine --play` it again to keep it going.
