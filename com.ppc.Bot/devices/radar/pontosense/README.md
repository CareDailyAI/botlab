# Pontosense SilverShield Device Class Information

The Pontosense SilverShield device uses radar to extract occupancy, fall, and target information from an environment. It can be used to monitor for fall events and transitions through a space, and provides detailed measurement parameters for integration and analytics.

## Device Parameters

The following measurement names are supported and available as attributes in the device class:

- `bedStatus`: Bed occupancy status
- `fallStatus`: Fall detection status (`0` = no fall, `1` = fall detected)
- `firmware`: Firmware version string
- `model`: Model identifier
- `occupancy`: General occupancy status
- `occupancyTarget`: Targeted occupancy status (with indices: `bedin`, `couchin`, `fall`, `pfall`, `other`)
- `pnt.fallThreshold`: Fall detection threshold
- `pnt.scanHeight`: Scan height in centimeters
- `pnt.scanLeft`: Scan left boundary in centimeters
- `pnt.scanRight`: Scan right boundary in centimeters
- `pnt.unit`: Pontosense unit identifier
- `rssi`: Signal strength indicator
- `status`: Device status (`0` = normal, `1` = error, `2` = alignment)

## Device Class

The main device class is `RadarPontosenseDevice`, which inherits from `RadarDevice`. It provides:

- Measurement parameter constants for all supported measurements
- Methods for setting and retrieving room boundaries and subregions
- Methods for fall detection and threshold configuration
- Device compatibility for type `2007` (Pontosense SilverShield)

## Room Boundaries

Room boundaries are managed in meters, but described on the device in centimeters, and can be set or retrieved using the device API. The device supports only corner installation, and the following boundaries are used:

- `x_min_meters`, `x_max_meters`: Left boundaries (default 6.0, min is always 0.0)
- `y_min_meters`, `y_max_meters`: Right boundaries (default 6.0, min is always 0.0)
- `z_min_meters`, `z_max_meters`: Distance face out from the device (always 6.0)
- `sensor_height_m`: Height of the sensor (default min: 2.0, max: 2.2)

## Occupancy Target Indices

The device supports multiple occupancy target indices for advanced use cases:

- `bedin`
- `couchin`
- `fall`
- `pfall`
- `other`

## Fall Detection

- `fallStatus`: `"0"` for no fall, `"1"` for fall detected
- Fall threshold can be configured between 0 and 300 seconds

## Subregions [WIP]

The device supports up to 6 subregions for advanced tracking and detection. Subregions follow the same coordinate system as the room boundaries.

## Device Status

- `0`: Normal
- `1`: Error
- `2`: Alignment

## Signal Strength

- `rssi`: Signal strength, with a low signal warning threshold at -70 dBm

---

For further details on device configuration, refer to the class docstrings and method
