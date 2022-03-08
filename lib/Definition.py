class Definition:
    def __init__(self, name, value, uid):
        self.name = name
        self.value = value
        self.uid = uid

    def get_annotated_name(self):
        return "{}.{}".format(self.name, self.uid)

    def get_name(self):
        return self.name

    def get_uid(self):
        return self.uid

    def get_value(self):
        return self.value

    def __str__(self):
        return "Definition[name={}, value={}, id={}]".format(self.name, self.value, self.uid)