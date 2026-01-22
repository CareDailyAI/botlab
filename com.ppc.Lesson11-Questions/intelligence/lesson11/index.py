# Lesson 11: Questions
#
# This file registers the microservices in this lesson.

MICROSERVICES = {
    "DEVICE_MICROSERVICES": {},
    "LOCATION_MICROSERVICES": [
        {
            "module": "intelligence.lesson11.location_questions_microservice",
            "class": "LocationQuestionsMicroservice",
            "execution_priority": 0,
        }
    ],
}

