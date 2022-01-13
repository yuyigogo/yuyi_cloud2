from mongoengine.document import Document
from mongoengine.fields import ListField


class ScriptEvidence(Document):
    """
    Handler used to keep an evidence with which scripts were run, so the scripts will
    not be executed twice
    """

    scripts_name = ListField()

    @classmethod
    def get_or_create_collection(cls):
        """
        gets or creates the collection ScriptEvidence
        :return: collection ScriptEvidence
        """

        script_evidence = ScriptEvidence.objects()

        if script_evidence.count() == 0:
            script_evidence = ScriptEvidence().save()
        else:
            script_evidence = script_evidence[0]

        return script_evidence
