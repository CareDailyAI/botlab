# Lesson 1 : Microservices

Welcome to the world of bot microservices. The first real lesson here is the most involved, but once you get through it then you can more or less rapidly create your own bot-drive smart home services.

By the end of this lesson, you will learn the following:
* How to commit, purchase, and run bots.
* You'll watch your bot execute live and react to new data from sensors and mode changes (Home, Away, Stay, etc.) from UIs.
* Explain key files and what they do: runtime.json, structure.json, index.py
* Understand differences between a 'Device Microservice' and a 'Location Microservice'

It is assumed that you know some basic Python and object-oriented concepts (see tutorials at [http://python.org]). 

## Run this lesson in your account

The process of creating and running a bot is similar to the process of mobile app development:

1. Develop code for a new bot on your local computer by copy/pasting an existing bot into a new directory and editing it. 
2. You `--commit` the bot to your smart home's cloud server, with the user account you already established. Now the bot is in 'developer mode'. You, as the developer, are the only person who can see it available for purchase. Once committed, it's like a blueprint or a class - it doesn't really exist until you instantiate it by purchasing it into your user account.
3. You `--purchase` the bot into your account. This doesn't necessarily mean there's money involved, but it is to say there's an explicit transaction to get the bot into your account. This makes an instance of the bot, running live in your user account on the server. As a developer, if you don't directly interact with your bot for at least 24 hours, it will automatically pause itself. By purchasing your bot into your own developer account, now you are able to test it and run it live in the cloud or locally on your computer for debugging.
4. You `--publish` the bot when it's ready for commercial release. The bot goes through a review process and is approved or rejected (with reasons) from People Power. If approved for distribution, then other users will be able to discover and purchase your bot.

You can also `--run` your bot locally, if you have the source code on your laptop. Which you should, if you have cloned this 'botlab' repository.

We will explore the contents of the files in this lesson in a moment. For now, let's get it committed and running.

[![Commit, Purchase, and Run Video](https://user-images.githubusercontent.com/1031168/42250532-61d235b0-7ee6-11e8-97a6-8ca1b38571e7.gif)](https://youtu.be/fbLv2KG7Xmw)

### Step 1 : Copy Lesson 1 into a new bot directory

Every bot has a unique name in reverse domain name notation (com.yourname.YourService). Once you `--commit` your bot, you permanently own that unique name. Choose wisely.

Copy the entire com.ppc.Lesson1-Microservices directory structure recursively into a new directory. Give yours a good name:

    cp -r com.ppc.Lesson1-Microservices com.yourname.Lesson1
    
We will explore the contents and the guts of this lesson in a moment. 


### Step 2 : Commit the bot to the server

Now it's time to commit your bot into your own developer account on the server:

    botengine --commit com.yourname.Lesson1 -b <brand>
    
Once committed, the server now has a blueprint of your bot service. This bot is privately available for you to purchase into your own developer account, but not available for other users to discover, purchase, or run.

    botengine --commit com.yourname.Lesson1 -b presence
    
    Presence by People Power
    Bot Server: https://app.presencepro.com
    Uploading the marketing file...
    Uploading the runtime configuration...
    Generating the bot...
    Ignoring files (add more in your .botignore file): 
    ['.botignore', '.DS_Store', 'icon.png', '.redirect', 'pylint.sh', '*.py_', '*.vm', '*.sh', '*.png', 'i18n.sh', '*.pyc']
    Locally installed packages: ['python-dateutil', 'dill', 'requests', 'tzlocal']
    Remotely installed packages: []
    Uploading the bot [6MB]...
    Uploading the icon...
    Processing the bot at the server.......
    Purchase this bot into your personal account (y/n)? 


### Step 3 : Purchase your bot for free

When you 'purchase' a bot into your account, you're not necessarily paying money for it. You are creating an instance of the bot from its blueprint, and it immediately begins running privately in your own account. 3rd party developers cannot see your data or contact information, and you have control over what the bot can do in your account. Privacy by design.

Either answer 'y' to the question about *'Purchase this bot into your personal account (y/n)?'* or purchase it explicitly:

    botengine --purchase com.yourname.Lesson1 -b <brand>
    
You can verify which bots have been purchased into your account:

    botengine --my_purchased_bots -b <brand>
    
And you can verify and review which bots were developed by you:

    botengine --my_developer_bots -b <brand>
    
    
### Step 4 : Run your bot locally

When you run your bot locally, you're actually forming a bi-directional connection with the smart home cloud server to receive real-time data and send back commands from the bot. The execution of the bot migrates from the cloud to your computer. When you stop running the bot locally, then the cloud will automatically start running the bot again in about a minute.

You must have your bot's source code locally available to run it on your computer. This lets you edit the source code, run the bot, and watch the changes in behavior in real-time.

    botengine --run com.yourname.Lesson1 -b <brand>
    
When your bot begins running locally, you'll see the following output to your Terminal window:

    botengine --run com.yourname.Lesson1 -b presence
    
    Presence by People Power
    Bot Server: https://app.presencepro.com
    Device Server: https://esp.peoplepowerco.com:8443
    Running forever, until you press CTRL+Z to quit

As you make changes to your bot, you do not need to commit your bot each time! Edit some code, exit the bot, run the bot. It will begin running your new code immediately on your local computer. The only time you need to commit the bot during the development cycle is when you alter your runtime.json files, which tell the server what data your bot should listen to.

### Step 5 : Shortcuts

When you interact with the 'botengine' file, you must pass in your username and password and brand/server. It's a slog to type that in every. single. time. I know.

Here's the pro way to handle this. Create environment variables in your Terminal's startup scripts (like ~/.profile, ~/.bash_rc, or ~/.bash_profile, etc.) to capture your credentials:

    export USER="-u email@address.com -p password -b brand"
    
*Personal note: I prefer my last name (MOSS) instead of USER, and I separate the brand into its own environment variable so I can hop from server to server effortlessly.*

Now when you run your botengine, just type `$USER` at the end to automatically inject your username, password, and brand:

    botengine --my_purchased_bots $USER
    
or using my own preferred style:

    botengine --my_purchased_bots $MOSS $BRAND
    
Remember this means your password is obviously not secure. Writing it in clear text file and using it in your command line terminal is obviously a dumb thing to do... but not if you are the only person in control of your computer. You're in charge of your own security, and it's up to you to throttle your privacy comfort level with the use of that password. If you don't give a password through the command line, you'll be securely prompted for a password every time. Your choice. 


#### Stimulate your bot to watch it react

If you have a smart home pack of products attached to your account, you'll see the bot execute every time data is produced by one of your sensors. Open an entry sensor, walk in front of a motion sensor, turn on a smart plug or light bulb. Open your smart home's app and toggle between HOME and AWAY modes. Anything you do in your smart home ecosystem, the bot will execute and react live on your computer using the source code you now control.

**Don't have any devices?** No problem. Included in this repository is a Python application `virtual_devices/virtual_light_switch.py`. Run it like this:

    cd virtual_devices
    python virtual_light_switch.py -b <brand>
    
This will add a virtual light switch device to your account (our server thinks it is a real device). When you toggle the virtual light switch on and off, you'll see your bot triggering and executing, reacting to the data flowing in real-time.

#### What happens when your bot is running

Unlike active applications on your computer, active bots do not run all the time. They go to sleep whenever possible - which technically means they exit and stop executing. That would normally mean you lose all your variables between executions, but the bot microservices framework by People Power takes care of that for you and makes it appear as if your bot never exits. It just keeps running. Thank you, bot microservices framework. 

Imagine if you had 10 million users and each of them had a python application that needed to run. Now imagine you have a computer (or in the case of a cloud server - a cluster of computers) running those applications. Can you imagine, even on a large body of computers, having 10 million applications open and running simultaneously? Ya, right. If you don't believe me, try opening a even just a few hundred applications on your own computer and see how that goes. This is why the bots run and exit completely. Your job, as the developer, is to make the bots trigger infrequently and get done executing quickly to free up CPU time for other bots to run.

Bots run when they are triggered. A **trigger** is any data or timer input that causes the bot to execute. In a moment, we'll see how the `runtime.json` files declare what your bot should listen to and trigger off of. Your bot gets triggered, does some work, and exits immediately. That's the basic way to think about it.


## Bot anatomy

It's important to understand some key files and concepts related to the bot.

### com.ppc.Bot

[![Foundational Bot Video](https://user-images.githubusercontent.com/1031168/42354060-16040cd2-8079-11e8-9bf8-b864b19087e4.gif)](https://www.youtube.com/watch?v=ygOqO2gvTvk)

You could start by creating your own bot literally from scratch. The only requirement of a bot from a Python perspective is that you implement a bot.py file in your root directory, and that the `bot.py` file contains a `run(botengine)` function. But that's a very low level to start with.

What you really want is to form a *representative model* of the home and all the devices in it, organized automatically for you. You need useful methods to extract critical information about the home and interact directly with devices without understanding each device's API. You need a way to start timers and set alarms effortlessly. You need memory managed for you instead of saving and loading variables each time your bot executes.

*Today is your lucky day.* What we call the "Foundational Bot", `com.ppc.Bot`, does all this for you and more. And we've open sourced it for you.

The `com.ppc.Bot` doesn't actually do anything behaviorally. It's a foundation to build new behaviors - *microservices* - on top of. This bot (Lesson 1) and all other bots we create here are built on top of that easy-to-use foundation, saving you hundreds of hours of development. We'll learn next how we build a new bot on top of the `com.ppc.Bot` foundation.

There are 2 key files to pay attention to inside the `com.ppc.Bot` directory: `com.ppc.Bot/locations/location.py` (which defines the `Location` object) and `com.ppc.Bot/devices/device.py` (which devices the `Device` object which every class of device extends).

**Homework Assignment** : Your microservices will interact with the Location and Device classes directly. Browse through the contents of both the `locations/location.py` file and the `devices/device.py` file to gain a basic understanding of what class variables they store, and what methods they provide.


![Bot Architecture](https://user-images.githubusercontent.com/1031168/42341513-227052f4-8048-11e8-8d61-13c074fdf1e1.png)

### structure.json

[![Structure Video](https://user-images.githubusercontent.com/1031168/42354025-d3cbb66c-8078-11e8-952f-7f9e8ad2e361.gif)](https://www.youtube.com/watch?v=PGCQz0Dm7ow)

As the name implies, the structure.json files describe how to structure the directories/files that compose the bot. It also describes which Python package dependencies are required for your bot to run (and the microservices in it).

The structure.json file exists in the root directory of your bot, and other copies of it can exist throughout the microservices that compose your project. When your bot gets generated through a `botengine --generate <bot>` or `botengine --commit <bot>` command, all structure.json files in the project get merged together.

**Homework Assignment**: Find the structure.json files in your Lesson 1 directory, read them, and understand them. There are at least 2.

#### Generate your bot

To see the structure.json file in action, `--generate` your bot and check out the directory that is created (no username/password is needed because this doesn't interact with the server):

    botengine --generate com.yourname.Lesson1
    
This will generate a directory called `.com.yourname.Lesson1` in your local working directory. It might be a hidden directory - see the '.' at the front? If you look at the contents of this newly generated bot, you'll find that it looks almost nothing like the contents of the original `com.ppc.Lesson1-Microservices` bot we started with. That's because the `structure.json` file `"extends": "com.ppc.Bot"`. First, a new directory is created, called `.com.yourname.Lesson1`. Next, all the contents from `com.ppc.Bot` are copied into that directory. Finally, all the contents from `com.yourname.Lesson1` are copied on top of that directory. This is how the files in your bot end up sitting on top of the foundational bot `com.ppc.Bot`.

Open the resulting `structure.json` file inside the newly generated bot directory. You'll see its contents are very different than we started with, containing only the `pip_install` and `pip_install_remotely` attributes. Because the directory/file structure of the bot is already taken care of, your `structure.json` file no longer needs the `extends` or `microservices` attributes found in the original `structure.json` file, and only needs the Python package dependency information to make the bot fully functional.

### runtime.json

[![Runtime Video](https://user-images.githubusercontent.com/1031168/42354024-d3b547f6-8078-11e8-9793-f0d765f7030d.gif)](https://www.youtube.com/watch?v=5Mod8nD0V3Q)

The `runtime.json` file is responsible for describing to the server how to actually run your bot. There can be multiple `runtime.json` files in your bot and its microservices, and they all get merged together when you `--generate` or `--commit` the bot.

The `runtime.json` file describes to the server:
* Version number of the bot, whose format (x.y.z) is strongly enforced and must always increment with every *published* bot on the server.
* Description of "What's New?" in the latest version of the bot.
* What data inputs to trigger off of.
* Which device types to listen for and how.
* What data stream messages to allow into the bot.
* Cron schedules to periodically trigger off of.
* Permissions needed to access certain services or data about the home.
* Who we want to communicate with and how.
* Maximum memory needed to allocate for the bot when it's running (memory * execution time = $).
* How long to allow the bot to run before forcefully killing it.
* Maximum number of copies a user may have of this bot.

**Homework Assignment** : Find the runtime.json files in your Lesson 1 directory, read them, and understand them. There are at least 2.

For your convenience, we have maximized the scope of the `runtime.json` file in your `lesson1` microservice package, meaning they'll listen to and trigger off of *all* devices and data sources. It's a good place to start, but is likely triggering off of far more data than you'll ever use in your bot. The objective of any good bot developer is to minimize the data your bot needs to listen to.

### index.py

[![Run# Lesson 1 : Microservices

Welcome to the world of bot microservices. The first real lesson here is the most involved, but once you get through it then you can more or less rapidly create your own bot-drive smart home services.

By the end of this lesson, you will learn the following:
* How to commit, purchase, and run bots.
* You'll watch your bot execute live and react to new data from sensors and mode changes (Home, Away, Stay, etc.) from UIs.
* Explain key files and what they do: runtime.json, structure.json, index.py
* Understand differences between a 'Device Microservice' and a 'Location Microservice'

It is assumed that you know some basic Python and object-oriented concepts (see tutorials at [http://python.org]). 

## Run this lesson in your account

[![Commit, Purchase, and Run Video](https://user-images.githubusercontent.com/1031168/42250532-61d235b0-7ee6-11e8-97a6-8ca1b38571e7.gif)](https://youtu.be/fbLv2KG7Xmw)

The process of creating and running a bot is similar to the process of mobile app development:

1. Develop code for a new bot on your local computer by copy/pasting an existing bot into a new directory and editing it. 
2. You `--commit` the bot to your smart home's cloud server, with the user account you already established. Now the bot is in 'developer mode'. You, as the developer, are the only person who can see it available for purchase. Once committed, it's like a blueprint or a class - it doesn't really exist until you instantiate it by purchasing it into your user account.
3. You `--purchase` the bot into your account. This doesn't necessarily mean there's money involved, but it is to say there's an explicit transaction to get the bot into your account. This makes an instance of the bot, running live in your user account on the server. As a developer, if you don't directly interact with your bot for at least 24 hours, it will automatically pause itself. By purchasing your bot into your own developer account, now you are able to test it and run it live in the cloud or locally on your computer for debugging.
4. You `--publish` the bot when it's ready for commercial release. The bot goes through a review process and is approved or rejected (with reasons) from People Power. If approved for distribution, then other users will be able to discover and purchase your bot.

You can also `--run` your bot locally, if you have the source code on your laptop. Which you should, if you have cloned this 'botlab' repository.

We will explore the contents of the files in this lesson in a moment. For now, let's get it committed and running.

### Step 1 : Copy Lesson 1 into a new bot directory

Every bot has a unique name in reverse domain name notation (com.yourname.YourService). Once you `--commit` your bot, you permanently own that unique name. Choose wisely.

Copy the entire com.ppc.Lesson1-Microservices directory structure recursively into a new directory. Give yours a good name:

    cp -r com.ppc.Lesson1-Microservices com.yourname.Lesson1
    
We will explore the contents and the guts of this lesson in a moment. 


### Step 2 : Commit the bot to the server

Now it's time to commit your bot into your own developer account on the server:

    botengine --commit com.yourname.Lesson1 -b <brand>
    
Once committed, the server now has a blueprint of your bot service. This bot is privately available for you to purchase into your own developer account, but not available for other users to discover, purchase, or run.

    botengine --commit com.yourname.Lesson1 -b presence
    
    Presence by People Power
    Bot Server: https://app.presencepro.com
    Uploading the marketing file...
    Uploading the runtime configuration...
    Generating the bot...
    Ignoring files (add more in your .botignore file): 
    ['.botignore', '.DS_Store', 'icon.png', '.redirect', 'pylint.sh', '*.py_', '*.vm', '*.sh', '*.png', 'i18n.sh', '*.pyc']
    Locally installed packages: ['python-dateutil', 'dill', 'requests', 'tzlocal']
    Remotely installed packages: []
    Uploading the bot [6MB]...
    Uploading the icon...
    Processing the bot at the server.......
    Purchase this bot into your personal account (y/n)? 


### Step 3 : Purchase your bot for free

When you 'purchase' a bot into your account, you're not necessarily paying money for it. You are creating an instance of the bot from its blueprint, and it immediately begins running privately in your own account. 3rd party developers cannot see your data or contact information, and you have control over what the bot can do in your account. Privacy by design.

Either answer 'y' to the question about *'Purchase this bot into your personal account (y/n)?'* or purchase it explicitly:

    botengine --purchase com.yourname.Lesson1 -b <brand>
    
You can verify which bots have been purchased into your account:

    botengine --my_purchased_bots -b <brand>
    
And you can verify and review which bots were developed by you:

    botengine --my_developer_bots -b <brand>
    
    
### Step 4 : Run your bot locally

When you run your bot locally, you're actually forming a bi-directional connection with the smart home cloud server to receive real-time data and send back commands from the bot. The execution of the bot migrates from the cloud to your computer. When you stop running the bot locally, then the cloud will automatically start running the bot again in about a minute.

You must have your bot's source code locally available to run it on your computer. This lets you edit the source code, run the bot, and watch the changes in behavior in real-time.

    botengine --run com.yourname.Lesson1 -b <brand>
    
When your bot begins running locally, you'll see the following output to your Terminal window:

    botengine --run com.yourname.Lesson1 -b presence
    
    Presence by People Power
    Bot Server: https://app.presencepro.com
    Device Server: https://esp.peoplepowerco.com:8443
    Running forever, until you press CTRL+Z to quit

As you make changes to your bot, you do not need to commit your bot each time! Edit some code, exit the bot, run the bot. It will begin running your new code immediately on your local computer. The only time you need to commit the bot during the development cycle is when you alter your runtime.json files, which tell the server what data your bot should listen to.

### Step 5 : Shortcuts

When you interact with the 'botengine' file, you must pass in your username and password and brand/server. It's a slog to type that in every. single. time. I know.

Here's the pro way to handle this. Create environment variables in your Terminal's startup scripts (like ~/.profile, ~/.bash_rc, or ~/.bash_profile, etc.) to capture your credentials:

    export USER="-u email@address.com -p password -b brand"
    
*Personal note: I prefer my last name (MOSS) instead of USER, and I separate the brand into its own environment variable so I can hop from server to server effortlessly.*

Now when you run your botengine, just type `$USER` at the end to automatically inject your username, password, and brand:

    botengine --my_purchased_bots $USER
    
or using my own preferred style:

    botengine --my_purchased_bots $MOSS $BRAND
    
Remember this means your password is obviously not secure. Writing it in clear text file and using it in your command line terminal is obviously a dumb thing to do... but not if you are the only person in control of your computer. You're in charge of your own security, and it's up to you to throttle your privacy comfort level with the use of that password. If you don't give a password through the command line, you'll be securely prompted for a password every time. Your choice. 


#### Stimulate your bot to watch it react

If you have a smart home pack of products attached to your account, you'll see the bot execute every time data is produced by one of your sensors. Open an entry sensor, walk in front of a motion sensor, turn on a smart plug or light bulb. Open your smart home's app and toggle between HOME and AWAY modes. Anything you do in your smart home ecosystem, the bot will execute and react live on your computer using the source code you now control.

**Don't have any devices?** No problem. Included in this repository is a Python application `virtual_devices/virtual_light_switch.py`. Run it like this:

    cd virtual_devices
    python virtual_light_switch.py -b <brand>
    
This will add a virtual light switch device to your account (our server thinks it is a real device). When you toggle the virtual light switch on and off, you'll see your bot triggering and executing, reacting to the data flowing in real-time.

#### What happens when your bot is running

Unlike active applications on your computer, active bots do not run all the time. They go to sleep whenever possible - which technically means they exit and stop executing. That would normally mean you lose all your variables between executions, but the bot microservices framework by People Power takes care of that for you and makes it appear as if your bot never exits. It just keeps running. Thank you, bot microservices framework. 

Imagine if you had 10 million users and each of them had a python application that needed to run. Now imagine you have a computer (or in the case of a cloud server - a cluster of computers) running those applications. Can you imagine, even on a large body of computers, having 10 million applications open and running simultaneously? Ya, right. If you don't believe me, try opening a even just a few hundred applications on your own computer and see how that goes. This is why the bots run and exit completely. Your job, as the developer, is to make the bots trigger infrequently and get done executing quickly to free up CPU time for other bots to run.

Bots run when they are triggered. A **trigger** is any data or timer input that causes the bot to execute. In a moment, we'll see how the `runtime.json` files declare what your bot should listen to and trigger off of. Your bot gets triggered, does some work, and exits immediately. That's the basic way to think about it.


## Bot anatomy

It's important to understand some key files and concepts related to the bot.

### com.ppc.Bot

[![Foundational Bot Video](https://user-images.githubusercontent.com/1031168/42354060-16040cd2-8079-11e8-9bf8-b864b19087e4.gif)](https://www.youtube.com/watch?v=ygOqO2gvTvk)

You could start by creating your own bot literally from scratch. The only requirement of a bot from a Python perspective is that you implement a bot.py file in your root directory, and that the `bot.py` file contains a `run(botengine)` function. But that's a very low level to start with.

What you really want is to form a *representative model* of the home and all the devices in it, organized automatically for you. You need useful methods to extract critical information about the home and interact directly with devices without understanding each device's API. You need a way to start timers and set alarms effortlessly. You need memory managed for you instead of saving and loading variables each time your bot executes.

*Today is your lucky day.* What we call the "Foundational Bot", `com.ppc.Bot`, does all this for you and more. And we've open sourced it for you.

The `com.ppc.Bot` doesn't actually do anything behaviorally. It's a foundation to build new behaviors - *microservices* - on top of. This bot (Lesson 1) and all other bots we create here are built on top of that easy-to-use foundation, saving you hundreds of hours of development. We'll learn next how we build a new bot on top of the `com.ppc.Bot` foundation.

There are 2 key files to pay attention to inside the `com.ppc.Bot` directory: `com.ppc.Bot/locations/location.py` (which defines the `Location` object) and `com.ppc.Bot/devices/device.py` (which devices the `Device` object which every class of device extends).

**Homework Assignment** : Your microservices will interact with the Location and Device classes directly. Browse through the contents of both the `locations/location.py` file and the `devices/device.py` file to gain a basic understanding of what class variables they store, and what methods they provide.


![Bot Architecture](https://user-images.githubusercontent.com/1031168/42341513-227052f4-8048-11e8-8d61-13c074fdf1e1.png)

### structure.json

[![Structure Video](https://user-images.githubusercontent.com/1031168/42354025-d3cbb66c-8078-11e8-952f-7f9e8ad2e361.gif)](https://www.youtube.com/watch?v=PGCQz0Dm7ow)

As the name implies, the structure.json files describe how to structure the directories/files that compose the bot. It also describes which Python package dependencies are required for your bot to run (and the microservices in it).

The structure.json file exists in the root directory of your bot, and other copies of it can exist throughout the microservices that compose your project. When your bot gets generated through a `botengine --generate <bot>` or `botengine --commit <bot>` command, all structure.json files in the project get merged together.

**Homework Assignment**: Find the structure.json files in your Lesson 1 directory, read them, and understand them. There are at least 2.

#### Generate your bot

To see the structure.json file in action, `--generate` your bot and check out the directory that is created (no username/password is needed because this doesn't interact with the server):

    botengine --generate com.yourname.Lesson1
    
This will generate a directory called `.com.yourname.Lesson1` in your local working directory. It might be a hidden directory - see the '.' at the front? If you look at the contents of this newly generated bot, you'll find that it looks almost nothing like the contents of the original `com.ppc.Lesson1-Microservices` bot we started with. That's because the `structure.json` file `"extends": "com.ppc.Bot"`. First, a new directory is created, called `.com.yourname.Lesson1`. Next, all the contents from `com.ppc.Bot` are copied into that directory. Finally, all the contents from `com.yourname.Lesson1` are copied on top of that directory. This is how the files in your bot end up sitting on top of the foundational bot `com.ppc.Bot`.

Open the resulting `structure.json` file inside the newly generated bot directory. You'll see its contents are very different than we started with, containing only the `pip_install` and `pip_install_remotely` attributes. Because the directory/file structure of the bot is already taken care of, your `structure.json` file no longer needs the `extends` or `microservices` attributes found in the original `structure.json` file, and only needs the Python package dependency information to make the bot fully functional.

### runtime.json

[![Runtime Video](https://user-images.githubusercontent.com/1031168/42354024-d3b547f6-8078-11e8-9793-f0d765f7030d.gif)](https://www.youtube.com/watch?v=5Mod8nD0V3Q)

The `runtime.json` file is responsible for describing to the server how to actually run your bot. There can be multiple `runtime.json` files in your bot and its microservices, and they all get merged together when you `--generate` or `--commit` the bot.

The `runtime.json` file describes to the server:
* Version number of the bot, whose format (x.y.z) is strongly enforced and must always increment with every *published* bot on the server.
* Description of "What's New?" in the latest version of the bot.
* What data inputs to trigger off of.
* Which device types to listen for and how.
* What data stream messages to allow into the bot.
* Cron schedules to periodically trigger off of.
* Permissions needed to access certain services or data about the home.
* Who we want to communicate with and how.
* Maximum memory needed to allocate for the bot when it's running (memory * execution time = $).
* How long to allow the bot to run before forcefully killing it.
* Maximum number of copies a user may have of this bot.

**Homework Assignment** : Find the runtime.json files in your Lesson 1 directory, read them, and understand them. There are at least 2.

For your convenience, we have maximized the scope of the `runtime.json` file in your `lesson1` microservice package, meaning they'll listen to and trigger off of *all* devices and data sources. It's a good place to start, but is likely triggering off of far more data than you'll ever use in your bot. The objective of any good bot developer is to minimize the data your bot needs to listen to.

### index.py

[![Index Video](https://user-images.githubusercontent.com/1031168/42354023-d39ccc4e-8078-11e8-93f5-75cb65e86250.gif)](https://www.youtube.com/watch?v=uXUG1NyUy7w)

The `index.py` file describes which microservices to dynamically import into your bot at runtime. Your bot project can contain multiple `index.py` files, but ultimately they will all be merged together into a single `index.py` inside of `intelligence/index.py`.

**Homework Assignment** : Find the index.py file in your Lesson 1 directory. Read it. Understand it.

You can dynamically add and remove microservices by adding and removing references to those microservices in your `index.py` file. On each triggered execution of your bot, the bot will resynchronize with the microservices that should be a part of your project.

## Microservices

**A microservice is the highest layer of the stack where developers live.** A microservice is intended to perform a small job. Anyone who has done UI development will be familiar with the event-driven nature of a microservice. As data becomes available, methods are called within your microservice file, and it is your job to simply react to whatever is of interest.

**All microservices are to be installed under the `intelligence/` directory.**

Every microservice has a well formatted name, like `device_*_microservice.py` or `location_*_microservice.py`. The naming convention helps developers understand that the Python module is a microservice, and that it's either a "Device Microservice" or a "Location Microservice" which we explain below.

Microservices can be packaged together in a directory (like a library) so you can keep them in one place in your repository and use them across multiple bot services without forking your code for each service. Use the `structure.json` file to pull entire `microservice` directories into your local bot project. Microservice packages all end up underneath the `intelligence/` directory. You can see that `intelligence/lesson1` is a self-describing microservice package because it contains `index.py`, `runtime.json`, and `structure.json` files. That means you could technically take the `lesson1` microservice directory and drag it somewhere else in your file system, and then simply reference it with your bot's main `structure.json` to pull it back in as you generate or commit your bot.

Every microservice extends the `Intelligence` class found in `com.ppc.Bot/intelligence/intelligence.py`. The event-driven methods found in any microservice are unapologetically copy/pasted from the top of the `com.ppc.Bot/intelligence/intelligence.py` file.


### Device Microservices

Device microservices add new features to a single device in your account.

In any `index.py` file in your project, you declare which device microservices should get added to specific device types.
As individual devices appear in your account that are of the device type referenced in your index.py files, device microservices
are dynamically instantiated and applied to those devices. These microservices begin listening to events that happen in the real-world
by triggering well defined methods inside. Your job is to react to the events you care about.

In a device microservice, you can get access to the parent device object at any time by referencing the `self.parent` class variable.
You can explore the `Device` object inside `com.ppc.Bot/devices/device.py`. The other directories in that folder contain other `Device` objects
that simply extend the `Device` class to provide some device-specific features for that particular type of device.
From inside your device microservice, you can access information about a device like this:

    self.parent.description         : The name of the device
    self.parent.device_id           : The globally unique ID of this device
    self.parent.location_object     : The Location object that this device belongs to, so you can interact with other data or devices in the user's home.
    self.parent.is_connected        : True if the device is currently connected
    self.parent.proxy_id            : The device ID of the gateway / proxy that this device connects through, if any.
    self.parent.remote_addr_hash    : The hashed IP address of this device (or the gateway/proxy it connects through), so you can see if 2 devices are at the same physical location.
    self.parent.goal_id             : An ID that represents the context / scenario the user selected when installing the device.
    self.parent.latitude            : The approximate latitude of the device (within about ~5-10 miles)
    self.parent.longitude           : The approximate longitude of the device (within about ~5-10 miles)
    self.parent.measurements        : A dictionary of cached recent measurements from this device, typically from within 1 hour ago.


A device microservices reacts to the following events:
  * \__init__()                      : Constructor that is called exactly once at the time the microservice is created.
  * initialize()                    : Initialize method called every single time the bot executes, before any other event
  * destroy()                       : The microservice is disappearing, probably because the device got deleted or the developer removed the microservice from the index.py file.
  * get_html_summary()              : Event-driven method to get HTML content for weekly summaries and test emails to end users.
  * mode_updated()                  : Event-driven method declaring the user's mode got updated at the UI level.
  * question_answered()             : The user answered a question.
  * datastream_updated()            : A data stream message was received
  * schedule_fired()                : A cron schedule fired
  * timer_fired()                   : A timer or alarm fired

The following methods only trigger when the 'parent' device is updated (unlike a 'location microservice' which triggers off of every device):
  * device_measurements_updated()   : The parent device sent a new measurement.
  * device_metadata_updated()       : The parent device updated some metadata (like the description, goals/scenarios/context, etc.)
  * device_alert()                  : The parent device sent an alert, typically used in cameras.
  * device_deleted()                : The parent device got deleted.
  * file_uploaded()                 : The parent device uploaded a file.
  * coordinates_updated()           : The parent device's coordinates (lat/long) were updated)


### Location Microservices

Location microservices add new services across one or more devices (or data sources) in your account. A location typically represents a physically place, like your home.

In any `index.py` file in your project, you declare which location microservices should get added to the project.
Location microservices are added to every `Location` that is being tracked in your account. Most accounts today have only 1 official `Location`,
but we do support scenarios already where a user has multiple homes, or multiple offices, etc.

These microservices begin listening to events that happen in the real-world by triggering well defined methods.
Again, your job is to react to the events you care about.

In a location microservice, you can get access to the parent `Location` object at any time by referencing the `self.parent` class variable.
Investigating `com.ppc.Bot/locations/location.py`, you'll see the `Location` object provides some helper methods, and also maintains
a dictionary of devices that are associated with that location. You can get access to individual devices dictionary by accessing `self.parent.devices[device_id]`.
There are other helper methods to explore in the Location object, which we demonstrate in future lessons.

Here are some Location object variables you might be interested in from the level of a location microservice:

    self.parent.location_id         : The globally unique reference ID of this location.
    self.parent.devices             : Dictionary of devices associated with this location. The key is a globally unique device_id, the value is a device object.
    self.parent.mode                : The user's mode as selected in the UI.


A location microservices reacts to the following events:
  * \__init__()                      : Constructor that is called exactly once at the time the microservice is created.
  * initialize()                    : Initialize method called every single time the bot executes, before any other event
  * destroy()                       : The microservice is disappearing, probably because the device got deleted or the developer removed the microservice from the index.py file.
  * get_html_summary()              : Event-driven method to get HTML content for weekly summaries and test emails to end users. This content typically appears at the top of the email.
  * mode_updated()                  : Event-driven method declaring the user's mode got updated at the UI level.
  * question_answered()             : The user answered a question.
  * datastream_updated()            : A data stream message was received
  * schedule_fired()                : A cron schedule fired
  * timer_fired()                   : A timer or alarm fired

The following methods whenever ANY device inside the location is updated:
  * device_measurements_updated()   : Any device sent a new measurement.
  * device_metadata_updated()       : Any device updated some metadata (like the description, goals/scenarios/context, etc.)
  * device_alert()                  : Any device sent an alert, typically used in cameras.
  * device_deleted()                : Any device got deleted.
  * file_uploaded()                 : Any device uploaded a file.
  * coordinates_updated()           : Any device's coordinates (lat/long) were updated)
  
### Explore more

**Challenge**: Make your own device microservice for a specific device type, following the examples set by `intelligence/lesson1/device_entrysensor_microservice.py` and `intelligence/lesson1/device_motionsensor_microservice.py`. Be sure that your `intelligence/lesson1/index.py` adds your new device microservices properly, and that the `intelligence/lesson1/runtime.json` declares in its `deviceTypes` section that this type of device is required to run the bot.

Quick recap of how to run the lesson in the cloud:

    cp -r com.ppc.Lesson1-Microservices com.yourname.Lesson1
    botengine --commit com.yourname.Lesson1 -b <brand>
    botengine --purchase com.yourname.Lesson1 -b <brand>
    
Watch it run locally:

    botengine --run com.yourname.Lesson1 -b <brand>
    (... do work editing the bot, then run it again to see how it changed ...)
    botengine --run com.yourname.Lesson1 -b <brand>

Pause it when you're ready to move on:

    botengine --pause com.yourname.Lesson1 -b <brand> -u <user@email.com> -p <password>time Video](https://user-images.githubusercontent.com/1031168/42354024-d3b547f6-8078-11e8-9793-f0d765f7030d.gif)](https://www.youtube.com/watch?v=5Mod8nD0V3Q)

