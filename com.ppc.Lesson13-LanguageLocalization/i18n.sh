#!/bin/bash

# Add your languages to this array, with spaces in between - Example: languages=("en" "es" "zh")
declare -a languages=("en")

# 1. Get the current working directory
cwd=${PWD##*/}

# 2. Generate this bot to capture all microservices
cd ../
./botengine --generate $cwd
cd $cwd

# 3. Update the .pot file template for all languages
pybabel extract -o ./locale/messages.pot -c NOTE: -s ../.$cwd

# 4. Loop through every language and update the .po file
for i in "${languages[@]}"
do
	if [ ! -d "./locale/$i/LC_MESSAGES" ]; then
		# 4a. Initialize the new language directory .po file
		echo ""
		echo "Initializing the new language directory : $i"
		pybabel init -D 'messages' -i ./locale/messages.pot -d ./locale -l $i
	else
		# 4b. Update the existing language directory .po file
		echo ""
		echo "Updating the existing language directory .po file : $i"	
		pybabel update -D 'messages' -i ./locale/messages.pot -d ./locale -l $i
	fi
	
	# 5. Compile the .po file into the .mo file
	pybabel compile -D 'messages' -d ./locale -l $i -i ./locale/$i/LC_MESSAGES/messages.po -f
done


