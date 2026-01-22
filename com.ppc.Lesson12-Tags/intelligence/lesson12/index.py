# Lesson 12: Tags
#
# Registers the microservices in this lesson.

MICROSERVICES = {
    "DEVICE_MICROSERVICES": {},
    "LOCATION_MICROSERVICES": [
        {
            "module": "intelligence.lesson12.location_tags_microservice",
            "class": "LocationTagsMicroservice",
            "execution_priority": 0,
        }
    ],
}

