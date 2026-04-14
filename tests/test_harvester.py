import unittest
from unittest.mock import patch, MagicMock
from src.harvester import ChatHarvester

class TestChatHarvester(unittest.TestCase):

    @patch('src.harvester.webdriver.Chrome')
    def test_browser_session(self, mock_chrome):
        mock_driver = MagicMock()
        mock_chrome.return_value = mock_driver

        with ChatHarvester().browser_session() as driver:
            self.assertEqual(driver, mock_driver)
            mock_chrome.assert_called_once()

        mock_driver.quit.assert_called_once()

    @patch('src.harvester.ChatHarvester.extract_messages')
    def test_message_extraction(self, mock_extract):
        mock_extract.return_value = [{'chat_id': '1', 'timestamp': '2023-01-01T00:00:00Z', 'role': 'user', 'text': 'Hello', 'source_url': 'http://example.com'}]
        
        harvester = ChatHarvester()
        messages = harvester.extract_messages('http://example.com/chat')

        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0]['text'], 'Hello')

if __name__ == '__main__':
    unittest.main()