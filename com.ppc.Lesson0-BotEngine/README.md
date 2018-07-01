# Lesson 0 : BotEngine

By the end of this lesson, you will have done the following:
* Setup your environment to run the botengine
* Understand what the botengine is and what it generally does.

You'll run the 'botengine' from a command line interface. Windows users should install Cygwin. Mac and Linux users can use the Terminal.

## Setup your environment

### Step 1 : Get a user account

You'll first need a user account with a smart home service that is powered by People Power's bot server.

Download and sign up one of our partner's apps from the App Store or sign up at one of these locations:

* http://app.presencepro.com : Presence by People Power. Transform spare smartphones and tablets into free internet security cameras.
* http://myplace.com : MyPlace by FPL Smart Services. Professional-monitoring and self-monitoring security services.
* http://originhomehq.com.au : Home HQ by Origin Energy.


### Step 2 : Setup Python

BotEngine prefers Python 2.7, because AWS Lambda - one of the execution environments this runs within - had exclusively supported 2.7 only until recently.

We prefer setting up Python 2.7 on your local machine inside a virtual environment, which helps keep things clean. See https://www.youtube.com/watch?v=N5vscPTWKOk.  This is also a good tutorial for Mac users: https://hackercodex.com/guide/python-development-environment-on-mac-osx/. After setting up a virtual environment, you can activate it each time you open the terminal with a strategically placed command in one of your startup scripts, like ~/.profile or ~/.bashrc. Here's an example out of my environment's startup scripts:

`source ~/workspace/botengine/bots/bin/activate`

Once you have your Python environment established, install these python package dependencies:

`pip install requests dill tzlocal python-dateutil`

### Step 3 : Install the BotEngine

We strongly recommend you clone this git repository and run the botengine locally. But installing the botengine with the command line below can accelerate the installation of dependencies as well.

To install the BotEngine framework on your local machine, copy and paste the following line of code in your terminal:

`curl -s https://raw.githubusercontent.com/peoplepower/botlab/master/installer.sh | sudo /bin/bash`

The installer file will download the BotEngine framework and all the dependencies needed to run botengine.

When you clone the botengine repository, be sure to add its location to your PYTHONPATH variable.


### Step 4 : Test it out

Run the following command from your terminal window:

    botengine --my_purchased_bots --brand <your brand>
    
Where `<your brand>` is one of the following:
* **presence**
* **myplace**
* **origin**

If running from a cloned repository, just add a `./` to the front of botengine:

    ./botengine --my_purchased_bots --brand <your brand>
    
    
If you successfully get back something that looks like this, you're in business. I've added a few more optional command line arguments to point them out. Obviously typing your password into a command line is not secure, but if it's your own computer then it sure is convenient.

    botengine --my_purchased_bots -u user@email.com -p password -b presence
    
    Presence by People Power
    Bot Server: https://app.presencepro.com
    Bot Instance 700: com.ppc.Geofencing; Version 1.0.8; ACTIVE
    
    Done!

## What is 'botengine'?

The `botengine` serves two purposes:

* It is a command line interface (CLI) to manage the creation of your bots, and to run your bots locally.
* When running bots, the `botengine` object provides a window into the user's account through easy-to-use methods.

The `botengine` is deployed as a single file so it can be easily downloaded and used.

Use `botengine --help` to get a list of things the `botengine` CLI can do.