"""
AWS Lambda execution environment wrapper

@author:     David Moss, Destry Teeter

@copyright:  2023 People Power Company. All rights reserved.

@contact:    dmoss@caredaily.ai, destry@caredaily.ai
"""

import botengine as BotEngine
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
    
    # TODO: Allow multiple loggers to differentiate logs from different microservices
    logger = LambdaLogger()
    
    try:
        bot = importlib.import_module('bot')
        botengine = BotEngine._run(bot, data, logger, context)
        
    except Exception as e:
        import traceback
        import sys
        (t, v, tb) = sys.exc_info()
        logger.tracebacks = traceback.format_exception(t, v, tb)
        logger.exception("Failed to execute bot: {}".format(str(e)))
        return logger.get_lambda_return()

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
        send_sqs_message(data.get('sqsQueue'), json.dumps(logger.get_lambda_return(botengine, bot)), data.get('clientContext'))

    # Commit logs to CloudWatch log group and stream
    if len(logger.log_events) > 0:

        # Default to the log group and stream name provided by Lambda
        log_group_name = context.log_group_name
        log_stream_name = context.log_stream_name
        logger.put_log_events(log_group_name, log_stream_name)

    return logger.get_lambda_return(botengine, bot)


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
    
    def __init__(self, log_level="info"):
        # Tracebacks for crashes
        # DEPRECATED: Captured from AWS Lambda
        self.tracebacks = []

        # Optional error message to return to the server
        self.error_message = None

        # Logs
        # DEPRECATED: Use log_events instead
        self.logs = []

        # Log events to return to the server
        self.log_events = [] # [{"timestamp": time.time() * 1000, "message": "Log Me"}]

        # Start Code - provided by the server in response to the Start API
        self.start_code = 0

        # Log level (info, debug, warn, error)
        self.log_level = log_level

        # Start time
        self.start_time_ms = int(time.time() * 1000)

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
            # Too granular
            # self.logs.append("{}: [{}] {}".format(time.time(), "DEBUG", message))
            self.log_events.append({
                'timestamp': int(time.time() * 1000),
                'message': "[{}] {}".format("DEBUG", message)
            })

    def info(self, message):
        if self.log_level in ["debug", "info"]:
            # Too granular
            # self.logs.append("{}: [{}] {}".format(time.time(), "INFO", message))
            self.log_events.append({
                'timestamp': int(time.time() * 1000),
                'message': "[{}] {}".format("INFO", message)
            })

    def warning(self, message):
        self.warn(message)

    def warn(self, message):
        if self.log_level in ["debug", "info", "warn"]:
            self.logs.append("{}: [{}] {}".format(time.time(), "WARN", message))
            self.error_message = message
            self.log_events.append({
                'timestamp': int(time.time() * 1000),
                'message': "[{}] {}".format("WARN", message)
            })

    def error(self, message):
        self.logs.append("{}: [{}] {}".format(time.time(), "ERROR", message))
        self.error_message = message
        self.log_events.append({
                'timestamp': int(time.time() * 1000),
                'message': "[{}] {}".format("ERROR", message)
            })

    def critical(self, message):
        self.logs.append("{}: [{}] {}".format(time.time(), "CRITICAL", message))
        self.error_message = message
        self.log_events.append({
                'timestamp': int(time.time() * 1000),
                'message': "[{}] {}".format("CRITICAL", message)
            })

    def exception(self, message):
        self.logs.append("{}: [{}] {}".format(time.time(), "EXCEPTION", message))
        self.error_message = message
        self.log_events.append({
                'timestamp': int(time.time() * 1000),
                'message': "[{}] {}".format("EXCEPTION", message)
            })

    def get_lambda_return(self, botengine=None, bot=None):
        """
        :param botengine: BotEngine instance
        :param bot: Bot instance
        :return: JSON dictionary of execution details
        """
        response = {}

        if botengine is None:
            response['startTime'] = self.start_time_ms
            response['endTime'] = int(time.time() * 1000)
            response["logEvents"] = self.log_events
            if self.error_message is not None:
                response['errorMessage'] = self.error_message
            
            if len(self.tracebacks):
                response['tracebacks'] = self.tracebacks
            
            return response

        # Include additional bot server statistics for individual microservices
        if botengine.is_server_version_newer_than(1, 38):
            response['startCode'] = self.start_code
            response["logEvents"] = self.log_events
            if bot is not None:
                response['microservices'] = bot.get_intelligence_statistics(botengine)
            response['startTime'] = self.start_time_ms
            response['endTime'] = int(time.time() * 1000)

            if self.error_message is not None:
                response['errorMessage'] = self.error_message
            
            if len(self.tracebacks):
                response['tracebacks'] = self.tracebacks
            
            return response
        
        if len(self.tracebacks):
            response['tracebacks'] = self.tracebacks

        if len(self.logs):
            import re
            response['logs'] = list(map(lambda x: re.sub(r'\033\[(\d|;)+?m', ' ', x).strip(), self.logs))

        response['startCode'] = self.start_code
        
        return response

    def put_log_events(self, log_group, stream_name):
        """
        Log a message to the server
        :return:
        """
        try:
            import boto3
            client = boto3.client('logs')
            client.put_log_events(logGroupName=log_group, logStreamName=stream_name, logEvents=self.log_events)
        except Exception as e:
            pass