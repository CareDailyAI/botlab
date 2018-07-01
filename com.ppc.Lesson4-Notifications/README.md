# Lesson 4 : Notifications

By the end of this lesson, you will know how to:
* Send push notifications
* Send emails with text and HTML
* Attach files and show inline images in HTML-based emails

## Sending notifications

The `botengine` object provides a single method to send notifications: `botengine.notify(...)`. The arguments to this method include:

* **push_content**: (optional) Push notification text (limited to the push notification service maximum message size)
* **push_sound**: (optional) Eg: "sound.wav"
* **email_subject**: (optional) Email subject line
* **email_content**: (optional) Email body
* **email_html**: (optional) True or False; default is False.
* **push_template_filename**: directoryName/PushTemplateName.vm. If this is used, the 'push_content' field is ignored.
* **push_template_model**: Dictionary of key/value pairs to inject into the push template. Dependent upon what the template itself understands.
* **email_template_filename**: directoryName/EmailTemplateName.vm. If this is used, the 'email_content' and 'email_subject' fields are ignored.
* **email_template_model**: Dictionary of key/value pairs to inject into the email template. Dependent upon what the template itself understands.
* **sms_content**: Content for an SMS message
* **sms_template_filename**: SMS template filename. If this is used, the 'sms_content' field is ignored
* **sms_template_model**: Dictionary of key/value pairs to inject into the sms template. Dependent upon what the template itself understands.
* **brand**: Case-sensitive brand for templates
* **user_id**: (optional) Specific user ID to send to if the bot is running at the organizational level.
* **user_id_list**: (optional) Specific a list of user ID's to send to if the bot is running at the organizational level.
* **to_me**: Send the message to the user only
* **to_my_friends**: Send the message to my friends
* **to_my_family**: Send the message to my family
* **to_my_group**: Send the message to people in my group in my organization
* **to_my_admins**: Send the message to the admins
* **admin_domain_name**: Domain name / "short name" of the organization to send a notification to the admins

We'll save SMS messages for a later lesson because they require additional setup and can actually enable conversations with the end user.

You can include multiple notification types (e.g. push + email) in a single call to `botengine.notify()`. By default, all messages are sent `to_me` which means the message is delivered to the user who owns the account.

### Push notification example
To send a push notification, we simply make a call like this:

    botengine.notify(push_content="Hello from your bot microservice.")
    
You can make the push notification emit a different sound like this (the sound file must be built into the app to be recognized):

    botengine.notify(push_content="Alarm!", push_sound="alarm.wav")
    

### Text-based email example
To send a basic text-based email notification, we call:
 
    botengine.notify(email_subject="Subject line here.", email_content="Email body here")

### HTML-email example
To send an HTML-formatted email, we call:
 
    botengine.notify(email_subject="Subject line here.", email_content="<HTML><b>HTML Email example</b></HTML>", email_html=True)

The `email_content` can actually be loaded from a local custom template, as we'll show you in this lesson.

## Adding email attachments
You can include attachments in your emails. Start by defining an empty list to hold your attachments:

    attachments = []

Then pass this list into `botengine.add_email_attachment(destination_attachment_array, filename, content, content_type, content_id)`:

    attachments = botengine.add_email_attachment(attachments, "example.txt", "This is some text content to put into a file named example.txt, but could be base64-encoded binary content if it were an image.", "text/plain", "contentId")
    
You can call this `add_email_attachment()` multiple times, passing in an ever-growing list of attachments. When you're done, add the list into the `notify()` method:

    botengine.notify(email_subject="Email with attachment", email_content="See the attached document.", email_attachments=attachments, email_html=False)
    
Each attachment's `content_id` can be used to enable an HTML-based email render an inline image. To see how this works, check out the `email_template.vm` file included in this lesson and search for `<img src="cid:inlineImageId" width="100%" alt="">`. The image will come from an attachment to your email with the `content_id` set to the name `inlineImageId`.


### Explore more

There are 2 files to check out in this lesson.

* `intelligence/lesson4/lesson_notification_microservice` : Location microservice that demonstrates how to send an email with a custom HTML template and an inline image.

* `intelligence/lesson4/lesson_entrynotification_microservice` : Device microservice that sends a push notification with a sound when an entry sensor opens while you are not in HOME mode.

Run it: 
    
    cp -r com.ppc.Lesson4-Notifications com.yourname.Lesson4
    botengine --commit com.yourname.Lesson4 -b <brand> -u <user@email.com> -p <password>
    botengine --purchase com.yourname.Lesson4 -b <brand> -u <user@email.com> -p <password>
    
Watch it run locally:

    botengine --run com.yourname.Lesson4 -b <brand> -u <user@email.com> -p <password>
    