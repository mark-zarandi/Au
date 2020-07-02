import asyncio
import websockets
import subprocess
import json
import logging
from logging import handlers
import requests
import feedparser
from soco import SoCo
level    = logging.INFO
format   = '%(asctime)-8s %(levelname)-8s %(message)s'
handlers = [logging.handlers.TimedRotatingFileHandler('/usr/local/bin/logs/socket-server',when="D",interval=1,backupCount=5,encoding=None,delay=False,utc=False,atTime=None), logging.StreamHandler()]

logging.basicConfig(level = level, format = format, handlers = handlers)

def play_brown_noise():
    subprocess.Popen('python /usr/local/bin/brown_noise.py',shell=True)
    logging.info('Playing Brown Noise. Night night.')
    r = requests.post(url = 'http://localhost:5000/api/device/left_master', params ={'state':'off'})
    r = requests.post(url = 'http://localhost:5000/api/device/right_master', params ={'state':'off'})
    
def lights_on(light_list):
    #lights_list must be array
    for light in light_list:
        r = requests.post(url = 'http://localhost:5000/api/device/' + light, params ={'state':'on'})
    logging.info(str(light_list) +': lights on')

def play_recent(pod_address):
    url = 'http://localhost:5005/preset/all_rooms'
    r = requests.get(url)
    
    with open('/usr/local/bin/sonos-rooms.json','r') as f:
        d = json.load(f)
        play_room = (d['Master'])
    
    d = feedparser.parse(pod_address)
    most_recent = d.entries[0].enclosures[0].href
    sonos = SoCo(play_room)
    sonos.play_uri(most_recent)
    #  *suppress SoCo logging note* 
    
async def test():
    logging.info('Starting up!')
    async with websockets.connect('ws://localhost:443') as websocket:
         while True:
            await websocket.send("hello")
 
            response = await websocket.recv()
            response = json.loads(response)
            logging.info(response)
            device_id = (response['id'])
            if 'config' in response:
                logging.warning('battery notification: id ' +  device_id + " @ " + str(response['config']['battery']))
            else:
                if 'buttonevent' in response['state']:
                    logging.info('Received response from ' + str(device_id))
                    click_type = response['state']['buttonevent']
                
            #func = button_dict.get(device_id)
            
                    device_id = int(device_id)
                    try:
                        button_dict[device_id][click_type]["task"](button_dict[device_id][click_type]['arg1'])
                    except KeyError:
                        logging.critical(device_id + " hasn't been setup.")
                    except TypeError:
                        button_dict[device_id][click_type]["task"]()
if __name__ == '__main__':
    #1002 is one click, 1004 is 2 clicks.
    feed_dict = {'BBC':{'RSS_feed':'https://podcasts.files.bbci.co.uk/p02nq0gn.rss'},"NPR":{'RSS_feed':'https://www.npr.org/rss/podcast.php?id=500005'}}
    button_dict = { 2:{1002:{"task":play_brown_noise,"arg1":None},
                       1004:{"task":lights_on,'arg1':['left_master','right_master']}},
                    3:{1002:{"task":play_recent,"arg1":feed_dict['BBC']['RSS_feed']},
                       1004:{"task":play_recent,'arg1':feed_dict['NPR']['RSS_feed']}}}
    
    asyncio.get_event_loop().run_until_complete(test())
