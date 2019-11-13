# Bot Lab: Add Thoughts to Things.

The Bot Lab contains the BotEngine Microservices Python framework, enabling developers to explore the creation of new features, agents, and services on top of every internet-connected data source or device. 

These bots run 24/7 in the background of your life, making products do things the manufacturer never imagined. In the same way that mobile app developers can create apps for smartphones, now we can move beyond screens and add features and services to every internet-connected device. 

**You do not need to host your own server to run bot microservices.** We host and run them for you on our servers. Of course, you can also run them live on your local computer and watch them execute against real-time data from the real world.


## Setup Python

BotEngine prefers Python 3.7.

We *strongly recommend* setting up Python 3.7 on your local machine inside a virtual environment, which helps keep things clean. See https://www.youtube.com/watch?v=N5vscPTWKOk.  This is also a good tutorial for Mac users: https://hackercodex.com/guide/python-development-environment-on-mac-osx/. After setting up a virtual environment, you can activate it each time you open the terminal with a strategically placed command in one of your startup scripts, like ~/.profile or ~/.bashrc. Here's an example out of my environment's startup scripts:

`source ~/workspace/botengine/bots/bin/activate`

Once you have your Python environment established, install these python package dependencies:

`pip install requests dill tzlocal python-dateutil`


## Get Started with the BotEngine

Clone this repository to your computer. The 'botengine' file is a Python application which serves a dual purpose: it is the command line interface which provides access for the developer to create and manage bots, and it is also the software execution environment for which provides access for a running bot to securely interact with the outside world.

Most developers simply type `./botengine` to execute commands on the command line interface. For example, `./botengine --help`

If you're running Windows, we recommend using Windows Terminal to run the 'botengine' application. You can also try `python botengine`. Please keep in mind that although Python is meant to be operating system independent, some differences do exist between OS's and bot commercial code runs in a Linux environment on the cloud or on the edge.

When you clone the botengine repository, be sure to add its location to your PYTHONPATH variable.


## BotEngine Shortcuts

The botengine requires your username and password for every interaction with the server. We go faster this by saving our login details inside environment variables on our local machine by adding some exports to one of the terminal startup scripts, like ~/.profile or ~/.bashrc:

`export LOGIN="-u email@example.com -p password"`

Then you can run your botengine like this:

`botengine --my_purchased_bots $LOGIN`


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

