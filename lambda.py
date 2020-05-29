"""
AWS Lambda execution environment wrapper

@author:     David Moss

@copyright:  2017 People Power Company. All rights reserved.

@contact:    dmoss@peoplepowerco.com
"""

import botengine
import importlib
import time


def lambda_handler(data, context):
    """
    Execution wrapper on AWS Lambda
    :param data: Inputs to the botengine
    :param context: Ignored
    :return: JSON structure with errors and debug information
    """
    if data is None:
        return 0
    
    logger = LambdaLogger()
    
    try:
        bot = importlib.import_module('bot')
        botengine._run(bot, data, logger, context)
        
    except:
        import traceback
        import sys
        (t, v, tb) = sys.exc_info()
        logger.tracebacks = traceback.format_exception(t, v, tb)

    # Check for asynchronous data request triggers which handle errors differently than synchronous executions of the bot.
    if 'inputs' in data:
        for i in data['inputs']:
            if i['trigger'] == 2048:
                import sys

                if len(logger.logs) > 0:
                    sys.stdout.write("logs: ")
                    for log in logger.logs:
                        sys.stdout.write(log + "; ")

                if len(logger.tracebacks) > 0:
                    sys.stdout.write("tracebacks: ")
                    for tb in logger.tracebacks:
                        sys.stdout.write(tb + "; ")

                sys.stdout.flush()
                break

    if 'sqsQueue' in data:
        import json
        send_sqs_message(data.get('sqsQueue'), json.dumps(logger.get_lambda_return()), data.get('clientContext'))

    return logger.get_lambda_return()


def send_sqs_message(queue_name, msg_body, client_context):
    """
    Method to deliver back to the server the logs and tracebacks during asynchronous parallel processed machine learning data request triggers
    :param queue_name:
    :param msg_body:
    :param client_context:
    :return:
    """
    import boto3
    sqs = boto3.resource('sqs')
    queue = sqs.get_queue_by_name(QueueName=queue_name)
    queue.send_message(MessageBody=msg_body, MessageAttributes={
        'ClientContext': {
            'StringValue': client_context,
            'DataType': 'String'
        }
    })


class LambdaLogger():
    
    def __init__(self):
        # Tracebacks for crashes
        self.tracebacks = []

        # Logs
        self.logs = []

        # Start Code - provided by the server in response to the Start API
        self.start_code = 0

    def log(self, level, message):
        pass

    def debug(self, message):
        pass

    def info(self, message):
        pass

    def warning(self, message):
        self.logs.append("{}: [{}] {}".format(time.time(), "WARNING", message))

    def warn(self, message):
        self.logs.append("{}: [{}] {}".format(time.time(), "WARNING", message))

    def error(self, message):
        self.logs.append("{}: [{}] {}".format(time.time(), "ERROR", message))

    def critical(self, message):
        self.logs.append("{}: [{}] {}".format(time.time(), "CRITICAL", message))

    def exception(self, message):
        self.logs.append("{}: [{}] {}".format(time.time(), "EXCEPTION", message))

    def get_lambda_return(self):
        """
        :return: JSON dictionary of execution details, only if we have info to share
        """
        response = {}
        
        if len(self.tracebacks):
            response['tracebacks'] = self.tracebacks
        
        if len(self.logs):
            response['logs'] = self.logs

        response['startCode'] = self.start_code
        
        return response
    
    