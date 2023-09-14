# Health Device Class Information

For biometric device data please refer to Confluence: https://presence.atlassian.net/wiki/spaces/INNOVATION/pages/1246560257/Biometrics+Innovations

Supplementary guide on coordinating device types and data through HealthKit: https://docs.google.com/presentation/d/13hqgAYUUQYcIGR2bOPNp-1FzH-s8Ld-S/edit?usp=sharing&ouid=107351607473737521351&rtpof=true&sd=true

# Associated models

- com.ppc.Bot/devices/health.py
- com.ppc.Bot/devices/health_apple.py
- com.ppc.BotProprietary/signals/health_apple.py
- com.ppc.Microservices/intelligence/health/device_healthtrends_microservice.py
- com.ppc.Microservices/intelligence/health/location_health_microservice.py
- com.ppc.Microservices/intelligence/health/location_healthuser_microservice.py
- com.ppc.Microservices/intelligence/movements/location_movements_microservice.py

# Synthetic APIs

## Location States

- health_users

## Data Streams

- set_health_user
- set_user_position

# Analytics

- health_movement_suspected_unconfirmed
- health_no_movement_suspected
- health_{alert_type}
- health_movement_enabled
- health_movement_disabled
- health_movement_confirmed_alert
- health_movement_confirmed_noalert
- health_movement_resolved

# Apple Health References

- https://en.wikipedia.org/wiki/List_of_iPhone_models
- https://en.wikipedia.org/wiki/List_of_iPad_models
- https://en.wikipedia.org/wiki/Apple_Watch
- https://en.wikipedia.org/wiki/IPod_Touch

