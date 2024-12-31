"""
Created on December 12, 2019

This file is subject to the terms and conditions defined in the
file 'LICENSE.txt', which is part of this source code package.

@author: David Moss
"""

# Data Request reference used when downloading all data
DATAREQUEST_REFERENCE_ALL = "all"


def request_data(botengine, location_object, reference=DATAREQUEST_REFERENCE_ALL, oldest_timestamp_ms=None, force=False):
    """
    Perform a data request from all devices that will result in an integrated sensor matrix.

    :param botengine: BotEngine environment
    :param location_object: Location object
    :param reference: Default is 'all' when all data is being pulled. If an oldest_timestamp_ms is set then this must be changed to a different reference.
    :param oldest_timestamp_ms: The oldest timestamp in milliseconds to retrieve. If None, it will retrieve data from several months back. If altered from None, then the reference MUST NOT be 'all'.
    :param force: Force the download of data, even if we've just recently requested data.
    """
    content = {
        "reference": reference,
        "oldest_timestamp_ms": oldest_timestamp_ms,
        "force": force
    }

    location_object.distribute_datastream_message(botengine, 'download_data', content=content, internal=True, external=False)


def add_tag(botengine, location_object, tag, timestamp_ms=None):
    """
    Capture machine learning feedback to add context to future model generations
    :param botengine: BotEngine environment
    :param location_object: Location object
    :param tag: Tag to apply
    :param timestamp: Optional timestamp for the tag in milliseconds
    :return:
    """
    ts = botengine.get_timestamp()
    if timestamp_ms is not None:
        ts = timestamp_ms

    content = {
        'type': tag,
        'timestamp': int(ts)
    }

    location_object.distribute_datastream_message(botengine,
                                                  address='capture_ml_feedback',
                                                  content=content,
                                                  internal=True,
                                                  external=False)

def reset_machine_learning(botengine, location_object):
    """
    Reset all machine learning
    """
    location_object.distribute_datastream_message(botengine, "reset_machine_learning", None, internal=True, external=False)


def ism_updated(botengine, location_object, reference, integrated_sensor_matrix, total_motion, total_entry, total_pressure, csv_dictionary=None, csv_strings=None, csv_types=None):
    """
    Integrated sensor matrix (ISM) updated. Distribute to microservices.

    :param botengine: BotEngine environment
    :param location_object: Location object
    :param reference: Data Request reference. 'all' means this is all the data and can be used to recalculate machine learning models.
    :param integrated_sensor_matrix: The integrated sensor matrix
    :param total_motion: Total motion sensors in the ISM
    :param total_entry: Total entry sensors in the ISM
    :param total_pressure: Total pressure pads in the ISM
    :param csv_dictionary: Raw CSV dictionary
    :param csv_strings: Raw CSV strings
    :param csv_types: Raw CSV types
    """
    ism_object = {
        # Integrated sensor matrix
        'integrated_sensor_matrix': integrated_sensor_matrix,

        # Reference passed into the data request
        'reference': reference,

        # If 'recalculate' is true then this can be used to recalculate full machine learning models
        'recalculate': reference == DATAREQUEST_REFERENCE_ALL,

        # Total motion sensors in the ISM
        'total_motion': total_motion,

        # Total entry sensors in the ISM
        'total_entry': total_entry,

        # Total pressure pads in the ISM
        'total_pressure': total_pressure,

        # Raw CSV dictionary
        'csv_dict': csv_dictionary,

        # Raw CSV strings
        'csv_strings': csv_strings,

        # Raw CSV types
        'csv_types': csv_types
    }

    location_object.distribute_datastream_message(botengine, 'ism_updated', ism_object, internal=True, external=False)

def radar_filter_input_updated(botengine, location_object, device_id, reference, radar_target_array, csv_dictionary=None):
    """
    Radar filter targets input updated. Distribute to microservices.

    :param botengine: BotEngine environment
    :param location_object: Location object
    :param device_id: Device Id
    :param reference: Data Request reference. 'all' means this is all the data and can be used to recalculate machine learning models.
    :param radar_target_array: Data array
    :param csv_dictionary: Raw CSV dictionary
    """
    radar_object = {
        # Radar targets data array
        'radar_target_array': radar_target_array,

        # Device Id
        'device_id': device_id,

        # Reference passed into the data request
        'reference': reference,

        # If 'recalculate' is true then this can be used to recalculate full machine learning models
        'recalculate': reference == DATAREQUEST_REFERENCE_ALL,

        # Raw CSV dictionary
        'csv_dict': csv_dictionary
    }

    location_object.distribute_datastream_message(botengine, 'radar_filter_input_updated', radar_object, internal=True, external=False)
    # Backwards compatibility
    location_object.distribute_datastream_message(botengine, 'vayyar_filter_input_updated', radar_object, internal=True, external=False)

def vayyar_filter_input_updated(botengine, location_object, device_id, reference, vayyar_target_array, csv_dictionary=None):
    """Deprecated. Use radar_filter_input_updated instead."""
    radar_filter_input_updated(botengine, location_object, device_id, reference, vayyar_target_array, csv_dictionary)
    