import json
import websocket
from datetime import datetime
import time


def live_data(ticker: str, interval: str, run_time=None):

    start_time = time.time()
    asset = ticker.lower() + f"@kline_{interval}" 

    def on_message(ws, message: list):
        message = json.loads(message)
        message = message["data"]["k"]
        open_price = float(message["o"])
        close_price = float(message["c"])
        high_price = float(message["h"])
        low_price = float(message["l"])
        time_stamp = datetime.fromtimestamp(int(message["t"]) / 1000)
        return time_stamp, open_price, close_price, high_price, low_price

    def on_open(ws):
        print(" ### Connection Opened ### ")

    def on_close(ws, close_status_code, close_msg):
        if close_status_code:
            print(close_status_code)
        elif close_msg:
            print(f" ### {close_msg} ### ")
        else:
            print(" ### Connection Closed ### ")

    socket = "wss://stream.binance.com:9443/stream?streams="+asset
    ws = websocket.WebSocket()
    ws.connect(socket)
    on_open(ws)

    while True:
        elapsed_time = time.time() - start_time 
        if (run_time == None ) or run_time > elapsed_time:
            try:
                message = ws.recv() 
                if message:
                    on_message(ws, message)
                    
                else:
                    print("WebSocket is closed, exiting.")
                    break 

            except Exception as e:
                print(f"Error receiving message: {e}")
                break  

        else:
            ws.close() 
            on_close(ws, None, "Exceeded run time")
            break

            
live_data("BTCUSDT", "1s")