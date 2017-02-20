"""
AWS Lambda execution environment wrapper

@author:     David Moss

@copyright:  2017 People Power Company. All rights reserved.

@contact:    dmoss@peoplepowerco.com
"""

import botengine
import importlib
import logging

def lambda_handler(data, context):
    """
    Execution wrapper on AWS Lambda
    :param data: Inputs to the botengine
    :param context: Ignored
    :return: Exit code
    """
    if data is None:
        return 0
    
    logger = logging.getLogger('bot')
    logger.setLevel(logging.WARN)
    
    bot = importlib.import_module('bot')
    botengine._run(bot, data, logger)
    