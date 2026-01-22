"""
Lesson 11 - Questions

Demonstrates how to:
- Ask a question (bot -> UI)
- Receive an answer (UI -> bot trigger)
- Persist the answer into a location property/state for use by other microservices/UIs
"""

from intelligence.intelligence import Intelligence  # type: ignore


QUESTION_KEY = "lesson11.enable_questions"
STATE_ADDRESS = "lesson11/questions"
LOCATION_PROPERTY_KEY = "lesson11_enable_questions"


class LocationQuestionsMicroservice(Intelligence):
    """
    A small location-level microservice demonstrating bot questions.
    """

    def __init__(self, botengine, parent):
        super().__init__(botengine, parent)

    def initialize(self, botengine):
        """
        Ask a single configuration-style (editable) question if we haven't already
        captured an answer.
        """
        # If already configured, do nothing.
        existing = self.parent.get_location_property(botengine, LOCATION_PROPERTY_KEY)
        if existing is not None:
            return

        # If we've already asked, do not re-ask on every trigger.
        existing_question = botengine.retrieve_question(QUESTION_KEY)
        if existing_question is not None:
            return

        question = botengine.generate_question(
            key_identifier=QUESTION_KEY,
            response_type=botengine.QUESTION_RESPONSE_TYPE_BOOLEAN,
            display_type=botengine.QUESTION_DISPLAY_BOOLEAN_YESNO,
            editable=True,
            default_answer=True,
            front_page=True,
            send_push=False,
            send_email=False,
            urgent=False,
        )

        # Localize the question text.
        question.frame_question(_("Enable Lesson 11 questions?"), language="en")

        botengine.ask_question(question)

        # Expose that we asked, so UIs/microservices can introspect.
        botengine.set_state(
            address=STATE_ADDRESS,
            json_content={
                "questionKey": QUESTION_KEY,
                "asked": True,
                "answered": False,
            },
            overwrite=True,
        )

    def question_answered(self, botengine, question_object):
        """
        Consume the answer and persist it.
        """
        if question_object is None:
            return

        if getattr(question_object, "key_identifier", None) != QUESTION_KEY:
            return

        enabled = getattr(question_object, "answer", None)

        # Normalize booleans that may come through as strings.
        if isinstance(enabled, str):
            enabled = enabled.strip().lower() in ("1", "true", "yes", "y", "on")

        # Persist to a location property (good for other microservices).
        self.parent.set_location_property(
            botengine, LOCATION_PROPERTY_KEY, enabled, track=False
        )

        # Also publish to a stable UI address.
        botengine.set_state(
            address=STATE_ADDRESS,
            json_content={
                "questionKey": QUESTION_KEY,
                "asked": True,
                "answered": True,
                "answer": enabled,
            },
            overwrite=True,
        )

