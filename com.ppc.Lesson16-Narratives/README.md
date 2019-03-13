# Lesson 16 : Narratives

Please reach out to the developers if you would like a tutorial on narratives.

Narratives allow a bot to articulate, in human language, what is happening inside a home. This can allow an auditable trail of history which can be viewed by end users and deciphered by customer support to help diagnose problems and answer questions.

Please see the following methods in com.ppc.Bot/locations/location.py:

    location_object.narrate(self, botengine, title, description, priority, icon, timestamp_ms=None, file_ids=None, extra_json_dict=None, update_narrative_id=None, update_narrative_timestamp=None)
    location_object.delete_narration(self, botengine, narrative_id, narrative_timestamp)
