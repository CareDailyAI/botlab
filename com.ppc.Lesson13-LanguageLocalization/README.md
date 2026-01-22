# Lesson 13 : Language Localization

This lesson demonstrates gettext-based localization and the `_()` convention for marking strings translatable.

Also, please check out the following:
- **`i18n.sh`**: extracts strings and compiles locale catalogs.
- **`localization.py`**: installs gettext and selects language.
- **`domain.py`**: configures default language and branding.

Use the famous `_('Hello')` style nomenclature to create a localizable string in your microservices.

If you want to include something dynamic in this string, then use the `format()` function like so:

### CORRECT
    three = "3"
    _("One Two {}").format(three)

Remember that everything inside the parenthesis acts like a key, so this is wrong:

### WRONG
    three = "3"
    _("One Two {}".format(three))

Because this turns the string into "One Two 3", and then this string is used as a key to look up the translation - and none exists.

## What you’ll build

- A location microservice (`intelligence/lesson13/location_localization_microservice.py`) that publishes a small payload to `lesson13/localization` showing correct vs incorrect dynamic-string patterns.

## Run locally (recommended)

```bash
botlab-tests --bundle com.ppc.Lesson13-LanguageLocalization --directory tests
```

## Generate and compile locale files

Inside the bot directory:

```bash
./i18n.sh
```

This will:
- generate the bot (so all microservices are included),
- extract strings into `locale/messages.pot`,
- update per-language `messages.po`,
- compile `messages.po` into `messages.mo`.
