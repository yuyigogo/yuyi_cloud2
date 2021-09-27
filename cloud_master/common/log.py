import logging

from common.framework.middleware.request import global_request


class DefaultServerFormatter(logging.Formatter):
    def __init__(self, *args, **kwargs):
        super(DefaultServerFormatter, self).__init__(*args, **kwargs)

    def format(self, record):
        record.user = getattr(global_request.user, "id", "none")
        message = super(DefaultServerFormatter, self).format(record)
        return message

