from buttons import Au
import buttons
import socketio
import logging
import sys
from pprint import pprint

def start_up():
    sio = socketio.Client()
    start_au = Au()
    the_thread = sio.start_background_task(start_au.main())
    #This line below is the answer.
    start_au.get_out()
    

    @sio.event
    def connect():
        logging.warning("connection established")


    @sio.on('message')
    def disconnect(data):
        logging.warning("message")

        sio.disconnect()

    sio.connect('ws://localhost:5000')
    sio.wait()

if __name__ == "__main__":
    start_up()
    print("made it")
    sys.exit()