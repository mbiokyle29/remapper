#!/usr/bin/env python
"""
test_result.py
Kyle McChesney
 Testing for classes/etc

"""
from one_codex_result import OneCodexResult
from remapper import read_results
import unittest
import os

class TestOneCodexResult(unittest.TestCase):
	fake_header ="@SALLY:444:C6LP0ACXX:4:1101:7512:3739 1:N:0:ACAGTG"
	fake_id = 1
	fake_hits = 2
	fake_chain = "1:0|2:1|3:2|4:4|5:5"
	fake_length = 10
	fake_file = "/home/kyle/Dev/remapper/test/example.tsv"
	fake_file_results = 74

	def test_expanding_chain(self):
		result = OneCodexResult(self.fake_header, self.fake_id, 
			self.fake_hits, self.fake_length, self.fake_chain)
		self.assertEqual(result.kmer_chain,[1,2,3,3,4,5,5,5,5,5])

	def test_parseing_tsv(self):
		array = read_results(self.fake_file)
		self.assertEqual(len(array), self.fake_file_results)
		self.assertTrue(isinstance(array[0], OneCodexResult))

if __name__ == '__main__':
    unittest.main()