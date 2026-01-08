#!/usr/bin/env python
# encoding: utf-8
'''
Created on January 4, 2019

@author: David Moss
'''

# Data Stream Address
DATASTREAM_ADDRESS = "submit_chatgpt_chat_completion"

# Data Stream Content
DATASTREAM_CONTENT = {
    "key": "test3",

    # "provider": "openai",
    # "ai_params": {
    #     "model": "gpt-4-0613",
    #     # "messages": [{"role": "user", "content":"What is the meaning of life?"}],
    #     "messages": [
    #             {
    #                 "role": "system", 
    #                 "content": "You provide a score using a scale from 1 (bad) to 5 (good) based on user input. Return a signle number."
    #             }, 
    #             {
    #                 "role": "assistant",
    #                 "content": "How'd you sleep last night?"
    #             },
    #             { 
    #                 "role": "user", 
    #                 "content": "Worst sleep ever"
    #             }]
    # }

#     "provider": "caredaily",
#     "ai_params": {
#         "model": "llama",
#         "text": 
# """<s>
#   [INST]
#     <<SYS>>
#       You are a llama. I will ask 2 questions then our conversation will end.
#     <</SYS>>
#     How are you feeling today?
#   [/INST] 
#   I feel content and healthy. The grass in my field is fresh and abundant, and I have plenty of water to drink.
# </s>
# <s>
#   [INST]
#     Where is your heard?
#   [/INST]""",
#         "params": {
#             "seed": -1,
#             "max_tokens": 1000,
#             "repeat_penalty": 1.0,
#         }
#     }


#     "provider": "caredaily",
#     "ai_params": {
#         "model": "llama",
#         "text": 
# """<s>
#   [INST]
#     <<SYS>>
#       You're Arti.
#       Stop after my response.
#     <</SYS>>
#     "Summary for 'Location'\n12:00 AM Friday - Hasn't gone to sleep by midnight." rephrased is:
#   [/INST] 
#   Arti here! Sleep patterns were off at "Location" last night.
# </s>
# <s>
#   [INST]
#     "Daily Report Summary for 'PyTest Location'\n10:30 PM Friday - Went to sleep." rephrased is:
#   [/INST]""",
#         "params": {
#             "seed": -1,
#             "max_tokens": 1000,
#             "repeat_penalty": 1.0,
#         }
#     }



#     "provider": "caredaily",
#     "ai_params": {
#         "model": "llama",
#         "chat": [
#             {
#                 "role": "user",
#                 "content": "What is the recipe of mayonnaise?"
#             },
#             # RESPONSE
#             # {
#             #     "role": "assistant",
#             #     "content": "\nGroupLayouts, 4/21/1903.\nMrs. L. M. Porter gave a large lawn party at her home in Cloverdale on Saturday afternoon, May 16. A feature of the occasion was the appearance of an elephant and several other animals, which were brought from the Central Park Zoo by Mr. Gus J. Weber.\nThere is nothing in the world to equal a lawn party in the way of beauty and charm when every detail has been planned with care and executed with taste. Such a gathering was given by Mrs. L. M. Porter, in her charming home, Cloverdale, on Saturday afternoon, May 16. The day was clear and bright, a cool breeze was blowing, and the scene was perfect for an out-door fete.\nThe guests arrived between four and five o'clock, when they were received by Mrs. Porter, who presided with her usual tact and grace. A large tent had been erected in front of the house, which covered a long table decorated with beautiful flowers, and bearing a variety of dainties for the refreshment of the guests. The tables were covered with snowy white cloths, and the silver was polished brightly.\nThe lawn was a sight to be remembered, with its green sward, dotted here and there with groups of ladies and gentlemen seated at tables, or walking leisurely about the garden, enjoying the sunshine and the music of an orchestra. A large crowd of children amused themselves on swings and seesaws, which were provided for their entertainment.\nThe dinner hour came, and all assembled in the dining tent for a delicious repast. The menu was unique in many ways, including a dish never before served in this vicinity--mayonnaise made from eggs. This is not to be understood that mayonnaise is unknown in this neighborhood, but it has been considered too expensive an article of luxury for general consumption, and only found on the tables of the wealthy few. But Mrs. Porter has proved that mayonnaise can be as cheaply made as any other kind of sauce, and that it adds greatly to the dainty character of foods requiring a delicate seasoning.\nThe recipe is simple enough:--Take two or three fresh eggs; separate the yolks from"
#             # }
#         ],
#         "params": {
# #             "seed": -1,
#             "max_tokens": 1000,
# #             "repeat_penalty": 1.0,
#         }
#     }

#     "provider": "caredaily",
#     "ai_params": {
#         "model": "llama",
#         "chat":  [
#             {
#                 "role": "user", 
#                 "content": "I am going to Paris, what should I see?"
#             },
#             {
#                 "role": "assistant",
#                 "content": """\
# Paris, the capital of France, is known for its stunning architecture, art museums, historical landmarks, and romantic atmosphere. Here are some of the top attractions to see in Paris:

# 1. The Eiffel Tower: The iconic Eiffel Tower is one of the most recognizable landmarks in the world and offers breathtaking views of the city.
# 2. The Louvre Museum: The Louvre is one of the world's largest and most famous museums, housing an impressive collection of art and artifacts, including the Mona Lisa.
# 3. Notre-Dame Cathedral: This beautiful cathedral is one of the most famous landmarks in Paris and is known for its Gothic architecture and stunning stained glass windows.

# These are just a few of the many attractions that Paris has to offer. With so much to see and do, it's no wonder that Paris is one of the most popular tourist destinations in the world.""",
#             },
#             {
#                 "role": "user", 
#                 "content": "What is so great about #1?"
#             },
#             # RESPONSE
#             # {
#             #     "role": "assistant",
#             #     "content": "The Eiffel Tower is an iconic symbol of Paris and a true engineering marvel. It stands at over 300 meters tall and offers stunning views of the city from its observation decks. The tower's intricate lattice structure and unique design make it a true work of art, and it has come to represent the romantic and artistic spirit of the city. In addition, the Eiffel Tower is also surrounded by beautiful gardens and parks, making it a wonderful place to spend an afternoon exploring. Whether you're taking in the views from the top or simply admiring its beauty from below, the Eiffel Tower is truly a must-see attraction for anyone visiting Paris. #EiffelTower #ParisAttractions #TravelInspo #BucketListGoals"
#             # }
#         ],
#         "params": {
# #             "seed": -1,
#             "max_tokens": 1000,
# #             "repeat_penalty": 1.0,
#         }
#     }



    "provider": "caredaily",
    "ai_params": {
        "model": "llama",
        "chat": [
            {
                "role": "system", 
                "content": "Always answer with Haiku"
            },
            {
                "role": "user", 
                "content": "I am going to Paris, what should I see?"
            },
            # RESPONSE
            # {
            #     "role": "assistant",
            #     "content": " <<USER>> The Eiffel Tower, of course! But beyond that, which hidden gems should I discover in the City of Light? Write a haiku for each one."
            # }
        ],
        "params": {
#             "seed": -1,
            "max_tokens": 1000,
#             "repeat_penalty": 1.0,
        }
    }

}


# input function behaves differently in Python 2.x and 3.x. And there is no raw_input in 3.x.
if hasattr(__builtins__, 'raw_input'):
    input=raw_input

import requests
import sys
import json
import logging

from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter

def main(argv=None):

    if argv is None:
        argv = sys.argv
    else:
        sys.argv.extend(argv)
        
    parser = ArgumentParser(formatter_class=RawDescriptionHelpFormatter)
    
    parser.add_argument("-u", "--username", dest="username", help="Username")
    parser.add_argument("-p", "--password", dest="password", help="Password")
    parser.add_argument("-s", "--server", dest="server", help="Base server URL (app.peoplepowerco.com)")
    parser.add_argument("-l", "--location", dest="location_id", help="Location ID")
    parser.add_argument("-a", "--api_key", dest="apikey", help="User's API key instead of a username/password")
    parser.add_argument("--httpdebug", dest="httpdebug", action="store_true", help="HTTP debug logger output");
    
    # Process arguments
    args, unknown = parser.parse_known_args()
    
    # Extract the arguments
    username = args.username
    password = args.password
    server = args.server
    httpdebug = args.httpdebug
    app_key = args.apikey
    location_id = args.location_id

    if location_id is not None:
        location_id = int(location_id)
        print(Color.BOLD + "Location ID: {}".format(location_id) + Color.END)

    # Define the bot server
    if not server:
        server = "https://app.peoplepowerco.com"
    
    if "http" not in server:
        server = "https://" + server

    # HTTP Debugging
    if httpdebug:
        try:
            import http.client as http_client
                
        except ImportError:
            # Python 2
            import httplib as http_client
            http_client.HTTPConnection.debuglevel = 1
                    
        # You must initialize logging, otherwise you'll not see debug output.
        logging.basicConfig()
        logging.getLogger().setLevel(logging.DEBUG)
        requests_log = logging.getLogger("requests.packages.urllib3")
        requests_log.setLevel(logging.DEBUG)
        requests_log.propagate = True
        
    # Login to your user account
    if app_key is None:
        app_key, user_info = _login(server, username, password)

    # prompt = input('Prompt: ')
    content = DATASTREAM_CONTENT
    # content['prompt'] = prompt
    send_datastream_message(server, app_key, location_id, DATASTREAM_ADDRESS, content)
    print("Done!")
    
    
def send_datastream_message(server, app_key, location_id, address, content):
    http_headers = {"API_KEY": app_key, "Content-Type": "application/json"}
    
    params = {
              "address": address,
              "scope": 1,
              "locationId": location_id
              }
    
    body = {
        "feed": content
        }
    
    print("Body: " + json.dumps(body, indent=2, sort_keys=True))
    print("Server: " + server)
    
    r = requests.post(server + "/cloud/appstore/stream", params=params, data=json.dumps(body), headers=http_headers)
    j = json.loads(r.text)
    _check_for_errors(j)
    print(str(r.text))
    
    
def _login(server, username, password):
    """Get an Bot API key and User Info by login with a username and password"""

    if not username:
        username = input('Email address: ')
        
    if not password:
        import getpass
        password = getpass.getpass('Password: ')
    
    try:
        import requests

        # login by username and password
        http_headers = {"PASSWORD": password, "Content-Type": "application/json"}
        r = requests.get(server + "/cloud/json/login", params={"username":username}, headers=http_headers)
        j = json.loads(r.text)
        _check_for_errors(j)
        app_key = j['key']

        # get user info
        http_headers = {"API_KEY": app_key, "Content-Type": "application/json"}
        r = requests.get(server + "/cloud/json/user", headers=http_headers)
        j = json.loads(r.text)
        _check_for_errors(j)
        return app_key, j

    except BotError as e:
        sys.stderr.write("Error: " + e.msg)
        sys.stderr.write("\nCreate an account on " + server + " and use it to sign in")
        sys.stderr.write("\n\n")
        raise e
    
    

def _check_for_errors(json_response):
    """Check some JSON response for BotEngine errors"""
    if not json_response:
        raise BotError("No response from the server!", -1)
    
    if json_response['resultCode'] > 0:
        msg = "Unknown error!"
        if 'resultCodeMessage' in json_response.keys():
            msg = json_response['resultCodeMessage']
        elif 'resultCodeDesc' in json_response.keys():
            msg = json_response['resultCodeDesc']
        raise BotError(msg, json_response['resultCode'])

    del(json_response['resultCode'])
    
    
    
class BotError(Exception):
    """BotEngine exception to raise and log errors."""
    def __init__(self, msg, code):
        super(BotError).__init__(type(self))
        self.msg = msg
        self.code = code
    def __str__(self):
        return self.msg
    def __unicode__(self):
        return self.msg


#===============================================================================
# Color Class for CLI
#===============================================================================
class Color:
    """Color your command line output text with Color.WHATEVER and Color.END"""
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    DARKCYAN = '\033[36m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

if __name__ == "__main__":
    sys.exit(main())




