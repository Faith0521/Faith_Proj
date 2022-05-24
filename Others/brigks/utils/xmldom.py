

def indent(elem, level=0):
	'''Pretty print for etree.Element

	Args:
		elem (etree.Element): 
		level (int): level of indentation

	Returns:
		etree.Element
	'''
	i = "\n" + level*" "
	if len(elem):
		if not elem.text or not elem.text.strip():
			elem.text = i + " "
		if not elem.tail or not elem.tail.strip():
			elem.tail = i
		for elem in elem:
			indent(elem, level+1)
		if not elem.tail or not elem.tail.strip():
			elem.tail = i
	else:
		if level and (not elem.tail or not elem.tail.strip()):
			elem.tail = i


