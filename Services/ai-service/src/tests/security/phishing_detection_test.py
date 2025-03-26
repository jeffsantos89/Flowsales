import unittest
from phishing_detection import PhishingDetector

class TestPhishingDetection(unittest.TestCase):

    def setUp(self):
        self.detector = PhishingDetector()

    def test_detect_phishing_url(self):
        phishing_urls = [
            "http://phishing.com",
            "http://malicious-site.com",
            "http://fakebank.com/login"
        ]
        for url in phishing_urls:
            with self.subTest(url=url):
                self.assertTrue(self.detector.is_phishing(url))

    def test_detect_non_phishing_url(self):
        non_phishing_urls = [
            "http://example.com",
            "http://github.com",
            "http://google.com"
        ]
        for url in non_phishing_urls:
            with self.subTest(url=url):
                self.assertFalse(self.detector.is_phishing(url))

    def test_empty_url(self):
        self.assertFalse(self.detector.is_phishing(""))

    def test_invalid_url(self):
        invalid_urls = [
            "htp://invalid-url",
            "www.missing-scheme.com",
            "ftp://unsupported-protocol.com"
        ]
        for url in invalid_urls:
            with self.subTest(url=url):
                self.assertFalse(self.detector.is_phishing(url))

    def test_edge_cases(self):
        edge_case_urls = [
            "http://example.com?query=phishing",
            "http://example.com#fragment",
            "http://example.com/path/to/resource"
        ]
        for url in edge_case_urls:
            with self.subTest(url=url):
                self.assertFalse(self.detector.is_phishing(url))

if __name__ == '__main__':
    unittest.main()