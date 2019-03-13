# Lesson 10 : Machine Learning

This lesson will demonstrate some examples and best practices for implementing your own time-series machine learning services.

The bot itself is not meant to be fully functional because the prediction algorithm at the bottom of the stack is stubbed out and left as an exercise for you to explore your own ML algorithm implementation. It does demonstrate the mindset of professional machine learning developers / data scientists as we strive to create best-in-class AI services on top of time-series data.

## Requesting Data

Machine learning algorithms are hungry for data. Any services enablement platform optimized for machine learning AI services must provide smooth mechanisms for extracting large amounts of data from a deployment.

Requesting large amounts of data from the server with `botengine.get_measurements()` is *strongly discouraged* and services caught using this method to extract large amounts of data will be banned. This method is very forceful in extracting data from the databaser, and doesn't play nicely with all the other bots that may also be trying to extract data. Imagine writing a bot that wakes up at midnight to recalculate machine learning models. And then that bot gets deployed into 400,000 user accounts. At midnight, all 400,000 bots wake up and attempt to extract all data from the database - you've just DDoS'd your own service.

The much more intelligent method to extract large amounts of data is with an asynchronous data request. This is performed with the following method:

    def request_data(self, device_id, oldest_timestamp_ms=None, newest_timestamp_ms=None, param_name_list=None, reference=None, index=None, ordered=1):
        """
        Selecting a large amount of data from the database can take a significant amount of time and impact server
        performance. To avoid this long waiting period while executing bots, a bot can submit a request for all the
        data it wants from this location asynchronously. The server gathers all the data on its own time, and then
        triggers the bot with trigger 2048. Your bot must include trigger 2048 to receive the trigger.

        Selected data becomes available as a file in CSV format, compressed by LZ4, and stored for one day.
        The bot receives direct access to this file.

        You can call this multiple times to extract data out of multiple devices. The request will be queued up and
        the complete set of requests will be flushed at the end of this bot execution.

        :param device_id: Device ID to download historical data from
        :param oldest_timestamp_ms: Oldest timestamp in milliseconds
        :param newest_timestamp_ms: Newest timestamp in milliseconds
        :param param_name_list: List of parameter names to download
        :param reference: Reference so when this returns we know who it's for
        :param index: Index to download when parameters are available with multiple indices
        :param ordered: 1=Ascending (default); -1=Descending.
        """
        
The request goes into the server, the server crunches on it for awhile, and later the bot gets triggered with trigger 2048 to deliver the requested data.

## Architecture 

We may have multiple microservices that want to create machine learning models, leveraging all the data in a Location. To make things easy and keep our server loads to a minimum, we have a `data_request` microservice package that is responsible for requesting consistent data that automatically gets shared throughout the microservices framework.

Take a look at the local `structure.json` file. It pulls in two microservice packages:
    
        "microservices": [
            "com.ppc.Microservices/intelligence/data_request",
            "com.ppc.Microservices/intelligence/absent_ml_example"
        ],
        


### data_request microservice package
The `data_request` microservice package wakes up at least once per week and downloads all data from the location, safely. The microservice accepts `download_data` data stream messages to cause it to download all data now (faster than the default once-per-week schedule), and will cause the `data_request_ready()` event to trigger throughout the microservice framework. The microservice uses the reference `"all"` when making a data request, allowing all other microservices to recognize when all of the user's data was downloaded by the `data_request` microservice.

In general, as the lifestyle patterns of people are cyclical on a weekly basis, we download and recalculate all machine learning models once per week.

Note the `data_request/runtime.json` file includes trigger 2048 to trigger off of data request responses, and increases the default memory usage to 1536 MB. This makes your bot a bit more expensive to run.

The `data_request/structure.json` file includes the `lz4` package, because the historical time-series CSV data from a user's account becomes available as a set of LZ4-compressed files. As a developer, you never have to see this because the decompression is taken care of at a level below the `data_request_ready()` event.

### absent_ml_example microservice package

The `absent_ml_example` is an example microservice package that trains a set of models to form predictions about whether a location is currently occupied or unoccupied. It is an example of a specific machine learning service which would leverage all of the data in the user's account to produce models.

## Absent Machine Learning Service

In this example, we demonstrate the thought process of implementing a time-series machine learning algorithm to classify whether a home is occupied or empty. The issue requiring a machine learning solution is this: Two people are asleep in bed in the morning. One person gets up and goes to work, while the other person remains asleep in bed. Based on the activity sensors throughout the home, the house looks completely empty: no movement, no lights turning on, no water running. The only way to know the house is actually still occupied is to defer to machine learning models generated on historical data. Machine learning algorithms fill in the gaps in the current data.

When a door closes, either you're inside the house or you're out. We define a list that contains durations, in minutes after the last door closed, to ask the machine learning models for their prediction about whether the home is empty or not. 

Each week, the `data_request` microservice wakes up and requests all the data from this Location. This results in a `data_request_ready()` event, which is triggered in all other microservices including the `absent_ml_example` microservice. 

Once triggered, machine learning models are created for each duration of time since the last door closed, based on all historical data in the home. "Labels" are automatically generated by the ML algorithm model generation functions without user input by looking for a fingerprint of the house being empty: a door closed, there was no activity for at least 15 minutes, and then a door opened. 

The models themselves are stored in their own non-volatile variables (using `botengine.save_variable()`) instead of a class variable, because it could be very large and it is not needed on every execution. Class variables (i.e. `self.variable`) are stored and loaded from memory on every execution of the bot.

When a door closes, we wait for each prescribed duration of time in minutes to evaluate the current conditions against the machine learning model. There is one model generated per time duration.

For full disclosure, this occupancy sensing machine learning service is patent pending People Power Company, although we didn't disclose all of the concepts and mechanisms that apply in the commercial-grade service. Hope this helps get you started in the world of time-series machine learning AI services.