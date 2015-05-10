class ImportException(Exception):
	def __init__(self, msg):
		self.msg = msg

	def __str__(self):
		return self.msg

class ImportWarning(ImportException):
	def __init__(self, msg):
		ImportException.__init__(self, msg)

class ImportError(ImportException):
	def __init__(self, msg):
		ImportException.__init__(self, msg)
