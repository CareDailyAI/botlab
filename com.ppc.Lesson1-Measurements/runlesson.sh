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
echo "COMMIT YOUR BOT"
echo "${bold}botengine --commit $bundle_id${normal}"
./botengine --commit $bundle_id -u $user -p $password
if [ $? -ne 0 ]
  then
    echo "STOPPING THE SCRIPT."
    echo
    exit $?
fi

echo
echo Lesson 1 : Measurements
echo If you haven\'t done so already, you should definitely open up the bot.py
echo file and read through all the commentary there. Note on the first line of
echo the bot.py commentary that you may use Python 2.7 or 3.5 to run botengine.
echo
echo We just finished creating a directory for your bot, $bundle_id.
echo Then we created a new bot in your account on the server with the same bundle ID.
echo We committed your bot to the server, which taught the server about how to run your bot.
echo We then purchased the bot, and configured it to access your sensors.
echo You should review all the commands we used above, because when you create your own bot,
echo there won\'t be this script to automate the process for you.
echo
echo Now the server knows what real-time data to deliver into your bot.
echo If you need to reconfigure your bot instance, just use
echo \"botengine --configure $bundle_id\". Remember, you always run botengine from
echo the directory above the bot\'s directory.
echo
echo The next step is to run your bot locally. The botengine framework will start listening
echo to the server for real-time data, based on the permissions you configured when
echo you purchased the bot.
echo
echo The bot only executes when real-time data is available. You will need to cause
echo something to happen to make the bot execute. Lesson 1 listens to two types of
echo sensors: Entry Sensors, and a Virtual Light Switch. You\'ll need to cause
echo one of those sensors to change state.
echo
echo You can run the virtual light switch with this command:
echo     python lightSwitch.py
echo
echo Every device that connects has a globally unique device ID, like a MAC address.
echo You can use anything you want.  I use \'moss-switch1\' for my device ID.
echo Then you can toggle the light switch on and off from its command-line interface.
echo The cloud software has no idea this isn\'t a real physical light switch.
echo
echo So we\'re going to run this Lesson 1 bot now. But until you actually trigger
echo some data from either an Entry Sensor or a Virtual Light Switch, then
echo it\'s just going to sit there, listening quietly in the background of your life.
echo

echo "RUN YOUR BOT LOCALLY"
echo "${bold}botengine --run $bundle_id${normal}"
./botengine --run $bundle_id -u $user -p $password
