class RequiredParamNull(Exception):
    def __init__(self):
        self.msg = "Error. Required param is null"

    def __str__(self):
        return self.msg


class ApiError(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg
