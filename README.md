# Bot Lab: Add Thoughts to Things.

The Bot Lab contains the BotEngine Microservices Python framework, enabling developers to explore the creation of new features, agents, and services on top of every internet-connected data source or device. 

These bots run 24/7 in the background of your life, making products do things the manufacturer never imagined. In the same way that mobile app developers can create apps for smartphones, now we can move beyond screens and add features and services to every internet-connected device. 

**You do not need to host your own server to run bot microservices.** We host and run them for you on our servers. Of course, you can also run them live on your local computer and watch them execute against real-time data from the real world.

### Start with getting your virtual environment

Reach out to Care Daily at hello@caredaily.ai to get set up with your own organization and user account.

### You need Python 3.x

We're using Python 3.x+. We strongly recommend using a virtual environment. 

```
# Create your virtual environment
virtualenv -p PATH/TO/PYTHON3 bots
# if it fails for you, Try:
# python3 -m virtualenv bots

# Activate your virtual environment. I add this to my ~/.bash_profile (on mac).
source bots/bin/active

# Install dependencies. Note it may be 'pip3' in your environment.
pip install -r requirements.txt
```

## Get Started with the BotEngine

Clone this repository to your computer. The 'botengine' file is a Python application which serves a dual purpose: it is the command line interface which provides access for the developer to create and manage bots, and it is also the software execution environment for which provides access for a running bot to securely interact with the outside world.

Most developers simply type `./botengine` to execute commands on the command line interface. For example, `./botengine --help`

If you're running Windows, we recommend using Windows Terminal to run the 'botengine' application. You can also try `python botengine`. Please keep in mind that although Python is meant to be operating system independent, some differences do exist between OS's and bot commercial code runs in a Linux environment on the cloud or on the edge.


## BotEngine Shortcuts

The botengine requires your username and password for every interaction with the server. We go faster this by saving our login details inside environment variables on our local machine by adding some exports to one of the terminal startup scripts, like ~/.profile or ~/.bashrc:

`export LOGIN="-u email@example.com -p password"`

Then you can run your botengine like this:

`botengine --my_purchased_bots $LOGIN`


### Developer bots stop executing after 24 hours.

If you're not interacting with your bot as a developer, the cloud will automatically stop executing it. This is to protect our resources from bots that haven't been reviewed for performance.

Next steps include:
* Make your bot do what you want by editing code locally, and `--run` it again with each modification.
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


## Documentation

Each Lesson contains documentation. Open each lesson to review the documentation, and then drill down into the individual microservices inside the intelligence directories.

