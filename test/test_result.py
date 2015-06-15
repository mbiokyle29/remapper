#!/usr/bin/env python
"""
test_result.py
Kyle McChesney
 Testing for classes/etc

"""
from one_codex_result import OneCodexResult
from remapper import read_results, split_results, search
import unittest
import os

class TestOneCodexResult(unittest.TestCase):
    fake_header ="@SALLY:444:C6LP0ACXX:4:1101:7512:3739 1:N:0:ACAGTG"
    fake_id = 1
    fake_hits = 2
    fake_chain = "1:0|2:1|3:2|4:4|5:5"
    fake_length = 10
    fake_file = "/home/kyle/Dev/remapper/test/example.tsv"
    fake_file_results = 75
    fake_threads_divise = 5
    fake_threads_uneven = 6
    fake_ids = [0,11856,99999999999,9606]
    fake_is_or = True
    fake_search_file = "/home/kyle/Dev/remapper/test/search_test.tsv"
    fake_search_ids = [99999999999,88888888888]

    def test_expanding_chain(self):
        result = OneCodexResult(self.fake_header, self.fake_id, 
            self.fake_hits, self.fake_length, self.fake_chain)
        self.assertEqual(result.kmer_chain,[1,2,3,3,4,5,5,5,5,5])

    def test_parseing_tsv(self):
        array = read_results(self.fake_file, self.fake_ids, self.fake_is_or)
        self.assertEqual(len(array), self.fake_file_results)
        self.assertTrue(isinstance(array[0], OneCodexResult))

    def test_split_array_divisor(self):
        array = read_results(self.fake_file, self.fake_ids, self.fake_is_or)

        # we have 75 results so first try with 5 chunks
        five_chunks = split_results(array, self.fake_threads_divise)
        self.assertEqual(len(five_chunks), self.fake_threads_divise)
        print five_chunks
        # each piece should be of length 75 / 5 or 15
        for chunk in five_chunks:
            self.assertEqual(len(chunk),15) 

    def test_split_array_mod(self):
        array = read_results(self.fake_file, self.fake_ids, self.fake_is_or)
        
        six_chunks = split_results(array, self.fake_threads_uneven)
        
        self.assertEqual(len(six_chunks), self.fake_threads_uneven)

        # 75 / 6 = 12.5
        # 75 % 6 = 3
        # 75 - 3 = 72
        # 72 / 6 = 12
        # also the 3 sized array will be at the end 
        equal_size = 12
        front_loaded_size = 13

        # we front loaded the extra three 
        # so 0,1,2 will have length 13, rest will be 12
        for i in range(0, len(six_chunks)):
            if i in [0,1,2]:
                self.assertEqual(len(six_chunks[i]), front_loaded_size)
            else:
                self.assertEqual(len(six_chunks[i]), equal_size)
    
    def test_search(self):
        array_with_one_match = read_results(self.fake_search_file, self.fake_search_ids, self.fake_is_or)
        matching = search(array_with_one_match, [99999999999], self.fake_is_or, 1)
        self.assertEqual(len(matching), 1)

        array_with_no_match = read_results(self.fake_search_file, self.fake_search_ids, False)
        none = search(array_with_no_match, [99999999999], self.fake_is_or, 1)
        self.assertEqual(len(none), 0)

if __name__ == '__main__':
    unittest.main()