import africastalking
from dotenv import load_dotenv
import os

# Load environment variables from the .env file
load_dotenv()

# Retrieve credentials from environment variables
AT_USERNAME = os.getenv('AT_USERNAME')
AT_API_KEY = os.getenv('AT_API_KEY')

# Initialize Africa's Talking
africastalking.initialize(
    username=AT_USERNAME,
    api_key=AT_API_KEY
)

sms = africastalking.SMS

class SendSMS:
    def __init__(self):
        self.sms = sms

    def sending_order(self, customer_telephone, order_item, order_amount, order_time):
        """
        Send an SMS to the customer with their order details.
        
        Parameters:
        - customer_telephone (str): The customer's telephone number.
        - order_item (str): The item ordered by the customer.
        - order_amount (float): The price of the ordered item.
        - order_time (str): The time when the order was placed.
        """
        # Format the message with order details
        message = (
            f"Dear Customer, your order has been received!\n"
            f"Item: {order_item}\n"
            f"Amount: ${order_amount:.2f}\n"
            f"Time: {order_time}\n"
            f"Thank you for your purchase!"
        )

        # Set the recipient number
        recipients = [customer_telephone]

        # Set your shortCode or senderId (if applicable)
        sender = "KBenedict"

        try:
            # Sending the message
            response = self.sms.send(message, recipients, sender)
            print("Message sent successfully:", response)
        except Exception as e:
            print(f"Failed to send message: {e}")

# Example Usage
if __name__ == "__main__":
    sms_service = SendSMS()
    # Example data for testing
    # customer_telephone = "+254722123123"
    # order_item = "Pizza Margherita"
    # order_amount = 10.99
    # order_time = "2024-11-14 13:45"

    # sms_service.sending_order(customer_telephone, order_item, order_amount, order_time)
