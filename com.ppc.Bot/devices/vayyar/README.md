Button Press - "button_press" alert

vyrc.trackerSubRegions parameter - the JSON format is exactly as is shown in the Vayyar API documentation. We have to provide the entire array every time.

    [
           {
                "enterDuration": 1,
                "exitDuration": 3,
                "isFallingDetection": false,
                "isPresenceDetection": true,
                "xMax": 1,
                "xMin": 0,
                "yMax": 1,
                "yMin": 0.3
          }
    ]

The Vayyar Home device has a 135 degree viewing angle, and a 3D X/Y/Z coordinate system. Do not install it facing directly at a mirror.

The device is mounted to the wall 5 feet off the ground to the center of the device.

Facing out into the room from the device:
* **X-axis** = left/right, and the center of the Vayyar Home is 0 (so left is a negative number). Maximum to the left is -1.9 meters, maximum to the right is 1.9 meters.
* **Y-axis** = forward in front of the device. Again, center of the Vayyar Home is 0. There are no negative numbers here. Maximum is 3.9 meters.
* **Z-axis** = up/down in the room. The device should always be 1.5 meters off the ground (~5 feet off the ground to the center of the device). The ceiling might be 2.5 to 3 meters high.
 
All units are in meters unless "cm" is specified.

* vyrc.xMin = room boundary to the left of the Vayyar Home (max is -1.9 meters)
* vyrc.xMax = room boundary to the right of the Vayyar Home (max is +1.9 meters)
* vyrc.yMin = closest distance in front of the Vayyar Home (I see this sometimes starts at 0.3 meters / 1 foot)
* vyrc.yMax = farthest distance in front of the Vayyar Home.
* vyrc.zMin = floor height (0 meters)
* vyrc.zMax = ceiling height (2.5 meters for example)
* vyrc.sensorHeight = height off the ground (usually 1.5 meters always)
* vyrc.fallingSensitivity = 1 is low sensitivity (will only detect a fall if the person is lying flat on the ground, more resilient to false alarms); 2 = regular sensitivity (will detect a person sitting low or laying on the ground)
* vyrc.fallingTrigger = 0 (always)
* vyrc.maxTargetsForFallingTrigger = 0 (not supported / reserved for future use)
* vyrc.confirmedToAlertTimeoutSec = Usually set to 30 seconds
* vyrc.ledMode = 0 is "all off"; 1 is "all on"
* vyrc.volume = 100 means the buzzer is enabled upon fall confirmed state; 0 = buzzer is always off
* vyrc.telemetryPolicy = 0 is off; 1 is on; 2 is only on falls (default)
* vyrc.presenceReportMinRateMills = presence reporting rate in milliseconds
* vyrc.silentMode = True or False
* vyrc.targetPositionChangeThresholdMeters = meters
