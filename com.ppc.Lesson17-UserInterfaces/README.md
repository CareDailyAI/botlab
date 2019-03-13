# Lesson 17 : Delivering content from bots to UIs

Please reach out to the developers if you would like a tutorial on delivering content to user interfaces.

Bots can save some addressable state information in the form of raw JSON content which apps and UI's can retrieve. 

To leverage this, please check out com.ppc.Bot/locations/location.py. This Location object contains the method:

    location_object.set_ui_content(self, botengine, address, json_content)
    
The UI must know the address to pull data from, and typically the bot developers agree with the UI developers in advance about an address to use and the structure of JSON content to generate.
 
This allows bots to generate reports and deliver "bot-only" information directly into native user interfaces.