import unittest
from unittest.mock import patch, MagicMock
from send_sms import SendSMS  # Assuming this code is saved in send_sms.py
import os

class TestSendSMS(unittest.TestCase):

    @patch('africastalking.SMS.send')
    def test_sending_order_successful(self, mock_send):
        # Arrange
        mock_response = {'status': 'Success', 'data': {'recipient': '+254759505343', 'messageId': '1234567890'}}
        mock_send.return_value = mock_response
        
        # Initialize the SendSMS class
        sms_service = SendSMS()

        # Example order details
        customer_telephone = "+254759505343"
        order_item = "Pizza Margherita"
        order_amount = 10.99
        order_time = "2024-11-14 13:45"

        # Act: Call the sending_order method
        sms_service.sending_order(customer_telephone, order_item, order_amount, order_time)

        # Assert: Ensure send method was called with the correct arguments
        mock_send.assert_called_once_with(
            "Dear Customer, your order has been received!\n"
            f"Item: {order_item}\n"
            f"Amount: ${order_amount:.2f}\n"
            f"Time: {order_time}\n"
            "Thank you for your purchase!",
            [customer_telephone],
            "KBenedict"
        )

        # Assert the response is correct
        self.assertEqual(mock_send.return_value, mock_response)
        print("Test passed: SMS sent successfully")

    @patch('africastalking.SMS.send')
    def test_sending_order_failed(self, mock_send):
        # Arrange
        mock_send.side_effect = Exception("Network error")
        
        # Initialize the SendSMS class
        sms_service = SendSMS()

        # Example order details
        customer_telephone = "+254759505343"
        order_item = "Pizza Margherita"
        order_amount = 10.99
        order_time = "2024-11-14 13:45"

        # Act: Call the sending_order method
        sms_service.sending_order(customer_telephone, order_item, order_amount, order_time)

        # Assert: Check if exception handling works
        mock_send.assert_called_once_with(
            "Dear Customer, your order has been received!\n"
            f"Item: {order_item}\n"
            f"Amount: ${order_amount:.2f}\n"
            f"Time: {order_time}\n"
            "Thank you for your purchase!",
            [customer_telephone],
            "KBenedict"
        )

        print("Test passed: SMS sending failed as expected due to network error")

if __name__ == "__main__":
    unittest.main()
