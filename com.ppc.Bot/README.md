# FOUNDATIONAL BOT

com.ppc.Bot is a foundational bot which you can extend and build upon in your own bots.

It provides the following features:

* Manages memory automatically. No need to save/load variables.
* Transforms the underlying infrastructure of bots into a nice event-driven framework.
* Provides device definitions for many common device types, along with methods to interact with devices directly.
* Allows developers to focus on creating event-driven microservices and behaviors instead of low-level code.
* Dynamically adds and removes microservices from live bot instances already running in peoples' accounts as new versions and updates of your bot are published.
* Multiplexes timers and alarms infinitely, and provides nice methods to start timers and set alarms.

*Do not try to commit this bot directly.*  This provides a foundation for you to rapidly build your own bot microservices.

To extend this bot foundation, apply the 'extends' attribute in your bot's structure.json file:

    'extends': 'com.ppc.Bot' 
    
When you --generate or --commit your bot, first all of the files from com.ppc.Bot will be copied into a new temporary directory, then all the files from your bot will be copied on top of that directory, allowing you to override and extend all the files in com.ppc.Bot. 