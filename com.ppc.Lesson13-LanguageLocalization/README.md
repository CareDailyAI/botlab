# Lesson 13 : Language Localization

Please reach out to the developers if you would like a complete tutorial on language localization.

Also, please check out the following:
* **i18n.sh** inside each bot. Run this script inside a bot directory to extract all localizable strings from your bots.
* **localization.py** inside each bot. I've included a copy of this locally with the key lines uncommented to allow for language localization packages.
* **domain.py** inside each bot. We use this file to configure and brand a bot service. This file also specifies the default language.

Use the famous _("Hello") style nomenclature to create a localizable string in your microsevices. 

If you want to include something dynamic in this string, then use the format() function like so:

### CORRECT
    three = "3"
    _("One Two {}").format(three)

Remember that everything inside the parenthesis acts like a key, so this is wrong:

### WRONG
    three = "3"
    _("One Two {}".format(three))

Because this turns the string into "One Two 3", and then this string is used as a key to look up the translation - and none exists.
