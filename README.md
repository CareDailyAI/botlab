# Bot Lab: Add Thoughts to Things.

The Bot Lab contains the BotEngine Python framework, enabling developers to explore the creation of new features, agents, and services on top of every internet-connected data source or device. 

These aren't silly chatbots. These bots run 24/7 in the background of your life, making products do things the manufacturer never imagined. In the same way that mobile app developers can create apps for smartphones, now we can move beyond screens and add features and services to every internet-connected device. 

## Setup Python

BotEngine prefers Python 2.7, because AWS Lambda - one of the execution environments this runs within - had exclusively supported 2.7 only until recently.

We prefer setting up Python 2.7 on your local machine inside a virtual environment, which helps keep things clean. See https://www.youtube.com/watch?v=N5vscPTWKOk.  This is also a good tutorial for Mac users: https://hackercodex.com/guide/python-development-environment-on-mac-osx/. After setting up a virtual environment, you can activate it each time you open the terminal with a strategically placed command in one of your startup scripts, like ~/.profile or ~/.bashrc. Here's an example out of my environment's startup scripts:

`source ~/workspace/botengine/bots/bin/activate`

Once you have your Python environment established, install these python package dependencies:

`pip install requests dill tzlocal python-dateutil`


## Get Started with the BotEngine

To install the BotEngine framework on your local machine, copy and paste the following line of code in your terminal:

`curl -s https://raw.githubusercontent.com/peoplepower/botlab/master/installer.sh | sudo /bin/bash`

The installer file will download the BotEngine framework and all the dependencies needed to run botengine.

When you clone the botengine repository, be sure to add its location to your PYTHONPATH variable.


## BotEngine Shortcuts

The botengine requires your username and password for every interaction with the server. We go faster this by saving our login details inside environment variables on our local machine by adding some exports to one of the terminal startup scripts, like ~/.profile or ~/.bashrc:

`export LOGIN="-u email@example.com -p password"`

Then you can run your botengine like this:

`botengine --my_purchased_bots $LOGIN`


## Documentation

Each Lesson contains a bot with documentation. Open the bot.py and runtime.json files for step-by-step instructions to learn how to create your own bot micro-services on top of Internet-connected products.


## Connecting products 

Explore this store of already-connected devices and sensors: http://presencepro.com/store.

Or connect your own at http://presto.peoplepowerco.com.
