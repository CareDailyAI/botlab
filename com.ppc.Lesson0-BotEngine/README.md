# Lesson 0 : BotEngine

These README.md files are best viewed on the open source repository at GitHub.com, if you're not there already.

http://github.com/peoplepower/botlab

By the end of this lesson, you will have done the following:
* Setup your environment to run the botengine
* Understand what the botengine is and what it generally does.

You'll run the 'botengine' from your Terminal.

## Setup your environment

[![Installing the BotEngine](https://user-images.githubusercontent.com/1031168/42200555-acf1e37c-7e48-11e8-8f20-7896b4820f9d.gif)](https://www.youtube.com/watch?v=n2p5hQ68mIw)

### Step 1 : Get a user account

Download the People Power Family app on iOS or Android. Create an account with your phone number, email address, and password.


### Step 2 : Setup Python

BotEngine prefers Python 3.8.

We prefer setting up Python on your local machine inside a virtual environment, which helps keep things clean. See https://www.youtube.com/watch?v=N5vscPTWKOk.  This is also a good tutorial for Mac users: https://hackercodex.com/guide/python-development-environment-on-mac-osx/. After setting up a virtual environment, you can activate it each time you open the terminal with a strategically placed command in one of your startup scripts, like ~/.profile or ~/.bashrc. Here's an example out of my environment's startup scripts:

`source ~/workspace/botengine/bots/bin/activate`

Once you have your Python environment established, install these python package dependencies:

`pip install requests dill tzlocal python-dateutil`

### Step 3 : Install the BotEngine

We strongly recommend you clone this git repository and run the botengine locally.


### Step 4 : Test it out

Run the following command from your terminal window:

    botengine --my_purchased_bots 

If running from a cloned repository, just add a `./` to the front of botengine:

    ./botengine --my_purchased_bots
    
    
If you successfully get back something that looks like this, you're in business. I've added a few more optional command line arguments to point them out. Obviously typing your password into a command line is not secure, but if it's your own computer then it sure is convenient.

    botengine --my_purchased_bots -u user@email.com -p password
    
    Bot Server: https://app.presencepro.com
    Bot Instance 700: com.ppc.Geofencing; Version 1.0.8; ACTIVE
    
    Done!

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
