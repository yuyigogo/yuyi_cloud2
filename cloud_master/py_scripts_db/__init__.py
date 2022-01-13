import logging

from customer.models.customer import Customer

from common.framework.script import BaseHybridCloudScript
from common.utils import get_the_range
from py_scripts_db.models import ScriptEvidence
from py_scripts_db.modify_tev_data import ModifyTEVData

logger = logging.getLogger(__name__)

# for every script added please add the class in the list, and be sure they are in order
SCRIPT_LIST = [ModifyTEVData(),]

NOT_LIMIT_SCRIPT_NAME = {}


class RunScripts:
    """
    Class which will be called to run python scripts
    TO RUN IT CALL  python manage.py runPyScriptDb.
    """

    def __init__(self, *args, **kwargs):
        self.script_evidence = ScriptEvidence().get_or_create_collection()

    @classmethod
    def run_script(cls, script, part_of: int = None, total_part: int = None) -> None:
        if isinstance(script, BaseHybridCloudScript):
            customers = Customer.objects.all()
            total = customers.count()
            start = 0
            if part_of is not None and total_part is not None:
                start, end = get_the_range(total, part_of, total_part)
                customers = customers[start:end]
            for index, customer in enumerate(customers):
                customer = customer.pk
                logger.info(f"{customer=} rate of progress: {start + index}/{total}")
                script.run_script(customer)
        else:
            script.run_script()
        logger.info("\n****RunScript Finish****")

    def run_scripts(self):
        """ method which will run all the scripts"""
        for script in SCRIPT_LIST:
            script_name = script.__class__.__name__
            if script_name not in self.script_evidence.scripts_name:
                print("Running script: '{}'".format(script_name))
                self.run_script(script)
                if script_name not in NOT_LIMIT_SCRIPT_NAME:
                    self.add_script_in_db(script_name)
            else:
                print("Skipping script: '{}'".format(script_name))

    def add_script_in_db(self, script_name):
        """
        :param script_name: This will add the script name in database after the script was run
        """
        self.script_evidence.scripts_name.append(script_name)
        self.script_evidence.save()
