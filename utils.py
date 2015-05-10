def intParse(s):
	if s.replace(" ","") == "":
		return 0
	else:
		try:
			return int(s)
		except:
			try:
				return int(float(s))
			except:
				return 0

