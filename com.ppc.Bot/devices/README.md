# Devices

To remove a class of device and potentially replace it with another,
use the initialize() method in the device class to change its instance's 
device_id - for example, set it to None.

Upon the next execution, the bot.py will load the controller which will
initialize(). The device_id gets set to None. Then the controller
synchronizes devices. It loads the previous device instances
and if an instance's device_id is not in our list of devices,
it gets safely deleted.

