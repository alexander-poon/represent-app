from nltk.corpus import stopwords

stop = stopwords.words('english')


def tokenize(string):
	"""
	Split a string into a set of word tokens. Returns a set of distinct, lowercase
	tokens, with stopwords removed.

	:param string: A string with multiple word tokens.
	:return: A set of distinct word tokens in the string.
	"""
	tokens = set([w for w in string.lower().split() if w.isalpha() and w not in stop])

	return tokens


def jaccard(set1, set2):
	"""
	Returns the Jaccard similarity between two sets, defined as the
	cardinality of the intersection of the sets divided by the cardinality
	of the union of the sets.

	:param set1: A set of word tokens.
	:param set2: A set of word tokens.
	:return: A similarity measure in [0, 1], where a higher value represents
	greater similarity.
	"""
	similarity = len(set1.intersection(set2))/len(set1.union(set2))

	return similarity
