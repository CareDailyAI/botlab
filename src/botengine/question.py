"""
Question class for botlab
"""

class Question:
    """
    Class to hold a question and its answer
    """

    # Question Responses
    QUESTION_RESPONSE_TYPE_BOOLEAN = 1
    QUESTION_RESPONSE_TYPE_MULTICHOICE_SINGLESELECT = 2
    QUESTION_RESPONSE_TYPE_MULTICHOICE_MULTISELECT = 4
    QUESTION_RESPONSE_TYPE_DAYOFWEEK = 6
    QUESTION_RESPONSE_TYPE_SLIDER = 7
    QUESTION_RESPONSE_TYPE_TIME = 8
    QUESTION_RESPONSE_TYPE_DATETIME = 9
    QUESTION_RESPONSE_TYPE_TEXT = 10

    # Question display types
    # BOOLEAN QUESTIONS
    QUESTION_DISPLAY_BOOLEAN_ONOFF = 0
    QUESTION_DISPLAY_BOOLEAN_YESNO = 1
    QUESTION_DISPLAY_BOOLEAN_BUTTON = 2
    QUESTION_DISPLAY_BOOLEAN_THUMBS = 3

    # MULTIPLE CHOICE - SINGLE SELECT QUESTIONS
    QUESTION_DISPLAY_MCSS_RADIO_BUTTONS = 0
    QUESTION_DISPLAY_MCSS_PICKER = 1
    QUESTION_DISPLAY_MCSS_SLIDER = 2
    QUESTION_DISPLAY_MCSS_MODAL_BOTTOM_SHEET = 3

    # DAY OF WEEK QUESTIONS
    QUESTION_DISPLAY_DAYOFWEEK_MULTISELECT = 0
    QUESTION_DISPLAY_DAYOFWEEK_SINGLESELECT = 1

    # SLIDER
    QUESTION_DISPLAY_SLIDER_INTEGER = 0
    QUESTION_DISPLAY_SLIDER_FLOAT = 1
    QUESTION_DISPLAY_SLIDER_MINSEC = 2

    # TIME
    QUESTION_DISPLAY_TIME_HOURS_MINUTES_SECONDS_AMPM = 0
    QUESTION_DISPLAY_TIME_HOURS_MINUTES_AMPM = 1

    # DATETIME
    QUESTION_DISPLAY_DATETIME_DATE_AND_TIME = 0
    QUESTION_DISPLAY_DATETIME_DATE = 1

    # Answer Status
    ANSWER_STATUS_NOT_ASKED = -1
    ANSWER_STATUS_DELAYED = 0
    ANSWER_STATUS_QUEUED = 1
    ANSWER_STATUS_AVAILABLE = 2
    ANSWER_STATUS_SKIPPED = 3
    ANSWER_STATUS_ANSWERED = 4
    ANSWER_STATUS_NO_ANSWER = 5

    def __init__(
        self,
        key_identifier,
        response_type,
        device_id=None,
        icon=None,
        icon_font=None,
        display_type=None,
        collection=None,
        editable=False,
        default_answer=None,
        correct_answer=None,
        answer_format=None,
        urgent=False,
        front_page=False,
        send_push=False,
        send_sms=False,
        send_email=False,
        ask_timestamp=None,
        section_id=0,
        question_weight=0,
    ):
        """
        Initializer

        :param key_identifier: Your own custom key to recognize this question regardless of the language or framing of the question to the user.
        :param response_type: Type of response we should expect the user to give
            1 = Boolean question
            2 = Multichoice, Single select (requires response options)
            4 = Multichoice, Multi select (requires response options)
            6 = Day of the Week
            7 = Slider (Default minimum is 0, default maximum is 100, default increment is 5)
            8 = Time in seconds since midnight
            9 = Datetime (xsd:dateTime format)
            10 = Open-ended text

        :param device_id: Device ID to ask a question about so the UI can reference its name
        :param icon: Icon to display when asking this question. See http://peoplepowerco.com/icons or http://fontawesome.com
        :param icon_font: Icon font to render the icon. See the ICON_FONT_* descriptions in com.ppc.Bot/utilities/utilities.py
        :param display_type: How to render and display the question in the UI. For example, a Boolean question can be an on/off switch, a yes/no question, or just a single button. See the documentation for more details.
        :param collection: Collection name
        :param editable: True to make this question editable later. This makes the question more like a configuration for the bot that can be adjusted again and again, rather than a one-time question.
        :param default_answer: Default answer for the question
        :param correct_answer: This is a regular expression to determine if the user's answer is "correct" or not
        :param answer_format: Regular expression string that represents what a valid response would look like. All other responses would not be allowed.
        :param urgent: True if this question is urgent enough that it requires a push notification and should be elevated to the top of the stack after any current delivered questions. Use sparingly to avoid end-user burnout.
        :param front_page: True if this question should be delivered to the front page of mobile/web bot, when the user is ready to consume another question from the system.
        :param send_push: True to send this questions as a push notification. Use sparingly to avoid end user burnout.
        :param send_sms: True to send an SMS message. Because this costs money, this is currently disabled.
        :param send_email: True to send the question in an email. Use sparingly to avoid burnout and default to junk mail.
        :param ask_timestamp: Future timestamp to ask this question. If this is not set, the current time will be used.
        :param section_id: ID of a section, which acts as both the element to group by as well as the weight of the section vs. other sections in the UI. (default is 0)
        :param question_weight: Weight of an individual question within a grouped section. The lighter the weight, the more the question rises to the top of the list in the UI. (default is 0)
        """
        self._question_id = None
        self.key_identifier = key_identifier
        self.response_type = response_type
        self.device_id = device_id
        self.icon = icon
        self.icon_font = icon_font
        self.display_type = display_type
        self.editable = editable
        self.urgent = urgent
        self.front_page = front_page
        self.send_push = send_push
        self.send_sms = send_sms
        self.send_email = send_email
        self.correct_answer = correct_answer
        self.answer_format = answer_format
        self.default_answer = default_answer
        self.ask_timestamp = ask_timestamp
        self.tags = []
        self.question = {}
        self.placeholder = {}
        self.response_options = []
        self.section_title = {}
        self.section_id = section_id
        self.question_weight = question_weight
        self.answer_status = self.ANSWER_STATUS_NOT_ASKED
        self.answer_time = None
        self.answer = None
        self.answer_correct = False
        self.answer_modified = False
        self.slider_min = 0
        self.slider_max = None
        self.slider_inc = None
        self.slider_min_description = None
        self.slider_max_description = None
        self.slider_unit = None
        self.collection = collection

        # The user ID who answered this question
        self.user_id = None

        if response_type == self.QUESTION_RESPONSE_TYPE_SLIDER:
            if display_type == self.QUESTION_DISPLAY_SLIDER_MINSEC:
                # Minutes:Seconds slider - 60:00 max by default, in increments of 0:15 seconds
                self.slider_max = 3600
                self.slider_inc = 15

            else:
                # Float and Integer slider - 100 max by default, in increments of 5
                self.slider_max = 100
                self.slider_inc = 5
            self.slider_min_description = None
            self.slider_unit = None

    def _boolean_to_str(self, value):
        if isinstance(value, bool):
            if value:
                return "true"
            else:
                return "false"

        return value

    def _form_json_question(self, logger):
        """
        Private function to form the JSON request to POST this question
        :return: JSON string ready to send to the server
        """
        body = {
            "key": self.key_identifier,
            "urgent": self.urgent,
            "front": self.front_page,
            "push": self.send_push,
            "sms": self.send_sms,
            "email": self.send_email,
            "responseType": self.response_type,
            "editable": self.editable,
            "question": self.question,
        }

        if self.device_id is not None:
            body["deviceId"] = self.device_id

        # Added May 27, 2020
        if hasattr(self, "icon_font"):
            if self.icon_font is not None:
                body["iconFont"] = self.icon_font

        else:
            self.icon_font = None

        if self.icon is not None:
            body["icon"] = self.icon

        if self.display_type is not None:
            body["displayType"] = int(self.display_type)

        if len(self.section_title) > 0:
            body["sectionTitle"] = self.section_title

        if self.section_id is not None:
            body["sectionId"] = int(self.section_id)

        if self.question_weight is not None:
            body["questionWeight"] = int(self.question_weight)

        if self.ask_timestamp:
            body["askDateMs"] = self.ask_timestamp

        if len(self.placeholder) > 0:
            body["placeholder"] = self.placeholder

        if self.response_type == self.QUESTION_RESPONSE_TYPE_SLIDER:
            slider = {}
            slider["min"] = self.slider_min
            slider["max"] = self.slider_max
            slider["inc"] = self.slider_inc

            if self.slider_min_description is not None:
                slider["minDesc"] = self.slider_min_description
            if self.slider_max_description is not None:
                slider["maxDesc"] = self.slider_max_description
            if self.slider_unit is not None:
                slider["unitsDesc"] = self.slider_unit

            body["slider"] = slider

            if self.default_answer is None:
                self.default_answer = int((self.slider_max - self.slider_min) / 2)

        if len(self.tags) > 0:
            body["tags"] = self.tags

        if self.answer is not None:
            # We've already gotten an answer to this question and we're asking it again, don't lose the previous answer.
            self.default_answer = self.answer

        if self.default_answer is not None:
            body["defaultAnswer"] = self._boolean_to_str(self.default_answer)

        if self.correct_answer:
            body["validAnswer"] = self.correct_answer

        if self.answer_format:
            body["answerFormat"] = self.answer_format

        if not hasattr(self, "collection"):
            self.collection = None

        if self.collection:
            body["collectionName"] = self.collection

        if (
            self.response_type == self.QUESTION_RESPONSE_TYPE_MULTICHOICE_MULTISELECT
            or self.response_type
            == self.QUESTION_RESPONSE_TYPE_MULTICHOICE_SINGLESELECT
        ):
            body["responseOptions"] = []
            identifier = 0
            for option in self.response_options:
                if isinstance(option, dict):
                    try:
                        logger.warning("|_form_json_question() Malformed question response option {}: {}".format(body, option))
                    except Exception:
                        pass
                    body["responseOptions"].append(option)
                else:
                    body["responseOptions"].append(option._get_json_dictionary(identifier))
                identifier += 1

        return body

    def get_id(self):
        """
        :return: Server-generated Question ID, or None if this question hasn't been saved to the server yet.
        """
        return self._question_id

    def frame_question(self, question, language="en"):
        """
        Frame question in a specific language

        :param question: The question to ask in that language
        :param language: 'en', 'zh', etc. Default is 'en'
        """
        self.question[language] = question

    def slider_boundaries(self, slider_min=0, slider_max=100, slider_inc=5):
        """
        Set the boundaries of a question that expects a response in the form of a slider
        :param slider_min: Minimum slider boundary, default is 0
        :param slider_max: Maximum slider boundary, default is 100
        :param slider_inc: Incremental slider amount, default is 5
        """
        self.slider_min = slider_min
        self.slider_max = slider_max
        self.slider_inc = slider_inc

    def slider_description(self, minimum=None, maximum=None, unit=None):
        """
        Set the description of a slider question
        :param minimum: Minimum slider description
        :param maximum: Maximum slider description
        :param unit: Unit of the slider
        """
        self.slider_min_description = minimum
        self.slider_max_description = maximum
        self.slider_unit = unit

    def set_placeholder_text(self, placeholder, language="en"):
        """
        A placeholder adds an example to a question that expects a text-based response.
        For example, if the question was "What is your favorite color?" then the placeholder might be "Blue" in English.

        :param placeholder: Open-ended text example to prompt the user to type in their own answer.
        :param language: Language for the placeholder, 'en', 'zh', etc. Default is "en".
        """
        self.placeholder[language] = placeholder

    def set_section_title(self, section_title, language="en"):
        """
        Set the section title.
        The top most question in the section (lowest weight) sets the title.

        :param section_title: Name of the section of questions
        :param language: Language for this section title, default is 'en'
        """
        self.section_title[language] = section_title

    def set_default_answer(self, default_answer):
        """
        Set default answer.

        :param default_answer: Name of the section of questions
        """
        self.default_answer = default_answer

    def set_editable(self, editable):
        """
        Set the question is editable.

        :param editable: Question is editable
        """
        self.editable = editable

    def auto_tag_user(self, tag):
        """
        Auto-tag the user with this tag if they provide is the "correct" response, based on the correct_answer regular expression.
        Cannot be used with any list-type questions.
        Can be called multiple times to add multiple tags:  this simply does a self.tags.append(tag) so you could alternatively
        set it in a more Pythonic way by doing something like:  question.tags = ["tag1","tag2"]

        :param tag: Tag to tag the user's account with if they provide any valid response.
        """
        self.tags.append(tag)

    def generate_response_option(self, text=None, language="en"):
        """
        Get a QuestionResponseOption object
        :param text: Text for this response option
        :param language: Language identifier for that text, i.e. 'en'
        :return: QuestionResponseOption object that has been added to this question, for yours to edit
        """
        option = QuestionResponseOption(len(self.response_options), text, language)
        self.response_options.append(option)
        return option

    def ready_to_ask(self):
        """
        :return: True if this question is ready to ask
        """
        if len(self.question) == 0:
            return False

        if (
            self.response_type == self.QUESTION_RESPONSE_TYPE_RADIO
            or self.response_type == self.QUESTION_RESPONSE_TYPE_DROPDOWN
            or self.response_type == self.QUESTION_RESPONSE_TYPE_CHECKBOX
            or self.response_type == self.QUESTION_RESPONSE_TYPE_MULTISELECT
        ):
            return len(self.response_options) > 0

        return True

class QuestionResponseOption:
    """
    A single response option to a question that is a radio button, drop-down list, checkbox, or multi-select type of question
    """

    def __init__(self, identifier, text=None, language="en"):
        """
        Initialize
        :param identifier: Unique incremental identifier for this response, starting with 0
        :param text: Text for this response option
        :param language: Language identifier for that text, i.e. 'en'
        """
        self.identifier = identifier
        self.text = {}
        self.tags = []
        self.complete = False

        if text is not None:
            self.add_text(text, language)

    def _get_json_dictionary(self, identifier):
        """
        Private method to get a dictionary representing the content that needs to get injected into a JSON API POST
        :param identifier: id of this response option relative to other option, starting with 0
        :return: Dictionary formatted to conform to the POST API
        """
        block = {"id": identifier, "text": self.text}

        if len(self.tags) > 0:
            block["tags"] = self.tags

        return block

    def add_text(self, text, language="en"):
        """
        Add some text to this question's response option, in a specificied language

        :param text: Text for this option
        :param language: Language abbreviation, 'en' by default
        :return: self, so you can keep adding more if you want.
        """
        self.complete = True
        self.text[language] = text
        return self

    def add_tag(self, tag):
        """
        Tag a user with this tag if they answer in this way

        :param tag: Tag to tag the user with if they answer the question in this way
        :return: self, so you can keep adding more if you want.
        """
        self.tags.append(tag)
        return self