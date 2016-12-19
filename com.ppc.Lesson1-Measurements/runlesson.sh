#!/bin/bash

bold=$(tput bold)
green="\033[0;32m"
red="\033[0;31m"
normal=$(tput sgr0)

echo -ne "${green}What is your unique bundle ID that will last forever for this bot (i.e. com.yourname.Lesson1-Measurements): ${normal}"
read bundle_id
periods=`echo $bundle_id | grep -o "\." | wc -l`

if [ $periods -ne 2 ]
  then
    echo "You must specify a reverse-domain notation bundle ID for your bots."
    echo
    exit -1
fi

echo "${bold}Okay, we'll call it $bundle_id.${normal}"
echo

echo -n "Email address: "
read user
echo -n "Password: "
read -s password


echo
echo "COPY FILES TO A NEW DIRECTORY"
echo "Creating directory ../$bundle_id"
mkdir ../$bundle_id

echo "Copying all the files from this lesson into ../$bundle_id"
cp * ../$bundle_id/
cd ..

echo
<<<<<<< HEAD
echo "CREATE A NEW BOT IN YOUR ACCOUNT"
echo "${bold}botengine --new $bundle_id${normal}"
./botengine --new $bundle_id -u $user -p $password
=======
echo "COMMIT YOUR BOT"
echo "${bold}botengine --commit $bundle_id${normal}"
./botengine --commit $bundle_id -u $user -p $password
>>>>>>> 0a10d22171bd98f677176d1a751cd0c4428e15a8
if [ $? -ne 0 ]
  then
    echo "STOPPING THE SCRIPT."
    echo
    exit $?
fi

echo
<<<<<<< HEAD
echo "COMMIT YOUR BOT"
echo "${bold}botengine --commit $bundle_id${normal}"
./botengine --commit $bundle_id -u $user -p $password
=======
echo "PURCHASE YOUR BOT"
echo "${bold}botengine --purchase $bundle_id${normal}"
./botengine --purchase $bundle_id -u $user -p $password
>>>>>>> 0a10d22171bd98f677176d1a751cd0c4428e15a8
if [ $? -ne 0 ]
  then
    echo
<<<<<<< HEAD
    exit $?
fi

echo
echo "PURCHASE YOUR BOT"
echo "${bold}botengine --purchase $bundle_id${normal}"
./botengine --purchase $bundle_id -u $user -p $password
if [ $? -ne 0 ]
  then
    echo 
=======
>>>>>>> 0a10d22171bd98f677176d1a751cd0c4428e15a8
    echo "STOPPING THE SCRIPT."
    echo "If the error above says this bot is incompatible with your devices,"
    echo "then you need to add an Entry Sensor or a Virtual Light Switch to "
    echo "your account. You can use 'python lightSwitch.py' to add a"
    echo "Virtual Light Switch, then you will be able to run this script"
    echo "again and purchase your bot on the cloud."
    echo
    echo "If you have already purchased this bot instance already, then"
    echo "you should just run it. Use the following command from the directory"
    echo "above your bot:"
    echo    botengine --run $bundle_id
<<<<<<< HEAD
    echo 
=======
    echo
>>>>>>> 0a10d22171bd98f677176d1a751cd0c4428e15a8
    exit $?
fi

echo
echo Lesson 1 : Measurements
echo If you haven\'t done so already, you should definitely open up the bot.py
<<<<<<< HEAD
echo file and read through all the commentary there. Note on the first line of 
echo the bot.py commentary that you\'ll need Python 3.0 or newer to run botengine.
echo 
=======
echo file and read through all the commentary there. Note on the first line of
echo the bot.py commentary that you\'ll need Python 3.0 or newer to run botengine.
echo
>>>>>>> 0a10d22171bd98f677176d1a751cd0c4428e15a8
echo We just finished creating a directory for your bot, $bundle_id.
echo Then we created a new bot in your account on the server with the same bundle ID.
echo We committed your bot to the server, which taught the server about how to run your bot.
echo We then purchased the bot, and configured it to access your sensors.
echo You should review all the commands we used above, because when you create your own bot,
echo there won\'t be this script to automate the process for you.
<<<<<<< HEAD
echo 
echo Now the server knows what real-time data to deliver into your bot.
echo If you need to reconfigure your bot instance, just use 
echo \"botengine --configure $bundle_id\". Remember, you always run botengine from
echo the directory above the bot's directory.
echo 
=======
echo
echo Now the server knows what real-time data to deliver into your bot.
echo If you need to reconfigure your bot instance, just use
echo \"botengine --configure $bundle_id\". Remember, you always run botengine from
echo the directory above the bot's directory.
echo
>>>>>>> 0a10d22171bd98f677176d1a751cd0c4428e15a8
echo The next step is to run your bot locally. The botengine framework will start listening
echo to the server for real-time data, based on the permissions you configured when
echo you purchased the bot.
echo
echo The bot only executes when real-time data is available. You will need to cause
<<<<<<< HEAD
echo something to happen to make the bot execute. Lesson 1 listens to two types of 
=======
echo something to happen to make the bot execute. Lesson 1 listens to two types of
>>>>>>> 0a10d22171bd98f677176d1a751cd0c4428e15a8
echo sensors: Entry Sensors, and a Virtual Light Switch. You\'ll need to cause
echo one of those sensors to change state.
echo
echo You can run the virtual light switch with this command:
echo     python lightSwitch.py
echo
echo Every device that connects has a globally unique device ID, like a MAC address.
echo You can use anything you want.  I use \'moss-switch1\' for my device ID.
echo Then you can toggle the light switch on and off from its command-line interface.
echo The cloud software has no idea this isn't a real physical light switch.
echo
echo So we\'re going to run this Lesson 1 bot now. But until you actually trigger
<<<<<<< HEAD
echo some data from either an Entry Sensor or a Virtual Light Switch, then 
echo it\'s just going to sit there, listening quietly in the background of your life.
echo 

echo "RUN YOUR BOT LOCALLY"
echo "${bold}botengine --run $bundle_id${normal}"
./botengine --run $bundle_id -u $user -p $password
=======
echo some data from either an Entry Sensor or a Virtual Light Switch, then
echo it\'s just going to sit there, listening quietly in the background of your life.
echo
>>>>>>> 0a10d22171bd98f677176d1a751cd0c4428e15a8

echo "RUN YOUR BOT LOCALLY"
echo "${bold}botengine --run $bundle_id${normal}"
./botengine --run $bundle_id -u $user -p $password
