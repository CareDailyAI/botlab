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
        send_sqs_message(data.get('sqsQueue'), json.dumps(logger.get_lambda_return(data)), data.get('clientContext'))

    return logger.get_lambda_return(data)


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
    
    def __init__(self, log_level="warn"):
        # Tracebacks for crashes
        self.tracebacks = []

        # Logs
        self.logs = []

        # Start Code - provided by the server in response to the Start API
        self.start_code = 0

        # Log level (info, debug, warn, error)
        self.log_level = log_level

    def log(self, level, message):
        if level == "debug":
            self.debug(message)

        if level == "info":
            self.info(message)

        if level == "warn":
            self.warn(message)
        
        if level == "error":
            self.error(message)

    def debug(self, message):
        if self.log_level in ["debug"]:
            print("DEBUG {}".format(message))
            self.logs.append("{}: [{}] {}".format(time.time(), "DEBUG", message))

    def info(self, message):
        if self.log_level in ["debug", "info"]:
            print("INFO {}".format(message))
            self.logs.append("{}: [{}] {}".format(time.time(), "INFO", message))

    def warning(self, message):
        self.warn(message)

    def warn(self, message):
        if self.log_level in ["debug", "info", "warn"]:
            print("WARN {}".format(message))
            self.logs.append("{}: [{}] {}".format(time.time(), "WARN", message))

    def error(self, message):
        print("ERROR {}".format(message))
        self.logs.append("{}: [{}] {}".format(time.time(), "ERROR", message))

    def critical(self, message):
        print("CRITICAL {}".format(message))
        self.logs.append("{}: [{}] {}".format(time.time(), "CRITICAL", message))

    def exception(self, message):
        print("EXCEPTION {}".format(message))
        self.logs.append("{}: [{}] {}".format(time.time(), "EXCEPTION", message))

    def get_lambda_return(self, data):
        """
        :param data: Raw JSON data input to the botengine
        :return: JSON dictionary of execution details, only if we have info to share
        """
        response = {}
        
        if len(self.tracebacks):
            response['tracebacks'] = self.tracebacks

        if len(self.logs) > 0:
            self.logs.append("'{}'".format(self._form_admin_url(data)))

        if len(self.logs):
            import re
            response['logs'] = list(map(lambda x: re.sub(r'\033\[(\d|;)+?m', ' ', x).strip(), self.logs))

        response['startCode'] = self.start_code
        
        return response

    def _form_admin_url(self, data):
        """
        Form a URL that an administrator can click on
        :param data: Raw JSON data input to the botengine
        :return: Formatted URL
        """
        if 'apiHost' not in data:
            return "<No apiHost>"

        if 'inputs' not in data:
            return "<No inputs>"

        base_url = "https://maestro.peoplepowerco.com"

        # Add specific command center URLs here
        try:
            # This bundle.py is generated automatically by the botengine CLI when we create or upload a bot.
            # It includes a variable called CLOUD_ADDRESS that describes what cloud we uploaded the bot to.
            import bundle
            if 'sbox' in bundle.CLOUD_ADDRESS:
                base_url = "https://cc.presencepro.com"

            location_id = "NoLocationId"
            for i in data['inputs']:
                if 'locationId' in i:
                    location_id = i['locationId']

            return "{}/#!/main/locations/edit/{}".format(base_url, location_id)

        except:
            return "<Error importing auto-generated bundle.py>"
