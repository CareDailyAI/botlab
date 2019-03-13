'''
Created on March 1, 2019

This file is subject to the terms and conditions defined in the
file 'LICENSE.txt', which is part of this source code package.

This type of file allows a machine learning developer / data scientist to
test their own machine learning algorithms independently from running inside a microservice.

@author: Andrew Davis
'''

def get_prediction_value(relative_hour_of_day, day_of_week, last_door_closed_object, model):
    """
    This stubbed out function would return a prediction between 0.0 - 1.0 describing
    what the probability is that the location is unoccupied right now, based on the
    current features passed in - include the relative hour of the day, day of the week, and
    the last door that closed. It uses the model, which was previously calculated by
    the generate_predictions() function and stored externally, to produce the probability value.
    :param relative_hour_of_day: Relative hour of the day (0-23)
    :param day_of_week: Day of the week (0-6)
    :param last_door_closed_object: The device object of the last door that closed
    :param model: The specific model we're evaluating against, generated at the current interval in time that has elapsed since the last door closed.
    :return: a prediction between 0.0 - 1.0 that the house is currently unoccupied and all family members are absent.
    """
    # I will leave it as an exercise to the reader to develop your own time-series machine learning algorithms here.
    # In the meantime, here's some random numbers to enjoy.
    import random
    return random.random()

def generate_prediction_models(csv_dict, durations_min):
    """
    For each duration in minutes since a door was last closed, generate a machine learning model
    that describes - based on all the data and history from this location - what the probability is that
    the house is now unoccupied.  "Labels" can be generated automatically from the data by looking for patterns
    such as:  a door closed, there's no motion activity for more than 15 minutes, and later a door opened. That's
    the fingerprint of an unoccupied home.

    Return an list of machine learning models, one for each duration in time to evaluate after a door closed.

    :param csv_dict: History of all data from this location in CSV form, downloaded safely from the server through the 'data_request' package.
    :param durations_min: List of durations in minutes we want to evaluate after a door closes. One model is generated per duration.
    :return: List of machine learning models to be saved externally and injected into get_prediction_value() when we want to evaluate current conditions.
    """
    # I will leave it as an exercise to the read to develop your own time-series machine learning algorithms here.
    return []


