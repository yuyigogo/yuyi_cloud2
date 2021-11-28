from cloud.settings import MONGO_CLIENT


class ModifyTEVData:
    @classmethod
    def run_script(cls):
        tev = {"amp": 0.84375, "acqtime": "modified data"}
        MONGO_CLIENT["tev"].update_many(
            {"params.TEV": {"$exists": False}}, {"$set": {"params.TEV": tev}}
        )
