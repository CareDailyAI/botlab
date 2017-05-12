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
    :return: JSON structure with errors and debug information
    """
    if data is None:
        return 0
    
    logger = logging.getLogger('bot')
    logger.setLevel(logging.WARN)
    
    log_output_handler = LambdaHandler()
    logger.addHandler(log_output_handler)
    
    try:
        bot = importlib.import_module('bot')
        botengine._run(bot, data, logger)
        
    except:
        import traceback
        import sys
        (t, v, tb) = sys.exc_info()
        log_output_handler.tracebacks = traceback.format_exception(t, v, tb)
    
    return log_output_handler.get_lambda_return()
    


class LambdaHandler(logging.Handler):
    
    def __init__(self, level=logging.NOTSET):
        logging.Handler.__init__(self, level)
        self.tracebacks = []
        self.logs = []
        
    def emit(self, record):
        self.logs.append("%s: %s: %s" % (record.asctime, record.levelname, record.message))
        
    def get_lambda_return(self):
        """
        :return: JSON dictionary of execution details, only if we have info to share
        """
        response = {}
        
        if len(self.tracebacks):
            response['tracebacks'] = self.tracebacks
        
        if len(self.logs):
            response['logs'] = self.logs
        
        return response