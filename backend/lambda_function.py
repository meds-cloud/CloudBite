import json
import boto3
import uuid
from datetime import datetime, timezone

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('CloudBiteOrders')


def lambda_handler(event, context):

    try:
        body = event.get('body', event)

        if isinstance(body, str):
            body = json.loads(body)

        name = body['name'].strip()
        phone = body['phone'].strip()
        address = body['address'].strip()
        food = body['food'].strip()
        quantity = int(body['quantity'])

        if not all([name, phone, address, food]):
            raise ValueError("All fields are required")

        if quantity < 1 or quantity > 50:
            raise ValueError("Invalid quantity")

        order_id = str(uuid.uuid4())

        order = {
            'orderId': order_id,
            'name': name,
            'phone': phone,
            'address': address,
            'food': food,
            'quantity': quantity,
            'status': 'Placed',
            'orderTime': datetime.now(
                timezone.utc
            ).isoformat()
        }

        table.put_item(Item=order)

        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json'
            },
            'body': json.dumps({
                'message': 'Order placed successfully!',
                'orderId': order_id
            })
        }

    except (KeyError, ValueError, TypeError, AttributeError):
        return {
            'statusCode': 400,
            'body': json.dumps({
                'message': 'Invalid order details'
            })
        }

    except Exception as e:
        print(type(e).__name__)

        return {
            'statusCode': 500,
            'body': json.dumps({
                'message': 'Unable to place order'
            })
        }
