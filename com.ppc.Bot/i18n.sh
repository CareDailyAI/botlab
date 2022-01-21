#!/bin/bash

# Add your languages to this array, with spaces in between - Example: languages=("en" "es" "zh")
declare -a languages=("en" "de")

# 1. Update the .pot file template for all languages
pybabel extract -o ./intelligence/locale/messages.pot -c NOTE: -s ./ --sort-output

# Loop through every language and update the .po file
for i in "${languages[@]}"
do
	if [ ! -d "./intelligence/locale/$i/LC_MESSAGES" ]; then
		# 2a. Initialize the new language directory .po file
		echo ""
		echo "Initializing the new language directory : $i"
		pybabel init -D 'messages' -i ./intelligence/locale/messages.pot -d ./intelligence/locale -l $i
	else
		# 2b. Update the existing language directory .po file
		echo ""
		echo "Updating the existing language directory .po file : $i"	
		pybabel update -D 'messages' -i ./intelligence/locale/messages.pot -d ./intelligence/locale -l $i --ignore-obsolete
	fi
	
	# 3. Compile the .po file into the .mo file
	pybabel compile -D 'messages' -d ./intelligence/locale -l $i -i ./intelligence/locale/$i/LC_MESSAGES/messages.po -f
done


