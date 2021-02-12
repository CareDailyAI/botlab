'''
Created on August 23, 2019

This file is subject to the terms and conditions defined in the
file 'LICENSE.txt', which is part of this source code package.

@author: David Moss
'''

from intelligence.intelligence import Intelligence
from devices.entry.entry import EntryDevice

import domain
import utilities.utilities as utilities
import signals.tasks as tasks
import signals.dailyreport as dailyreport
import signals.analytics as analytics

class LocationTasksMicroservice(Intelligence):
    """
    Implements task management
    https://presence.atlassian.net/wiki/spaces/BOTS/pages/739869008/tasks+Task+Management+for+Presence+Family+based+apps

    + Add a narrative when a task is added/updated/modified including who made the change
    + Notify the person who is assigned the task
    + In the morning, if a task is still active and was created more than 24 hours ago, remind the person their task is due today.

    'tasks' state variable content example:
        {
          "d86b00c0-ef4a-4e47-9adc-845a5dda53e0": {
              "title": "Take mom to the doctor",
              "due_display": "Friday, October 11",
              "due_date": "YYYY-MM-DD",
              "assigned_to": user_id,
              "created_by": user_id,
              "comment": "Amanda, mom has a neuro apt coming up. Can you please take her?\n\nProvidence Hospital\n1816 NE 32nd Ave\nSeattle, WA 98580",
              "updated": 1569463246000
          },

          "6ec98029-4a56-4218-a2b1-ed233fc5e0bd": {
              "title": "Take mom to the doctor",
              "due_display": null,
              "due_date": null,
              "assigned_to": null,
              "created_by": user_id,
              "comment": "Take out the trash",
              "updated": 1569463246000
          },

          "11b393f8-c3ad-4e02-a0ca-6014f775042f": {
              "title": "Another example of take out the trash with no due date or assignee.",
              "created_by": user_id,
              "comment": "Take out the trash",
              "updated": 1569463246000
            }
          ]
        }

    """

    def __init__(self, botengine, parent):
        """
        Instantiate this object
        :param parent: Parent object, either a location or a device object.
        """
        Intelligence.__init__(self, botengine, parent)

    def initialize(self, botengine):
        """
        Initialize
        :param botengine: BotEngine environment
        """
        return

    def destroy(self, botengine):
        """
        This device or object is getting permanently deleted - it is no longer in the user's account.
        :param botengine: BotEngine environment
        """
        return

    def mode_updated(self, botengine, current_mode):
        """
        Mode was updated
        :param botengine: BotEngine environment
        :param current_mode: Current mode
        :param current_timestamp: Current timestamp
        """
        return

    def occupancy_status_updated(self, botengine, status, reason, last_status, last_reason):
        """
        AI Occupancy Status updated
        :param botengine: BotEngine
        :param status: Current occupancy status
        :param reason: Current occupancy reason
        :param last_status: Last occupancy status
        :param last_reason: Last occupancy reason
        """
        return

    def device_measurements_updated(self, botengine, device_object):
        """
        Device was updated
        :param botengine: BotEngine environment
        :param device_object: Device object that was updated
        """
        return

    def device_metadata_updated(self, botengine, device_object):
        """
        Evaluate a device that is new or whose goal/scenario was recently updated
        :param botengine: BotEngine environment
        :param device_object: Device object that was updated
        """
        return

    def device_alert(self, botengine, device_object, alert_type, alert_params):
        """
        Device sent an alert.
        When a device disconnects, it will send an alert like this:  [{u'alertType': u'status', u'params': [{u'name': u'deviceStatus', u'value': u'2'}], u'deviceId': u'eb10e80a006f0d00'}]
        When a device reconnects, it will send an alert like this:  [{u'alertType': u'on', u'deviceId': u'eb10e80a006f0d00'}]
        :param botengine: BotEngine environment
        :param device_object: Device object that sent the alert
        :param alert_type: Type of alert
        """
        return

    def device_added(self, botengine, device_object):
        """
        A new Device was added to this Location
        :param botengine: BotEngine environment
        :param device_object: Device object that is getting added
        """
        if isinstance(device_object, EntryDevice):
            already_created = botengine.load_variable("task.__init__")
            location_property = self.parent.get_location_property(botengine, "task.__init__")

            if already_created is None and location_property is None:
                botengine.save_variable("task.__init__", True)
                self.parent.set_location_property(botengine, "task.__init__", True, track=False)
                if hasattr(domain, "CARE_SERVICES"):
                    if domain.CARE_SERVICES:
                        tasks.update_task(botengine,
                                          location_object=self.parent,
                                          task_id="__init__",
                                          title=_("Learn how to create tasks."),
                                          comment=_("Use {} to easily create and assign household tasks to family and friends!\n"
                                                    "\n"
                                                    "\t1. Tap the [+] button on your Dashboard.\n"
                                                    "\t2. Select 'Add a Task'.\n"
                                                    "\t3. Fill out details of the task.\n"
                                                    "\n"
                                                    "To assign a task to someone, first invite them to your home. Set their Smart Home Access to 'Allow App Access' and Alert Texting to anything except 'No Alerts'.\n"
                                                    "\n"
                                                    "People can use their {} app to mark their tasks complete, and you will get notified. Enjoy!").format(domain.SERVICE_NAME, domain.SERVICE_NAME))

        return

    def device_deleted(self, botengine, device_object):
        """
        Device is getting deleted
        :param botengine: BotEngine environment
        :param device_object: Device object that is getting deleted
        """
        return

    def question_answered(self, botengine, question_object):
        """
        The user answered a question
        :param botengine: BotEngine environment
        :param question_object: Question object
        """
        return

    def datastream_updated(self, botengine, address, content):
        """
        Data Stream Message Received
        :param botengine: BotEngine environment
        :param address: Data Stream address
        :param content: Content of the message
        """
        if hasattr(self, address):
            getattr(self, address)(botengine, content)

    def schedule_fired(self, botengine, schedule_id):
        """
        The bot executed on a hard coded schedule specified by our runtime.json file
        :param botengine: BotEngine environment
        :param schedule_id: Schedule ID that is executing from our list of runtime schedules
        """
        return

    def timer_fired(self, botengine, argument):
        """
        The bot's intelligence timer fired
        :param botengine: Current botengine environment
        :param argument: Argument applied when setting the timer
        """
        return

    def file_uploaded(self, botengine, device_object, file_id, filesize_bytes, content_type, file_extension):
        """
        A device file has been uploaded
        :param botengine: BotEngine environment
        :param device_object: Device object that uploaded the file
        :param file_id: File ID to reference this file at the server
        :param filesize_bytes: The file size in bytes
        :param content_type: The content type, for example 'video/mp4'
        :param file_extension: The file extension, for example 'mp4'
        """
        return

    def coordinates_updated(self, botengine, latitude, longitude):
        """
        Approximate coordinates of the parent proxy device object have been updated
        :param latitude: Latitude
        :param longitude: Longitude
        """
        return

    def user_role_updated(self, botengine, user_id, alert_category, location_access, previous_alert_category, previous_location_access):
        """
        A user changed roles
        :param botengine: BotEngine environment
        :param user_id: User ID that changed roles
        :param alert_category: User's current alert/communications category (1=resident; 2=supporter)
        :param location_access: User's access to the location and devices. (0=None; 10=read location/device data; 20=control devices and modes; 30=update location info and manage devices)
        :param previous_alert_category: User's previous category, if any
        :param previous_location_access: User's previous access to the location, if any
        """
        return

    def data_request_ready(self, botengine, reference, csv_dict):
        """
        A botengine.request_data() asynchronous request for CSV data is ready.

        This is part of a very scalable method to extract large amounts of data from the server for the purpose of
        machine learning services. If a service needs to extract a large amount of data for one or multiple devices,
        the developer should call botengine.request_data(..) and also allow the bot to trigger off of trigger type 2048.
        The bot can exit its current execution. The server will independently gather all the necessary data and
        capture it into a LZ4-compressed CSV file on the server which is available for one day and accessible only by
        the bot through a public HTTPS URL identified by a cryptographic token. The bot then gets triggered and
        downloads the CSV data, passing the data throughout the environment with this data_request_ready()
        event-driven method.

        Developers are encouraged to use the 'reference' argument inside calls to botengine.request_data(..). The
        reference is passed back out at the completion of the request, allowing the developer to ensure the
        data request that is now available was truly destined for their microservice.

        Your bots will need to include the following configuration for data requests to operate:
        * runtime.json should include trigger 2048
        * structure.json should include inside 'pip_install_remotely' a reference to the "lz4" Python package

        :param botengine: BotEngine environment
        :param reference: Optional reference passed into botengine.request_data(..)
        :param csv_dict: { device_object: 'csv data string' }
        """
        return

    def update_task(self, botengine, content):
        """
        Add or Update a task - Data Stream Message
        https://presence.atlassian.net/wiki/spaces/BOTS/pages/739573895/update+task+Add+or+Update+a+Task+Data+Stream+Message
        :param botengine:
        :param content:
        :return:
        """
        if 'id' not in content:
            botengine.get_logger().warning("location_tasks_microservice: update_task() called with no 'id' in content: {}; trigger={}; inputs={}".format(content, botengine.get_trigger_type(), botengine.inputs))
            raise ValueError

        tasks = botengine.get_ui_content("tasks")
        if tasks is None:
            tasks = {}

        task_id = content.pop("id")
        for key in dict(content):
            if content[key] is None:
                del content[key]

        if 'title' in content:
            assigned_to_name = None

            if 'assigned_to' in content:
                if content['assigned_to'] is not None:
                    assigned_user_object = botengine.get_location_user(int(content['assigned_to']))
                    if assigned_user_object is None:
                        del(content['assigned_to'])
                    else:
                        assigned_to_name = self.get_contact_name(botengine, assigned_user_object)

            created_by_name = None
            if 'created_by' in content:
                if content['created_by'] is not None:
                    created_user_object = botengine.get_location_user(int(content['created_by']))
                    if created_user_object is None:
                        del(content['created_by'])
                    else:
                        created_by_name = self.get_contact_name(botengine, created_user_object)

            if task_id not in tasks:
                # This is a new task
                if created_by_name is None and assigned_to_name is None:
                    description = _("A task was added: {}").format(content['title'])

                elif created_by_name is not None and assigned_to_name is None:
                    description = _("{} added a task: {}").format(created_by_name, content['title'])

                elif created_by_name is None and assigned_to_name is not None:
                    description = _("A task was assigned to {}: {}").format(assigned_to_name, content['title'])
                    botengine.notify(push_content=_("You've been assigned a new task."), user_id=content['assigned_to'])

                else:
                    if created_by_name == assigned_to_name:
                        description = _("{} will take on a new task: {}").format(created_by_name, content['title'])
                    else:
                        description = _("{} assigned a task to {}: {}").format(created_by_name, assigned_to_name, content['title'])
                        push_sms_fallback_content = _("{} assigned you a new task. To view it and mark it complete, please download and sign into the {} app.").format(created_by_name, domain.SERVICE_NAME)

                        ios_url = None
                        android_url = None

                        if hasattr(domain, 'APP_IOS_URL'):
                            ios_url = domain.APP_IOS_URL

                        if hasattr(domain, 'APP_ANDROID_URL'):
                            android_url = domain.APP_ANDROID_URL

                        if ios_url is not None:
                            # Note: iOS app download URL qualifier
                            push_sms_fallback_content += "\n\n{}: {}".format(_("iPhone / iPad"), ios_url)

                        if android_url is not None:
                            # Note: Android download URL qualifier
                            push_sms_fallback_content += "\n\n{}: {}".format(_("Android"), android_url)

                        botengine.notify(push_content=_("{} assigned you a new task: '{}'").format(created_by_name, content['title']), user_id=content['assigned_to'], push_sms_fallback_content=push_sms_fallback_content)

                self.parent.narrate(botengine,
                                    title=_("Task created"),
                                    description=description,
                                    priority=botengine.NARRATIVE_PRIORITY_INFO,
                                    icon="tasks",
                                    extra_json_dict={
                                        "task_id": task_id
                                    })

                dailyreport.add_entry(botengine, self.parent, dailyreport.SECTION_ID_TASKS, comment=description, include_timestamp=True)
                content['created'] = botengine.get_timestamp()

                if not task_id.startswith("__"):
                    # This is not a system task
                    analytics.track(botengine, self.parent, "task_created")

            else:
                # This is updating an existing task
                if created_by_name is None and assigned_to_name is None:
                    description = _("A task was updated: {}").format(content['title'])

                elif created_by_name is not None and assigned_to_name is None:
                    description = _("{} updated a task: {}").format(created_by_name, content['title'])

                elif created_by_name is None and assigned_to_name is not None:
                    description = _("Updated a task assigned to {}: {}").format(assigned_to_name, content['title'])
                    botengine.notify(push_content=_("A task assigned to you has been updated.").format(content['title']), user_id=content['assigned_to'])

                else:
                    if created_by_name == assigned_to_name:
                        description = _("{} updated a task: {}").format(created_by_name, content['title'])
                    else:
                        description = _("{} updated a task assigned to {}: {}").format(created_by_name, assigned_to_name, content['title'])
                        botengine.notify(push_content=_("{} updated a task assigned to you.").format(created_by_name), user_id=content['assigned_to'])

                self.parent.narrate(botengine,
                                    title=_("Task created"),
                                    description=description,
                                    priority=botengine.NARRATIVE_PRIORITY_INFO,
                                    icon="tasks",
                                    extra_json_dict={
                                        "task_id": task_id
                                    })

            content['updated'] = botengine.get_timestamp()
            tasks[task_id] = content

        elif task_id in tasks:
            # A task was deleted
            deleted_by_name = None
            if 'deleted_by' in content:
                deleted_user_object = botengine.get_location_user(int(content['deleted_by']))
                if deleted_user_object is not None:
                    deleted_by_name = self.get_contact_name(botengine, deleted_user_object)

            if deleted_by_name is not None and 'title' in tasks[task_id]:
                description = _("{} marked a task complete: {}").format(deleted_by_name, tasks[task_id]['title'])

                if 'created_by' in tasks[task_id]:
                    if tasks[task_id]['created_by'] is not None:
                        if int(tasks[task_id]['created_by']) != int(content['deleted_by']):
                            botengine.notify(push_content=_("{} completed a task: '{}'").format(deleted_by_name, tasks[task_id]['title']), user_id=tasks[task_id]['created_by'])

            else:
                description = _("A task was marked complete: {}").format(tasks[task_id]['title'])

            self.parent.narrate(botengine,
                                title=_("Task completed"),
                                description=description,
                                priority=botengine.NARRATIVE_PRIORITY_INFO,
                                icon="check-square")

            dailyreport.add_entry(botengine, self.parent, dailyreport.SECTION_ID_TASKS, comment=description, include_timestamp=True)

            if not task_id.startswith("__"):
                # This is not a system task, track it
                properties = None
                if 'created' in tasks[task_id]:
                    properties = {"elapsed_ms": botengine.get_timestamp() - tasks[task_id]['created']}

                analytics.track(botengine, self.parent, "task_completed", properties=properties)

            del(tasks[task_id])

        self.parent.set_location_property_separately(botengine, "tasks", tasks, overwrite=True)

    def delete_task(self, botengine, content):
        """
        Delete a task - Data Stream Message
        https://presence.atlassian.net/wiki/spaces/BOTS/pages/739377286/delete+task+Delete+an+existing+task+Data+Stream+Message
        :param botengine:
        :param content:
        :return:
        """
        self.update_task(botengine, content)


    def get_contact_name(self, botengine, contact):
        """
        Get the first name of the contact. May return "" if the contact has no name.
        :param botengine:
        :param contact:
        :return:
        """
        contact_name = ""

        if 'firstName' in contact:
            if contact['firstName'].strip() != "":
                contact_name = contact['firstName'].strip()

        if 'lastName' in contact:
            if contact['lastName'].strip() != "":
                contact_name += " " + contact['lastName'].strip()

        return contact_name.strip()