'''
Created on September 12, 2019

This file is subject to the terms and conditions defined in the
file 'LICENSE.txt', which is part of this source code package.

@author: David Moss
'''

from intelligence.intelligence import Intelligence
import utilities.utilities as utilities
import json

NOW_UI_PROPERTY_NAME = "now"
SERVICES_UI_PROPERTY_NAME = "services"

# Types of cards
CARD_TYPE_NOW = 0
CARD_TYPE_SERVICES = 1

# Timestamped commands
COMMAND_DELETE = -2
COMMAND_SET_STATUS_HIDDEN = -1
COMMAND_SET_STATUS_GOOD = 0
COMMAND_SET_STATUS_WARNING = 1
COMMAND_SET_STATUS_CRITICAL = 2

class LocationDashboardMicroservice(Intelligence):
    """
    Dashboard Manager
    https://presence.atlassian.net/wiki/spaces/BOTS/pages/735379952/dashboard+Dashboard+content+for+Presence+Family+based+apps
    """

    def __init__(self, botengine, parent):
        """
        Instantiate this object
        :param parent: Parent object, either a location or a device object.
        """
        Intelligence.__init__(self, botengine, parent)

        # List of content ID's we're tracking
        self.content_id = []

        # New bot? Destroy all previous dashboard content.
        self.destroy(botengine)

    def new_version(self, botengine):
        """
        Upgraded to a new bot version
        :param botengine: BotEngine environment
        """
        return

    def update_dashboard_content(self, botengine, card_content):
        """
        Update a dashboard card - Data Stream Message

        # Create/Update a card
        card_content = {
            "type": 0,
            "title": "NOW",
            "weight": 0,
            "content": {
                "status": 0,
                "comment": "Sleeping since 10:35 PM.",
                "weight": 0,
                "id": "unique_content_id",
                "icon": "icon",
                "alarms": {
                    timestamp_0_ms : command_0,
                    timestamp_1_ms : command_1,
                    timestamp_2_ms : command_2
                }
            }
        }

        # Delete a card
        card_content = {
            "type": 0,
            "title": "NOW",
            "content": {
                "comment": None,
                "id": "unique_content_id"
            }
        }

        :param botengine:
        :param card_content:
        :return:
        """
        botengine.get_logger(f"{__name__}.{__class__.__name__}").info(">update_dashboard_content() card_content={}".format(json.dumps(card_content)))

        if 'content' not in card_content or 'type' not in card_content or 'title' not in card_content:
            botengine.get_logger(f"{__name__}.{__class__.__name__}").warning("<update_dashboard_content() Missing 'content', 'type', or 'title' elements. card_content={}".format(json.dumps(card_content)))
            return

        section_title = card_content['title']
        comment = None
        if 'comment' in card_content['content']:
            comment = card_content['content']['comment']

        if comment is None:
            if card_content['content']['id'] not in self.content_id:
                # This doesn't exist already, take no action.
                botengine.get_logger(f"{__name__}.{__class__.__name__}").warning("<update_dashboard_content() No content to updated. card_content={}".format(json.dumps(card_content)))
                return

        # Delete all possible alarms associated with this content for command ID's -2, -1, 0, 1, 2:
        for command_id in range(-2, 3):
            self.cancel_alarms(botengine, reference="{}-{}".format(card_content['content']['id'], command_id))

        if card_content['type'] == CARD_TYPE_NOW:
            focused_dashboard = botengine.get_state(NOW_UI_PROPERTY_NAME)

        elif card_content['type'] == CARD_TYPE_SERVICES:
            focused_dashboard = botengine.get_state(SERVICES_UI_PROPERTY_NAME)

        else:
            botengine.get_logger(f"{__name__}.{__class__.__name__}").error("|update_dashboard_content() Unknown card type. card_content={}".format(json.dumps(card_content)))

        if focused_dashboard is None:
            focused_dashboard = {
                "cards": []
            }

        # 2020.07.28
        # Remove a botched set of cards as we force-replaced the title.
        if 'cards' in focused_dashboard:
            for index, c in enumerate(focused_dashboard['cards']):
                if 'title' in c:
                    if c['title'] == "SERVICES":
                        del focused_dashboard['cards'][index]
                        break

        if comment is not None:
            # Update the content

            # First try to find an existing card to put this content into.
            focused_card = None
            if 'cards' in focused_dashboard:
                for card in focused_dashboard['cards']:
                    if card['title'] == card_content['title']:
                        focused_card = card
                        break

            if focused_card is None:
                # No existing card, so create it.
                focused_card = {
                    "type": card_content['type'],
                    "title": card_content['title'],
                    "weight": card_content['weight'],
                    "content": []
                }
                focused_dashboard['cards'].append(focused_card)

            # Next try to find some existing content to update
            focused_content_index = None
            for index, content in enumerate(focused_card['content']):
                try:
                    if content['id'] == card_content['content']['id']:
                        focused_content_index = index
                        break
                except Exception as e:
                    import traceback
                    botengine.get_logger(f"{__name__}.{__class__.__name__}").warning("|update_dashboard_content() Error parsing content. Error={} trace={}".format(e, traceback.format_exc()))
                    pass

            if card_content['content']['id'] not in self.content_id:
                self.content_id.append(card_content['content']['id'])

            card_content['content']['updated'] = botengine.get_timestamp()

            if focused_content_index is not None:
                # Update the existing content
                focused_card['content'][focused_content_index] = card_content['content']

            else:
                # No existing content, inject it.
                focused_card['content'].append(card_content['content'])

        else:
            # Delete the content from the card, and possibly the card itself.
            try:
                for card_index, card in enumerate(list(focused_dashboard['cards'])):
                    if card['title'] == card_content['title']:
                        for content_index, content in enumerate(card['content']):
                            if content['id'] == card_content['content']['id']:
                                # Delete the content from the card.
                                del(focused_dashboard['cards'][card_index]['content'][content_index])

                                if card_content['content']['id'] in self.content_id:
                                    self.content_id.remove(card_content['content']['id'])

                                # Check if the card is empty so we can delete it too.
                                if len(focused_dashboard['cards'][card_index]['content']) == 0:
                                    # Delete the card from the focused_dashboard.
                                    del(focused_dashboard['cards'][card_index])

                                raise StopIteration

            except StopIteration:
                pass

        # Delete cards that are too old
        for card_index, card in enumerate(focused_dashboard['cards']):
            if card['type'] == 0:
                for content_index, content in enumerate(card['content']):
                    if 'updated' not in content:
                        # Delete yourself
                        content['updated'] = botengine.get_timestamp() - utilities.ONE_MONTH_MS

                    if content['updated'] < (botengine.get_timestamp() - utilities.ONE_WEEK_MS):
                        # This content is older than a week. Is there anything keeping it alive?
                        okay = False
                        if 'alarms' in content:
                            for alarm_ms in list(content['alarms']):
                                if int(alarm_ms) > botengine.get_timestamp() - utilities.ONE_DAY_MS:
                                    # Alarm just triggered or will trigger in the future... you get to live another day
                                    okay = True
                                    break

                        if not okay:
                            # Kill it.
                            botengine.get_logger(f"{__name__}.{__class__.__name__}").warning("|update_dashboard_content() Deleting orphaned card '{}' which is older than a week and a day. content={}".format(content.get('comment'), json.dumps(content)))
                            del(focused_dashboard['cards'][card_index]['content'][content_index])

                            if card_content['content']['id'] in self.content_id:
                                self.content_id.remove(card_content['content']['id'])

                            # Check if the card is empty so we can delete it too.
                            if len(focused_dashboard['cards'][card_index]['content']) == 0:
                                # Delete the card from the focused_dashboard.
                                del (focused_dashboard['cards'][card_index])

        # After pruning out orphaned cards, find the next alarm to set
        next_alarm_ms = None
        for card in focused_dashboard['cards']:
            for content in card['content']:
                if 'alarms' in content:
                    for alarm_ms in list(content['alarms']):
                        if next_alarm_ms is None:
                            next_alarm_ms = int(alarm_ms)

                        elif int(alarm_ms) < next_alarm_ms:
                            next_alarm_ms = int(alarm_ms)

        if next_alarm_ms is not None:
            botengine.get_logger(f"{__name__}.{__class__.__name__}").info("|update_dashboard_content() Setting alarm for {} ms from now.".format(int(next_alarm_ms) - botengine.get_timestamp()))
            self.set_alarm(botengine, next_alarm_ms)

        # Sort it out
        for card in focused_dashboard['cards']:
            card['content'].sort(key=lambda x: (x.get('weight', 50), x.get('updated', botengine.get_timestamp())))
        focused_dashboard['cards'].sort(key=lambda x: x.get('weight', 50))

        # Save
        if card_content['type'] == CARD_TYPE_NOW:
            botengine.get_logger(f"{__name__}.{__class__.__name__}").debug("|update_dashboard_content() Saving now dashboard content. focused_dashboard={}".format(json.dumps(focused_dashboard)))
            self.parent.set_location_property_separately(botengine, NOW_UI_PROPERTY_NAME, focused_dashboard, overwrite=True)

        elif card_content['type'] == CARD_TYPE_SERVICES:
            botengine.get_logger(f"{__name__}.{__class__.__name__}").debug("|update_dashboard_content() Saving services dashboard content. focused_dashboard={}".format(json.dumps(focused_dashboard)))
            self.parent.set_location_property_separately(botengine, SERVICES_UI_PROPERTY_NAME, focused_dashboard, overwrite=True)
        botengine.get_logger(f"{__name__}.{__class__.__name__}").info("<update_dashboard_content()")

    def destroy(self, botengine):
        """
        This device or object is getting permanently deleted - it is no longer in the user's account.
        :param botengine: BotEngine environment
        """
        self.parent.set_location_property_separately(botengine, NOW_UI_PROPERTY_NAME, {"cards": []})
        self.parent.set_location_property_separately(botengine, SERVICES_UI_PROPERTY_NAME, {"cards": []})

    def timer_fired(self, botengine, argument):
        """
        The bot's intelligence timer fired
        :param botengine: Current botengine environment
        :param argument: Argument applied when setting the timer
        """
        dashboard = botengine.get_state(NOW_UI_PROPERTY_NAME)

        if dashboard is None:
            botengine.get_logger(f"{__name__}.{__class__.__name__}").warning("<timer_fired() No saved dashboard content.")
            return

        if 'cards' not in dashboard:
            botengine.get_logger(f"{__name__}.{__class__.__name__}").warning("<timer_fired() No 'cards' in saved dashboard content.")
            return

        import copy
        for card in dashboard['cards']:
            for content in card['content']:
                if 'alarms' in content:
                    for alarm_ms in sorted(list(content['alarms'])):
                        if int(alarm_ms) <= botengine.get_timestamp():
                            # Execute this alarm.
                            if alarm_ms in content['alarms']:
                                content['status'] = content['alarms'][alarm_ms]

                                if content['status'] == COMMAND_DELETE:
                                    content['comment'] = None

                                updated_card_content = {
                                    "type": card['type'],
                                    "title": card['title'],
                                    "weight": card['weight'],
                                    "content": content,
                                    "updated": botengine.get_timestamp()
                                }

                                # Prune out this alarm and older
                                for index, timestamp_ms in enumerate(dict(updated_card_content['content']['alarms'])):
                                    if int(timestamp_ms) < botengine.get_timestamp():
                                        del (updated_card_content['content']['alarms'][timestamp_ms])

                                botengine.get_logger(f"{__name__}.{__class__.__name__}").info("|timer_fired() Alarm fired - Updating card content status: {}".format(updated_card_content))
                                self.update_dashboard_content(botengine, updated_card_content)
        botengine.get_logger(f"{__name__}.{__class__.__name__}").info("<timer_fired()")
