import mock
import unittest
import datetime

from mock import patch, Mock
from message_new import dispatch_notice_message_new


class TestMessageNew(unittest.TestCase):

    def setUp(self):
        # initialize sender mock
        self.sender = mock.Mock()
        self.sender.hid = "sender_hid"
        self.sender.first_name = "Andrew"
        self.sender.gid_is = 1

        # initialize recipient mock
        self.recipient = mock.Mock()
        self.recipient.hid = "recipient_hid"
        self.recipient.first_name = "Jane"
        self.recipient.gid_is = 2

        # initialize message mock
        self.message = mock.Mock()
        self.message.id = "message_id"
        self.message.body = "this is a test message"
        self.message.sent_time = datetime.datetime.now()

        # initialize conversation mock
        self.conversation = mock.Mock()
        self.conversation.id = "conversation_id"
        self.conversation.last_message_sender = self.sender
        self.conversation.last_update = datetime.datetime.now()
        self.conversation.subject = "new conversation subject"
        self.conversation.bid_status = 1

        # initialize environ mocks
        self.env = patch.dict('os.environ', {
            'ONESIGNAL_APPID': 'test_onesignal_apid',
            'ONESIGNAL_API_ENDPOINT': 'test_onesignal_api_endpoint',
            'ONESIGNAL_AUTHORIZATION_HEADER': 'test_onesignal_authorization_header',
            'CACERT_PATH': 'test_cacert_path'})

    def test_dispatch_notice_message_new(self):
        # use patch as context manager
        with patch('requests.post') as mocked_post, self.env:
            # call function with mock objects
            dispatch_notice_message_new(self.sender, self.recipient, self.conversation, self.message)

            # test 1: requests.post was called
            mocked_post.assert_called_once()

            # access data json passed into requests.post
            list = mocked_post.call_args_list[0]
            mocked_post_dict = list[1]
            message_data = mocked_post_dict['json']

            # test 2: requests.post was called with expected sender values
            self.assertEqual(message_data["headings"]["en"], self.sender.first_name)
            self.assertEqual(message_data["data"]["message"]["sender_gender"], self.sender.gid_is)
            self.assertEqual(message_data["data"]["message"]["sender_hid"], self.sender.hid)
            self.assertEqual(message_data["data"]["message"]["sender_name"], self.sender.first_name)

            # test 3: requests.post was called with expected recipient values
            self.assertEqual(message_data["include_external_user_ids"], [self.recipient.hid])
            self.assertEqual(message_data["data"]["target_hid"], self.recipient.hid)
            self.assertEqual(message_data["data"]["conversation"]["partner_gender"], self.recipient.gid_is)
            self.assertEqual(message_data["data"]["conversation"]["partner_hid"], self.recipient.hid)
            self.assertEqual(message_data["data"]["conversation"]["partner_name"], self.recipient.first_name)
            self.assertEqual(message_data["data"]["message"]["recipient_hid"], self.recipient.hid)

            # test 4: requests.post was called with expected message values
            self.assertEqual(message_data["contents"]["en"], self.message.body)
            self.assertEqual(message_data["data"]["message"]["body"], self.message.body)
            self.assertEqual(message_data["data"]["message"]["id"], self.message.id)
            self.assertEqual(message_data["data"]["message"]["sent_time"], self.message.sent_time.isoformat())

            # test 5: requests.post was called with expected conversation values
            self.assertEqual(message_data["data"]["conversation"]["id"], self.conversation.id)
            self.assertEqual(message_data["data"]["conversation"]["last_message_sender_hid"], self.conversation.last_message_sender.hid)
            self.assertEqual(message_data["data"]["conversation"]["last_update"], self.conversation.last_update.isoformat())
            self.assertEqual(message_data["data"]["conversation"]["subject"], self.conversation.subject)
            self.assertEqual(message_data["data"]["conversation"]["bid_status"], self.conversation.bid_status)


if __name__ == '__main__':
    unittest.main()
