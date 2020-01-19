from buttons import Au
import buttons
import socketio
import logging
import sys
from pprint import pprint
import time
import threading

def start_up():

    sio = socketio.Client()
    start_au = Au()
    let_go = True

    @sio.event
    def connect():
        logging.warning("connection established")
        t = threading.Thread(name="au_timer",target=run_counter, daemon=True)
        t.start()

    def run_counter():
        time.sleep(3600)
        sio.disconnect()
        logging.warning("message")
        start_au.get_out()
        let_go = False
        sys.exit()

    @sio.on('message')
    def disconnect(data):
        sio.disconnect()
        logging.warning("message")
        start_au.get_out()
        let_go = False
        sys.exit()

    if let_go:
        sio.connect('ws://0.0.0.0:5000')
        sio.start_background_task(start_au.main())

    sio.wait()

if __name__ == "__main__":
    sys.exit(start_up())