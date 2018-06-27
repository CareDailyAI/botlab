MICROSERVICES = {
    # Map specific device types to a list of microservices
    "DEVICE_MICROSERVICES": {
        # Gateways
        10031: [
            {"module": "intelligence.daylight.device_daylight_microservice", "class": "DaylightMicroservice"},
            ],

        # Gateways
        31: [
            {"module": "intelligence.daylight.device_daylight_microservice", "class": "DaylightMicroservice"},
            ],
        },

}