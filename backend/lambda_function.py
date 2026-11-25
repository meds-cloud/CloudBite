import json
import boto3
import uuid
from datetime import datetime, timezone

table = boto3.resource('dynamodb').Table('CloudBiteOrders')
MENU = {'burger': ('Truffle Burger', 249), 'pizza': ('Margherita Pizza', 299), 'pasta': ('Creamy Pasta', 149), 'biryani': ('Royal Biryani', 279), 'brownie': ('Chocolate Brownie', 129), 'coffee': ('Iced Coffee', 119)}

def reply(code, data):
    return {'statusCode': code, 'headers': {'Content-Type': 'application/json'}, 'body': json.dumps(data)}

def lambda_handler(event, context):
    try:
        body = event.get('body', event)
        if isinstance(body, str):
            body = json.loads(body)
        name, phone, address = (body[k].strip() for k in ('name', 'phone', 'address'))
        if not name or len(name)>100 or len(phone)!=10 or not phone.isascii() or not phone.isdigit() or not address or len(address)>500:
            raise ValueError()
        order = {'orderId': str(uuid.uuid4()), 'name': name, 'phone': phone, 'address': address, 'status': 'Placed', 'orderTime': datetime.now(timezone.utc).isoformat()}
        if 'items' in body:
            items = body['items']
            if not isinstance(items, list) or not 1 <= len(items) <= 6:
                raise ValueError()
            lines, seen = [], set()
            for item in items:
                key, qty = item['id'], item['quantity']
                if key in seen or type(qty) is not int or not 1 <= qty <= 50:
                    raise ValueError()
                seen.add(key)
                title, price = MENU[key]
                lines.append({'id': key, 'food': title, 'quantity': qty, 'unitPrice': price})
            if sum(x['quantity'] for x in lines)>50:
                raise ValueError()
            order['items'] = lines
            order['total'] = sum(x['quantity']*x['unitPrice'] for x in lines)
        else:
            food, qty = body['food'].strip(), int(body['quantity'])
            if not food or not 1 <= qty <= 50:
                raise ValueError()
            order.update(food=food, quantity=qty)
        table.put_item(Item=order)
        result = {'message': 'Order placed successfully!', 'orderId': order['orderId']}
        if 'total' in order:
            result['total'] = order['total']
        return reply(200, result)
    except (KeyError, ValueError, TypeError, AttributeError):
        return reply(400, {'message': 'Invalid order details'})
    except Exception as e:
        print(type(e).__name__)
        return reply(500, {'message': 'Unable to place order'})
