def flatten(l):
  out = []
  for item in l:
    if isinstance(item, (list, tuple)):
      out.extend(flatten(item))
    else:
      out.append(item)
  return out

def calc_matrix(infile):
	matrix = dict()
	with open(infile, "r") as f:
		corpus = []
		for line in f:
			line = line.lower()
			line = re.sub('[\W_]', ' ', line)
			words = [word for word in line.split(" ") if re.match('\S', word)]
			corpus += words

	for idx, word in enumerate(corpus):
		if word not in matrix.keys():
			matrix[word] = dict()
			matrix[word][corpus[idx-1]] = 1
		else:
			if corpus[idx-1] not in matrix[word].keys():
				matrix[word][corpus[idx-1]] = 1
			else:
				matrix[word][corpus[idx-1]] += 1
		
	for k in matrix:
		total = sum(matrix[k].values())
		for j in matrix[k]:
			matrix[k][j] /= float(total)
	return matrix

def gibber(matrix):
	s = random.choice(matrix.keys())
	while True:
		# We want to select the next word based on the probability of it in the matrix
		# soooo...fill an array with the appropriate number of copies and use random.choice on it
		# There is no doubt a better way to approach this problem.
		# (this is a crappy markov chain)
		probs = matrix[s]
		parray = []
		for p in probs:
			parray += [p] * int(probs[p] * 10)

		if not parray:
			parray = [random.choice(matrix.keys())]
		s = random.choice(parray)
		yield s

def sentences(words, minlen=7, maxlen=17, capitalize=True):
	sentence = []
	sentence_len = random.randint(minlen, maxlen)
	for word in words:
		if len(sentence) == 0:
			word = string.capitalize(word)
		sentence.append(word)
		if sentence_len == len(sentence):
			stext = " ".join(sentence)
			if sentence[0] in ['did', 'does', 'were', 'was', 'what', 'how', 'when', 'where', 'if']:
				stext += random.choice(['?', '.'])
			else:
				stext += '.'
			sentence = []
			sentence_len = random.randint(minlen, maxlen)
			yield stext


m = calc_matrix("metadata/train1.txt")
g = gibber(m)
s = sentences(g)