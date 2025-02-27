#cik_lookup_test.py

import get_cik
import unittest

class Test_TestCIKLookup(unittest.TestCase):
    def test_cik(self):
        self.assertEqual(get_cik.get_cik_from_ticker("AAPL"),"0000320193") # Correct ticker & CIK for AAPL
        self.assertEqual(get_cik.get_cik_from_ticker("TSLA"),"0001318605") # Correct ticker & CIK for TSLA

        self.assertEqual(get_cik.get_cik_from_ticker("APPL"),"0000320193") # Incorrect ticker for AAPL

"""""
if __name__ == '__main__':
    unittest.main()
"""