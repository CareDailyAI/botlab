# Vayyar Device Class Information

The Vayyar Care device uses radar to extract occupancy and target information from an environment.  It can be used to monitor for fall events and transitions through a space.

The Vayyar Care device has a 135 degree viewing angle, and a 3D X/Y/Z coordinate system. Do not install it facing directly at a mirror.

## Device Mounting

The device is mounted (1) to the wall 5 feet off the ground to the center of the device or (2) on the ceiling at a 45 degree rotation.

### Wall

Facing out into the room from the device for a wall installation:
* **X-axis** = left/right, and the center of the Vayyar Care is 0 (so left is a negative number). Maximum to the left is -3.0 meters. Maximum to the right is 2.0 meters.
* **Y-axis** = forward in front of the device. Again, center of the Vayyar Care is 0. There are no negative numbers here. Maximum is 4.0 meters. Minimum is 0.3 meters
* **Z-axis** = up/down in the room. The device should always be 1.5 meters off the ground (~5 feet off the ground to the center of the device). The ceiling might be 2.5 to 3 meters high.

**Offset**: A wall installation may be offset 1 meter along the X-axis to the left of the device.  The total distance along the X-axis must be adjusted so that it is 4.0 meters or less.

## Configurating Boundaries

* vyrc.xMin = room boundary to the left of the Vayyar Care.         xMin < xMax
* vyrc.xMax = room boundary to the right of the Vayyar Care.        xMax > xMin
* vyrc.yMin = room boundary directly in front of the Vayyar Care.   yMin < yMax
* vyrc.yMax = room boundary farthest from the Vayyar Care.          yMax > yMin
* vyrc.zMin = room boundary at floor height (0 meters).             zMin < zMax
* vyrc.zMax = room boundary at ceiling height (2.5 meters ).        zMax > zMin
* vyrc.sensorHeight = height off the ground (1.5 meters).
* vyrc.sensorMounting = Wall - Vayyar Care sensor is mounted on a wall (0 Enum)

### Ceiling

Standing under the vayyar with the cable leading infront and to the left at 45 degrees:
* **X-axis** = left/right, and the center of the Vayyar Care is 0 (so left is a negative number). Maximum to the left is -2.0 meters. Maximum to the right is 2.0 meters.
* **Y-axis** = forward/backward, and the center of the Vayyar Care is 0 (so behind you is a negative number). Maximum is 3.0 meters. Minimum is 3.0 meters
* **Z-axis** = up/down in the room. The ceiling might be 2.5 to 3 meters high.

**Offset**: A ceiling installation may be offset 0.5 meters along the Y-axis in either direction.  The total distance along the Y-axis must be adjusted so that it is 5.0 meters or less.

## Configuring Boundaries

* vyrc.xMin = room boundary to the left of the Vayyar Care.     xMin < xMax
* vyrc.xMax = room boundary to the right of the Vayyar Care.    xMax > xMin
* vyrc.yMin = room boundary infront of the Vayyar Care.         yMin < yMax
* vyrc.yMax = room boundary behind of the Vayyar Care.          yMax > yMin
* vyrc.zMin = room boundary at floor height (0 meters).         zMin < zMax
* vyrc.zMax = room boundary at ceiling height (2.5 meters).     zMax > zMin
* vyrc.sensorMounting = Ceiling45Deg - Device is mounted on ceiling at a 45 degree angle (2 Enum)

# Device settings

## Configuration

All units are in meters unless "cm" is specified.

* vyrc.fallingSensitivity = Default: 1, Enum: 0 1 2
  * NoFalling - No fall alerts will be sent when falling sensitivity is set to NoFalling
  * LowSensitivity - fall alerts will be sent if the height of the target before the fall is at least 1.2 meters from zMin
  * RegularSensitivity - fall alerts will be sent if the height of the target before the fall is at least 0.7 meters from zMindetect a person sitting low or laying on the ground)
* vyrc.maxTargetsForFallingTrigger = 0 (not supported / reserved for future use)
* vyrc.confirmedToAlertTimeoutSec = Usually set to 30 seconds
* vyrc.ledMode = 0 is "all off"; 1 is "all on"
* vyrc.volume = 100 means the buzzer is enabled upon fall confirmed state; 0 = buzzer is always off
* vyrc.telemetryPolicy = Telemetry information is used for debugging and this capability must be supported in order to investigate algorithmic issues. The telemetry should be captured in bin files per frame (see API for telemetry data). Telemetries should be enabled in coordination with Vayyar. We don’t recommend enabling constantly as this amounts to a very large amount of data. Default: "OnFall"
  * 0 : Telemetry is Off
  * 1 : Telemetry is always On
  * 2 : Telemetry is on during fall event (Recommended Default value)
  * 3 : Telemetry is on while presence is detected in the arena
* vyrc.presenceReportMinRateMills = The time interval in milliseconds between presence reports. Used when tracker data is required for constant reporting. These messages are in addition to the reporting mentioned above (falls/ presence) which is done on a change state. Default: 60000
* vyrc.silentMode = This value is sent as-is in the fall event JSON and has no effect on the buzzer
* vyrc.enterDuration = The minimum detection time required to establish presence in the arena, in seconds. Default: 120
* vyrc.exitDuration = The minimum detection time required to establish non-presence in the arena, in seconds. Default: 120
* vyrc.durationUntilConfirm = Time in seconds from fall_detected to fall_confirmed. Default: 52
* vyrc.minTimeOfTarInFallLoc = The minimum number of seconds that the target should be detected in the fall location after fall detection to reach the fall confirmed state. This value should be set to 0.6 * durationUntilConfirm. Default: 30
* vyrc.dryContactActivationDuration = The time in seconds that the dry contact will be activated when a fall is detected. Default: 30
* vyrc.fallingMitigatorEnabled = Enable falling mitigator (V40 and above). Use machine learning to reduce false alarm rates by up to 50%.  May reduce true alarm rates by up to 5%. Default: false
* vyrc.aboveThPointTelemetry above th point telemetry for skeleton data (V40 and above). Default: false
* vyrc.offlineMode = When offline mode is set to true, the device will not reboot if losses the Wi-Fi or internet connectivity. When offline mode is set to false, the device will reboot automatically after 5 minutes of MQTT disconnection. Note: daily reboot / OTA check will keep performing every 24 hours. Default: true
* vyrc.callingDurationSec = This is the time in seconds that the device stays in the ‘calling’ state. Default: 30
* vyrc.learningModeEnd = Refers to the time that the learning period ends. When Learning mode is activated this should be ‘NOW’ + the amount of milliseconds in the learning period (2 week). End of learning mode in milliseconds. The device in learning mode may behave differently to allow data collection for the sensitivity map. The device should be on silent mode and fall events shouldn’t cause alerts in the customer view. Default: "learningModeStartTs + 14 * 1000 * 60 * 60 * 24"
* vyrc.testMode = Enables test mode. To test during learning mode, the user should activate test mode. When learning and test mode are activated at the same time, the data will be marked and ignored in the sensitivity map creation. Default: "false"
* vyrc.dryContacts = “primary” and “secondary”
  * object (Dry Contact Config)
    * mode = number (DryContactMode) Default: "ActiveHigh" Enum: 0 1
      * 0 - "ActiveLow" - For use with a normally closed circuit. The dry contact alert is triggered when the circuit is open.
      * 1 - "ActiveHigh" - For use with a normally open circuit. The dry contact alert is triggered when the circuit is closed.
    * policy = number (DryContactPolicy) Default: "Off" Enum: 0 1 2 3 4. determines when a dry contact alert will be triggered.
      * Off - no dry contact alert
      * OnFall - in the event of a fall, the dry contact alert will be triggered when the device reaching the calling stage
      * OutOfBed - In an out of bed event the dry contact will be triggered
      * OnSensitiveFall - in the event of a target on the ground fall, the dry contact alert will be triggered when the device reaching the calling stage
      * OnAnyFall “in the event of either a standard fall or a target on the ground fall, the dry contact alert will be triggered when the device reaching the calling stage.
* vyrc.demoMode = When demoMode is set to true, fall_detected and fall_confirmed times are each 10sec, so time to calling is 20sec. Not to be used for deployment, only client demonstrations. Default: false
* vyrc.doorEvents = When set to 'True', enables the user to receive event messages when a target exit the room (Empty room) or enters the room, this feature requires setting upto 2 subregions with isDoor set to true and isLowSnr set to false. Default: false
* vyrc.outOfBed = When set to True, the device will report Empty bed (out of bed) event in the first defined subregion, the subregion must be defined as low SNR subregion - set IsLowSNR to true. Default: false
* vyrc.sensitiveMode = Enable the target on the ground alerts. Default: false
* vyrc.sensitivityLevel = suspected fall events with a confidence level that is above this threshold are considered human falls. Default: 0.78
* vyrc.minEventsForFirstDecision = minimum number of 'fall_suspected' events required in a chain to detect a fall and trigger a 'calling' event. Default: 5
* vyrc.detectionsInChain = minimum number of human falls in chain to detect fall. Human falls are defined as falls that are detected with a confidence which is above the set 'sensitivityLevel' parameter. Default: 4

# Subregions

Subregions follow the same coordinate system as the vayyar boundaries.

* vyrc.trackerSubRegions = Array of objects (Tracker Sub Regions)
  * xMin = Default: 0
  * xMax = Default: 1
  * yMin = Default: 0.3
  * yMax = Default: 1
  * zMin = Default: 0
  * zMax = Default: 1.2
  * enterDuration = The minimum detection time required to establish presence in the subregion, in seconds. Note: This parameter does not influence the time of Door Events (V40 and above). Default: 120
  * exitDuration = The minimum detection time required to establish non-presence in the subregion, in seconds. Note: This parameter does not influence the time of Door Events (V40 and above). Default: 120
  * isFallingDetection = True - Detect fall in the subregion; False - Exclude fall in the subregion. Default: false
  * isPresenceDetection = Default: true
  * isLowSnr = allows for better tracking of targets in a subregion with lower energy (low SNR). Default: true
  * isDoor = up to two subregions can be configured as doors by setting isDoor to True. When enableDoorEvents is true, isLowSNR must be set to false. Default: false
  * name = Meaningful name of the subregion, e.g. Bed / Door / Toilet
