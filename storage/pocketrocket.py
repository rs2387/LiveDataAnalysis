import json
import websocket
import csv


#assets = ["BTCUSDT", "ETHUSDT", "BNBUSDT"]
assets = ["BTCUSDT"]

#interval = input("Enter time interval") 1s
#1s, 1m, 3m, 5m, 15m, 30m, 1h, 2h, 4h, 6h, 8h, 12h, 1d, 3d, 1w, 1M
interval = "1s"

assets = [coin.lower() + f"@kline_{interval}" for coin in assets]

assets = '/'.join(assets)

messages = []

def on_message(ws, message):
    message = json.loads(message)
    message = message["data"]["k"]
    x= ['t','T','i','x','f','L','v','n','q','V','Q','B']
    [message.pop(x[i]) for i in range(len(x))]
    messages.append(message)
    print(message)

def on_open(ws):
    print(" ### Connection Opened ### (Press Control + C to exit) ")

# Press Control C to close the connection while it is running
def on_close(ws, close_status_code, close_msg):
    print(" ### Connection Closed ### ")

socket = "wss://stream.binance.com:9443/stream?streams="+assets

ws = websocket.WebSocketApp(socket, on_message = on_message, on_open= on_open, on_close = on_close)
ws.run_forever()


# file_path = 'realData.csv'

# with open(file_path, 'w', newline='') as csvfile:
#     fieldnames = ['s', 'o', 'c', 'h', 'l']
#     writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
#     writer.writeheader()
#     writer.writerows(messages)

# from tabulate import tabulate
# f = open("realData.csv")
# csv_f = csv.reader(f)
# print(tabulate(csv_f, headers='firstrow'))
