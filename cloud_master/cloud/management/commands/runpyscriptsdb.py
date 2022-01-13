import sys
import traceback

from django.core.management import BaseCommand

from py_scripts_db import RunScripts


# The class must be named Command, and subclass BaseCommand
class Command(BaseCommand):
    # Show this when the user types help
    help = "The following options are:"

    # A command must define handle()
    def handle(self, *args, **options):

        self.stdout.write("ATTENTION!")
        self.stdout.write(
            "Run the command before (re)starting the server or "
            "stop the server before running the command \n"
        )
        self.stdout.write("Running python scripts...")
        try:
            RunScripts().run_scripts()
            self.stdout.write("The scripts were run successfully")
        except Exception:
            traceback.print_exc()
            self.stdout.write(
                "ERROR: some serious error has been produced, please check traceback on top."
            )
            sys.exit(-1)
