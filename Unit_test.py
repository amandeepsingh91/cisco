import unittest
from urlservice import NewUrl

class NewUrl(unittest.TestCase):

    def setUp(self):
        self.service = testUrls()

    def test_malware(self):
        self.service.get('')

    def test_pass(self):
        self.service.get('microsoft.com:445/')

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()
