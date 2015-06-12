class OneCodexResult:

	def __init__(self,header,tax,hits,read_length,raw_kmer_chain):
		self.header = header
		self.tax = tax
		self.hits = hits
		self.read_length = read_length

		# make str into array of tuples
		self.kmer_chain = self.expand_kmer_chain(raw_kmer_chain)

	def expand_kmer_chain(self,raw_kmer_chain):

		# preset stuff
		full_chain = []		
		chunks = raw_kmer_chain.split("|")
		curr_id = None
		curr_size = None

		# each chunk is id|size*
		# size is relative to the next chunk size
		for chunk in chunks:
			next_id, next_size = chunk.split(":")
			
			next_id = int(next_id)
			next_size = int(next_size)

			# extend the current frag into the array
			if curr_id is not None and curr_size is not None:
				full_chain.extend([curr_id] * (next_size - curr_size))

			# update pointers
			curr_id = next_id
			curr_size = next_size
		
		# the last tax id fills to the end of the read
		left_over = self.read_length - len(full_chain)
		full_chain.extend([curr_id] * left_over)
		return full_chain