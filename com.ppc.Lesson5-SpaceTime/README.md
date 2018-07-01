# Lesson 5 : SpaceTime

By the end of this lesson you will understand:

* How time is conveyed throughout the bot microservices architecture
* How to start a relative timer
* How to set an absolute alarm
* Methods that help manage and localize time to the user's geographic location and timezone

## Get the current time

Time is always conveyed in milliseconds since the unix epoch. For each execution of the bot service, you extract the timestamp in milliseconds from the `botengine` object:

    botengine.get_timestamp()
    
The timestamp provided by the `botengine` is the time at which the trigger really occurred, which may be several tens of milliseconds in the past. Using this timestamp throughout the execution of your bot makes it appear as if your bot is executing at a single moment in time.

## Timers and Alarms

You can have near-infinite alarms and timers in this framework. When an alarm or timer fires, it fires only into the microservice that started it.

### Start a Timer

Timers are relative from the point of time provided by `botengine.get_timestamp()`. You can start a timer in units of seconds or in units of milliseconds. The timer methods are provided as a convenience inside the `Intelligence` class (`com.ppc.Bot/intelligence/intelligence.py`) which every microservice extends. This allows your microservice to call, for example, `self.start_timer_s(...)` to start a timer.

Here are some methods your microservice can call for timers, provided by the `Intelligence` class:

* **self.start_timer_ms(botengine, milliseconds, argument=None, reference="")** : Start a timer in units of milliseconds.
    * *botengine* = BotEngine environment object
    * *milliseconds* = Number of milliseconds, relative to botengine.get_timestamp(), to fire the timer.
    * *argument* = Optional. Any object, tuple, list, dictionary, number, etc. you want to pop out on the other side when the timer fires.
    * *reference* = Optional. Provide a string to reference this timer later, allowing you to see if it's running or cancel it. If left blank, a default reference is applied.
    
* **self.start_timer_s(botengine, seconds, argument=None, reference="")** : Start a timer in units of seconds.
    * *botengine* = BotEngine environment object
    * *seconds* = Number of milliseconds, relative to botengine.get_timestamp(), to fire the timer.
    * *argument* = Optional. Any object, tuple, list, dictionary, number, etc. you want to pop out on the other side when the timer fires.
    * *reference* = Optional. Provide a string to reference this timer later, allowing you to see if it's running or cancel it. If left blank, a default reference is applied.
    
* **self.is_timer_running(botengine, reference="")** : Check if a timer with the given reference is actively running.
    * *botengine* = BotEngine environment object
    * *reference* = Reference for the timer. If left blank, a default reference is applied.
    
* **self.cancel_timers(botengine, reference="")** : Cancel all timers with the given reference.
    * *botengine* = BotEngine environment object
    * *reference* = Reference for the timer. If left blank, a default reference is applied.
    
If the relative time is in the past, the bot will trigger immediately and fire the `timer_fired(...)` method.
    
### Set an Alarm

**Alarms are actually timers**, but provided for convenience as a way to trigger at an absolute timestamp instead of a relative amount of time.

Here are some methods your microservice can call for alarms, provided by the `Intelligence` class:

* **self.set_alarm_ms(botengine, timestamp_ms, argument=None, reference="")** : Set an alarm to fire at the given absolute timestamp.
    * *botengine* = BotEngine environment object
    * *milliseconds* = Number of milliseconds, relative to botengine.get_timestamp(), to fire the timer.
    * *argument* = Optional. Any object, tuple, list, dictionary, number, etc. you want to pop out on the other side when the timer fires.
    * *reference* = Optional. Provide a string to reference this timer later, allowing you to see if it's running or cancel it. If left blank, a default reference is applied.
    
* **self.is_alarm_running(botengine, reference="")** : Check if an alarm with the given reference is actively running.
    * *botengine* = BotEngine environment object
    * *reference* = Reference for the alarm. If left blank, a default reference is applied.
    
* **self.cancel_alarm(botengine, reference="")** : Cancel all alarms with the given reference.
    * *botengine* = BotEngine environment object
    * *reference* = Reference for the alarm. If left blank, a default reference is applied.
    
If the timestamp is in the past, the bot will trigger immediately and fire the `timer_fired(...)` method.


### Handling a Timer or Alarm fires

When the timer or alarm fires, they will both trigger this event (because underneath, they are both timers):

* **def timer_fired(self, botengine, argument)** : A timer OR alarm fired.
    * *botengine* = BotEngine environment object
    * *argument* = Any argument passed in while setting the timer or alarm

Your job is to react to this event.

If you need multiple arguments passed into the `timer_fired(...)` event, one trick is to use a `tuple` to inject multiple arguments into the `argument` field. 

## Datetimes and Timezones

The `Location` object provides helper methods to extract the user's timezone and other interesting time-related attributes based on their approximate geographic location. Remember, you can access your `Location` object from a *location microservice* by calling `self.parent`, or from a *device microservice* by calling `self.parent.location_object`.

Here are some methods in your `Location` object that you may find useful:

* **get_local_datetime(self, botengine)** : Get the current time as a Datetime object in the user's local timezone.

* **get_local_datetime_from_timestamp(self, botengine, timestamp_ms)** : Transform a timestamp in milliseconds into a local datetime object.

* **get_local_timezone_string(self, botengine)** : Retrieve the user's local timezone string

* **get_relative_time_of_day(self, botengine, timestamp_ms=None)** : Used primarily to power machine learning algorithms, this method will transform either the current time or a given timestamp in milliseconds into a `float` of the format `hours.minutes` where the minutes is divided by 60. For example, 10:15 AM will transform into the `float` 10.25.

* **get_midnight_last_night(self, botengine)** : Returns a Datetime object representing midnight *last night* in the user's local timezone.

* **get_midnight_tonight(self, botengine)** : Returns a Dateimte object representing midnight *tonight* in the user's local timezone.

* **local_timestamp_ms_from_relative_hours(self, botengine, weekday, hours)** : Returns an absolute timestamp in milliseconds from a given relative day-of-the-week (Monday is 0) and relative hour-of-the-day (for example, `float` 23.5 = 11:30 PM local time).

* **timezone_aware_datetime_to_unix_timestamp(self, botengine, dt)** : Returns a unix timestamp from a local timezone-aware Datetime object.

* **get_local_hour_of_day(self, botengine)** : Returns the current local hour-of-the-day as a `float`, typically used in machine learning algorithms. For example, midnight last night is `0.0`. Noon is `12.0`. And 9:15 PM is `21.25`.

* **get_local_day_of_week(self, botengine)** : Returns the current local day of the week from 0 - 6.



## Explore More

Check out the following microservices in this lesson:

* `intelligence/lesson5/device_entrytimer_microservice.py` : Starts a 10-second timer when a door opens. Cancels the timer if the door closes.

* `intelligence/lesson5/device_alarm_microservice.py` : Sets an alarm for midnight tonight when your mode changes.


Run it in the cloud: 
    
    cp -r com.ppc.Lesson5-SpaceTime com.yourname.Lesson5
    botengine --commit com.yourname.Lesson5 -b <brand> -u <user@email.com> -p <password>
    botengine --purchase com.yourname.Lesson5 -b <brand> -u <user@email.com> -p <password>
    
Watch it run locally:

    botengine --run com.yourname.Lesson5 -b <brand> -u <user@email.com> -p <password>
    
Toggle your user account into a different mode, and the alarm will be set for midnight. You'll get a bunch of command line output when running locally that demonstrates some helper methods from the `Location` object.

Open an entry sensor and leave it open for more than 10 seconds. The timer will fire if the door has been left open for too long, and you'll receive a push notification.

