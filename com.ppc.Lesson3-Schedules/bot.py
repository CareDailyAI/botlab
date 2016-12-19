'''
Created on June 11, 2016

@author: David Moss and Destry Teeter

Email support@peoplepowerco.com if you have questions!
'''

# LESSON 3 - SCHEDULES
# Apps can be triggered to run on a recurring basis, using Cron schedules.
# Some of this description is copied from the Quartz Scheduler Documentation. Hope it helps.
# You'll need the 'apscheduler' module installed to run this on your local system. Run this command:
#
#     pip install apscheduler
#
#
# VERSION.JSON
# Open the version.json file, and you'll see we are triggering off of a cron schedule:
#
#    "trigger": 1,
#
# This type of trigger requires the schedule to trigger off of:
#
#    "schedule": "0 0/1 * * * ?",
#
# This schedule says "Fire every minute". Realistically, your bot should avoid such a heavy
# load on the server. But this is good for quick turn-around demonstration purposes.
#
# Cron is a UNIX tool that has been around for a long time, so its scheduling capabilities are
# powerful and proven. A cron expression, like we see in the "schedule" above, is capable of
# firing schedules such as: "At 8:00 AM every Monday through Friday" or "At 1:30 AM every last
# Friday of the month".  Think about using this for weekly recurring summary emails to your users.
#
# CRON FORMAT
# A cron expression is a string comprised of 6 or 7 fields separated by white space. Fields can
# contain any of the allowed values, along with various combinations of the allowed special characters
# for that field. The fields are as follows:
#
# FIELD NAME    MANDATORY?    ALLOWED VALUES    ALLOWED SPECIAL CHARS
# Seconds       Yes           0-59              , - * /
# Minutes       Yes           0-59              , - * /
# Hours         Yes           0-23              , - * /
# Day of Month  Yes           1-31              , - * ? / L W
# Month         Yes           1-12 or JAN-DEC   , - * /
# Day of Week   Yes           1-7 or SUN-SAT    , - * ? / L #
# Year          NO            empty, 1970-2099  , - * /
#
# So cron expression can be as simple as this:
#
#     * * * * ? *
#
# Or more complex like this:
#
#     0/5 14,18,3-39,52 * ? JAN,MAR,SEP MON-FRI 2016-2030
#
# SPECIAL CHARACTERS
# * ("all values") used to select all values within a field.
#   For example, "" in the minute field means "every minute".
#
# ? ("no specific value") useful when you need to specify something in one of the two fields
#   in which the character is allowed, but not the other. For example, if I want my trigger to
#   fire on a particular day of the month (say, the 10th), but don't care what day of the week that
#   happens to be, I would put "10" in the day-of-month field, and "?" in the day-of-week field.
#   See the examples below for clarification.
#
#   Pay attention to the effects of '?' and '*' in the day-of-week and day-of-month fields!
#
# - used to specify ranges.
#   For example, "10-12" in the hour field means "the hours 10, 11 and 12".
#
# , used to specify additional values.
#   For example, "MON,WED,FRI" in the day-of-week field means "the days Monday, Wednesday, and Friday".
#   The legal characters and the names of months and days of the week are not case sensitive. MON is the same as mon.
#
# / used to specify increments.
#   For example, "0/15" in the seconds field means "the seconds 0, 15, 30, and 45".
#   And "5/15" in the seconds field means "the seconds 5, 20, 35, and 50".
#
# L ("last") has different meaning in each of the two fields in which it is allowed.
#   For example, the value "L" in the day-of-month field means "the last day of the month".
#   Day 31 for January, day 28 for February on non-leap years. If used in the day-of-week
#   field by itself, it simply means "7" or "SAT".
#   But if used in the day-of-week field after another value, it means "the last xxx day of the month".
#   For example "6L" means "the last Friday of the month". You can also specify an offset from the last
#   day of the month, such as "L-3" which would mean the third-to-last day of the calendar month.
#   When using the 'L' option, it is important not to specify lists, or ranges of values, as you'll get
#   confusing/unexpected results.
#
# W ("weekday") used to specify the weekday (Monday-Friday) nearest the given day.
#   As an example, if you were to specify "15W" as the value for the day-of-month field, the meaning
#   is: "the nearest weekday to the 15th of the month". So if the 15th is a Saturday, the trigger will
#   fire on Friday the 14th. If the 15th is a Sunday, the trigger will fire on Monday the 16th. If the
#   15th is a Tuesday, then it will fire on Tuesday the 15th. However if you specify "1W" as the value for
#   day-of-month, and the 1st is a Saturday, the trigger will fire on Monday the 3rd, as it will not 'jump'
#   over the boundary of a month's days. The 'W' character can only be specified when the day-of-month
#   is a single day, not a range or list of days.
#
#   The 'L' and 'W' characters can also be combined in the day-of-month field to yield 'LW', which translates to *"last weekday of the month"*.
#
# # used to specify "the nth" XXX day of the month.
#   For example, the value of "6#3" in the day-of-week field means "the third Friday of the month" (day 6 = Friday and "#3" = the 3rd one in the month).
#   Other examples: "2#1" = the first Monday of the month and "4#5" = the fifth Wednesday of the month.
#   Note that if you specify "#5" and there is not 5 of the given day-of-week in the month, then no firing will occur that month.
#
#
#
#
# EXAMPLES
#   0 0 12 * * ?    Fire at 12pm (noon) every day
#   0 15 10 ? * *    Fire at 10:15am every day
#   0 15 10 * * ?    Fire at 10:15am every day
#   0 15 10 * * ? *    Fire at 10:15am every day
#   0 15 10 * * ? 2005    Fire at 10:15am every day during the year 2005
#   0 * 14 * * ?    Fire every minute starting at 2pm and ending at 2:59pm, every day
#   0 0/5 14 * * ?    Fire every 5 minutes starting at 2pm and ending at 2:55pm, every day
#   0 0/5 14,18 * * ?    Fire every 5 minutes starting at 2pm and ending at 2:55pm, AND fire every 5 minutes starting at 6pm and ending at 6:55pm, every day
#   0 0-5 14 * * ?    Fire every minute starting at 2pm and ending at 2:05pm, every day
#   0 10,44 14 ? 3 WED    Fire at 2:10pm and at 2:44pm every Wednesday in the month of March.
#   0 15 10 ? * MON-FRI    Fire at 10:15am every Monday, Tuesday, Wednesday, Thursday and Friday
#   0 15 10 15 * ?    Fire at 10:15am on the 15th day of every month
#   0 15 10 L * ?    Fire at 10:15am on the last day of every month
#   0 15 10 L-2 * ?    Fire at 10:15am on the 2nd-to-last last day of every month
#   0 15 10 ? * 6L    Fire at 10:15am on the last Friday of every month
#   0 15 10 ? * 6L    Fire at 10:15am on the last Friday of every month
#   0 15 10 ? * 6L 2002-2005    Fire at 10:15am on every last Friday of every month during the years 2002, 2003, 2004 and 2005
#   0 15 10 ? * 6#3    Fire at 10:15am on the third Friday of every month
#   0 0 12 1/5 * ?    Fire at 12pm (noon) every 5 days every month, starting on the first day of the month.
#   0 11 11 11 11 ?    Fire every November 11th at 11:11am.
#
#
# NOTES
# Support for specifying both a day-of-week and a day-of-month value is not complete (you must currently use the '?' character in one of these fields).
#
# Be careful when setting fire times between the hours of the morning when "daylight savings" changes occur in your locale (for US locales,
# this would typically be the hour before and after 2:00 AM - because the time shift can cause a skip or a repeat depending on whether the time moves back or
# jumps forward.
#
# You may find this wikipedia entry helpful in determining the specifics to your locale:
# https://secure.wikimedia.org/wikipedia/en/wiki/Daylight_saving_time_around_the_world
#
#

# RUNNING THIS BOT
# First, register your developer account at http://presto.peoplepowerco.com.
#
# There are several steps needed to run this bot:
#    1. Create a new directory for your bot, with your own unique bundle ID. Copy all the files into it.
#       Note that bundle ID's are always reverse-domain notation (i.e. com.yourname.YourBot) and cannot
#       be deleted or edited once created.
#    2. Create a new --bot on the server with botengine
#    3. Commit your bot to the server with botengine
#    4. Purchase your bot with botengine
#    5. Run your bot locally
#
#
# We've automated this for you with a script, 'runlesson.sh'. Run it from your terminal window:
#
#    $ ./runlesson.sh
#
#
# This script will automatically do the following for you.
# From a terminal window *above* this bot's current directory:
#
# 1. Create a new directory for your bot with your given bundle ID, and copy all the files from this
#    lesson into that new directory.
#
#
# 2. Commit your bot to the server.
#    This will push all the code, version information, marketing information, and icon to the server.
#    The bot will become privately available.
#
#    botengine --commit com.yourname.YourBot
#
#
# 3. Purchase the bot as if you're an end-user. Note that because your bot is privately available, other end users
#    will not be able to see or access it.
#
#    botengine --purchase com.yourname.YourBot
#
#    This will return a unique instance ID for your purchased bot, which you may reference to reconfigure the bot instance later.
#
#
# 4. Run the bot locally.
#
#    botengine --run com.yourname.YourBot
#
#    This will automatically look up your bot instance ID and run the bot, using the real-time streaming data from the server
#    and the code that is on your local computer.
#

import datetime

def run(botengine):
    '''This is the execution starting point of your bot

    @param botengine: Instance of the BotEngine object, which provides built-in functions for you to privately interact with this user's data
    @param initialize: True if we should initialize this bot for the given deviceId, and perhaps clear variables
    '''

    logger = botengine.get_logger()
    inputs = botengine.get_inputs()              # Get the inputs to this bot from BotEngine

# This is what my inputs look like when the bot runs. Pretty sparse.
#
# {
#   'trigger': 1,
#   'time': 1465683540431
# }

    unixTimeMs = int(inputs['time'])
    unixTimeSec = unixTimeMs / 1000             # Convert to seconds, to later feed into the datetime converter

    print("\nExecuting on schedule")
    print("\t=> Unix timestamp in milliseconds = " + str(unixTimeMs))
    print("\t=> Human readable timestamp: " + datetime.datetime.fromtimestamp(unixTimeSec).strftime('%Y-%m-%d %H:%M:%S'))
