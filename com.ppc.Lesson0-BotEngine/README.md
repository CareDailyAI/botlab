# Lesson 0 : BotEngine

These README.md files are best viewed on the open source repository at GitHub.com, if you're not there already.

http://github.com/caredailyai/botlab

By the end of this lesson, you will have done the following:
* Setup your environment to run the botengine
* Understand what the botengine is and what it generally does.

You'll run the 'botengine' from your Terminal.

## What is 'botengine'?

The `botengine` serves two purposes:

* It is a command line interface (CLI) to manage the creation of your bots, and to run your bots locally in a Terminal window.
* When running bots, the `botengine` object (which is passed around in most events) provides APIs to interact with the outside world.

The `botengine` is deployed as a single file so it can be easily downloaded and used.

Use `botengine --help` to get a list of things the `botengine` CLI can do.

When running bots, you will notice **every method** includes `botengine` as a first argument. This is standard practice for creating bots, so remember to include `botengine` in every method. 

Sometimes if a method doesn't require use of the `botengine` object, we still support it as an argument so you can program without thinking about it. For example:

    # Demonstration of a method that doesn't really need the botengine argument.
    # Add it anyway. Always pass the botengine object around as it's your only window to the outside world.
    def my_method(self, botengine=None):
        ...
        
See the `docs/index.html` page in this repository for the documentation on the `botengine` object and what methods it provides to you bot services.

## Setup your environment

[![Installing the BotEngine](https://user-images.githubusercontent.com/1031168/42200555-acf1e37c-7e48-11e8-8f20-7896b4820f9d.gif)](https://www.youtube.com/watch?v=n2p5hQ68mIw)

### Step 1 : Setup Python

BotEngine supports the latest Python release (currently 3.11).

We prefer setting up Python on your local machine inside a virtual environment, which helps keep things clean. See https://www.youtube.com/watch?v=N5vscPTWKOk.  This is also a good tutorial for Mac users: https://hackercodex.com/guide/python-development-environment-on-mac-osx/. After setting up a virtual environment, you can activate it each time you open the terminal with a strategically placed command in one of your startup scripts, like ~/.profile or ~/.bashrc. Here's an example out of my environment's startup scripts:

`source ~/workspace/botengine/bots/bin/activate`

### Step 2 : Install the BotEngine

Clone this repository to your computer. The 'botengine' file is a Python application which serves a dual purpose: it is the command line interface which provides access for the developer to create and manage bots, and it is also the software execution environment for which provides access for a running bot to securely interact with the outside world.

**Install dependencies**

Note it may be 'pip3' in your environment.
`pip install -r requirements.txt`

Type `./botengine` to execute commands on the command line interface. To see a list of all commands type `./botengine --help`.

If you're running Windows, we recommend using Windows Terminal to run the 'botengine' application. You can also try `python botengine`. Please keep in mind that although Python is meant to be operating system independent, some differences do exist between OS's and bot commercial code runs in a Linux environment on the cloud or on the edge.

### Step 3 : Create an account

Before you begin, you'll need a user, location, and an organization.  Sign up at https://app.caredaily.ai/signup to jump start your development and get ready to dive into building your own services.

### Step 4 : Test it out

Run the following command from your terminal window, replacing the arguments with your own credentials:

`./botengine --my_purchased_bots -u user -p password`
    
If you successfully get back something that looks like this, you're in business.

```
Bot Server: https://app.peoplepowerco.com
Bot Instance 700: com.ppc.Tests; Version 1.0.8; ACTIVE
    
Done!
```

### Common botengine commands

* **botengine --my_purchased_bots** : Get a list of the bot services you are running in your account.

* **botengine --my_developer_bots** : Get a list of the bots you have created as a developer.

* **botengine --commit [bot]** : Commit a bot to the cloud. Do this especially when you want to change the what the runtime.json file says your bot is listening to.

* **botengine --purchase [bot]** : Purchase an instance of a bot into your account. For example, this can take the blueprint of the bot that you committed as a developer, and activate it inside your own end-user account.

* **botengine --configure [bot]** : Configure which devices and data sources a bot instance has access to in your account.

* **botengine --run [bot]** : Migrate the execution of the bot from the cloud to your local computer, using bot source code you have available locally.

* **botengine --play [bot]** : Resume execution of a bot that is paused. Note that your developer bots pause automatically after 24 hours if you aren't explicitly interacting with them with the botengine.

* **botengine --pause [bot]** : Pause the execution of a bot that is actively running in your account.

* **botengine --delete [bot]** : Delete a bot instance out of your account. This doesn't delete the committed developer blueprint of the bot. It only deletes the instance of that bot which you've purchased and activated inside your end user account. You can `--purchase` the bot again.

* **botengine --errors [bot]** : As a developer of the bot, you can see the errors and warnings your bot is generating while running in the cloud.

### BotEngine Shortcuts

The botengine requires your username and password for every interaction with the server. We go faster this by saving our login details inside environment variables on our local machine by adding some exports to one of the terminal startup scripts, like ~/.profile or ~/.bashrc:

`export LOGIN="-u email@example.com -p password"`

Then you can run your botengine like this:

`botengine --my_purchased_bots $LOGIN`

### Developer bots stop executing after 24 hours.

If you're not interacting with your bot as a developer, the cloud will automatically stop executing it. This is to protect our resources from bots that haven't been reviewed for performance.

## Publishing

Next steps include:
* Keep making commits to the cloud. You do not need to increment the version number each time inside `runtime.json`.
* Publish the bot with the `--publish` command. This technically puts it through a review process like the Apple App Store. In reality, since we're not the Apple App Store yet, you can just let us know when you are ready to publish a bot by emailing dmoss@caredaily.ai or destry@caredaily.ai. Once published, other users can purchase the bot with the `--purchase` command.

## Notes on architecture

There are a few design philosophies and best practices we've grown over the years as we've developed bots. 

* No lower layer in the stack should depend upon any higher layer in the stack. Data flows from `lambda.py` to `botengine` to `bot.py` on up the stack to the location object -> filter objects -> device objects -> microservice objects. It should be obvious, but while microservices can be dependent upon a device object, the device object should never be dependent upon a microservice.
* To get around these dependencies, we use `signals`. A signal is really just a function definition that turns a set of arguments into a data stream message. We try to avoid creating data stream messages directly inside microservices now, because they're difficult to maintain, find, and document. Check out `com.ppc.Bot/signals` and `com.ppc.BotProprietary/signals`. 
* Check out how we use the `datastream_updated()` event in our microservices to transform a data stream message (signal) directly into a function call, where the name of the function is the name of the signal. Super easy.
* Often times, these signals can become externally accessible "Synthetic APIs". A Synthetic API is asynchronous, and realized through a combination of 2 platform APIs: Data Stream Messages and State Variables. If you choose to expose a Synthetic API, documentation is important, and we keep these docs on http://github.com/caredailyai/docs.
* We've found pretty much all devices produce untrustworthy data, and cleaning that data or deriving entirely new information is an important activity. This is why we introduced the concept of `filters` in the Summer of 2021. Filters are treated just like microservices in that they're modular and can be added and removed without strict dependencies, but they also have a slightly different interface than microservices. Data now flows up the stack from the location object -> filters -> device objects and then finally to microservices. The `filter_measurements()` event allows filters the opportunity to correct or delete data before it lands in our representative model of the world. And it can even invent new parameterized data for microservices to work with. There's still more to explore in this architecture, including the ability to potentially save the corrected and parameterized time-series data back to the device on the AI+IoT Platform itself.

As a new bot developer, I strongly recommend you generate a bot and follow the data path all the way through from botengine -> bot.py -> controller -> location.py -> filters -> device objects -> microservices. I also strongly recommend understanding what microservice packages exist today, how they operate, and what signals they use to communicate with each other. A large part of being a good bot developer is simply knowing where things are located.

Always remember your place on the DIKW ladder: 
1. DATA is what a device produces, in its own protocol / language, below the AI+IoT Platform.
2. INFORMATION is produced when we transform all that data into a common language, separating the messy "network layer" from the "application layer". Information is what you pull out of the AI+IoT Platform, and you can visualize it on a graph. Filters help improve the trustworthiness of information, and help synthesize new information.
3. KNOWLEDGE is derived from information. This can often be expressed as a sentence, like "You got great sleep quality last night." Most of the time, this is what people want. People don't want to think hard about a graph of energy consumption, they want to read a sentence that conveys the knowledge that energy consumption is currently trending out-of-bounds. People don't want to look at a graph of bedtime, they want to know the bedtime has remained consistent day after day.
4. WISDOM is an action back to the physical world, derived from knowledge. This is what happens when we turn off a light because we know you've gone to bed, or we send a notification that you forgot to arm your security system when you left the house.

Bots operate primarily in the Knowledge and Wisdom layers of the stack.


## Corporate Networks with Proxies

If you are operating in a corporate network that has a proxy, you can provide the proxy information as an argument to the command line interface with the `--https-proxy <proxy>` argument:

`botengine --my_purchased_bots --https_proxy http://10.10.1.10:1080`

The BotEngine uses the Python `requests` library to make HTTPS calls to the server. The `requests` library allows you to alternatively set the proxy through an environment variable:

`export HTTPS_PROXY="http://10.10.1.10:1080"`

The BotEngine exclusively uses HTTPS and never uses HTTP communications. 

For rapid transitions in and out of corporate network environments, check out the Envswitch tool developed by https://github.com/smarie

https://smarie.github.io/develop-behind-proxy/switching/#envswitcher

