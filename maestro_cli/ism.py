import datetime
import re
import time

import numpy as np


def create_integrated_sensor_matrix_str(str_batch, types, h_len, ml_note):
    """
    REQUIRED
    This gets called every week. At the end of the process, we end up with a set of random forest objects
    that correspond to the times that we place on the schedule
    :param str_batch: List of .csv strings where each .csv string element is an entire .csv file
    :param types: List of "motion", "entry", or "modes" strings in the same position as the .csv data in str_batch
    :return: numpy object, which is later to be used in gen_home_away_prediction(..)
    """
    behavior_flag = True
    if behavior_flag:
        ser = np.array([[0, 0, 0, 0, 0]])
        wid = 5
    if behavior_flag is False:
        ser = np.array([[0, 0, 0, 0]])
        wid = 4
    for x in range(len(str_batch)):
        # then through this loop we append each new sensor's matrix to the master
        if behavior_flag:
            tmp = extract_sensor_data_behaviors(str_batch[x], types[x], h_len[x])
        if behavior_flag is False:
            tmp = extract_sensor_data_behaviors(str_batch[x], types[x])
        if len(tmp.shape) == 2:
            # ADD EXTRA DIMENSION HERE TOO
            if tmp.shape[1] == wid:
                ser = np.r_[ser, tmp]
            if tmp.shape[1] != wid:
                print('Matrix for ' + types[x] + ' is too narrow')
                print('It has shape ' + str(tmp.shape))
                print('Its first line is:')
                print(tmp[0, :])
        if len(tmp.shape) != 2:
            print('Matrix for ' + types[x] + ' is too small')
            print('It has shape ' + str(tmp.shape))
            print('It looks like:')
            print(tmp)
    print('Overall matrix has dimension ' + str(ser.shape))
    string_a = np.array(ml_note.split(','))
    s_ln = len(string_a)
    s_rw = np.floor_divide(s_ln, 4)
    tot = s_rw * 4
    arr_t = np.reshape(string_a[0:tot], (s_rw, 4))
    print('Notification matrix has dimensions:')
    print(arr_t.shape)
    dum = np.zeros((s_rw - 1, wid)).astype(str)
    dum[:, [0, 2]] = arr_t[1:, [2, 3]]
    dum[:, 1] = 'note'
    dum[:, 2] = 'none'
    print(dum)
    ser = np.r_[ser, dum]
    ser = ser[ser[:, 0] != '0', :]
    print(list(set(ser[:, 2])))
    return ser[ser[:, 0].argsort(), :]


def csv_string_to_array_behaviors(string, col):
    """
    REQUIRED
    Parse a csv string to get timestamp, name, and readings
    :param string: a comma-delimited string of data from a single device
    :param col: a total number of columns
    :return nam: the device name
    :return arr_f: an array of [timestamp, value, behavior]
    """
    # First we split the long string into an array its constituent elements
    nam = 'none'
    if string is None:
        arr_f = np.array([0, 0, 0])
        print('flag - NoneType')
    else:
        string_a = re.split(',|\r\n|\r|\n', string)
        # Then we get the total number of elements
        s_ln = len(string_a)
        # Then we find the integer number of rows we should have
        s_rw = np.floor_divide(s_ln, col)
        tot = s_rw * col
        if s_ln - tot > 1:
            print(str(s_ln - tot) + ' element[s] not captured!')
        arr = np.reshape(string_a[0:tot], (s_rw, col))
        head_n = arr[0, :]
        dum = np.arange(col)
        name_c = dum[head_n == 'description']
        time_c = dum[head_n == 'timestamp_iso']
        behav_c = dum[head_n == 'behavior']
        int_step_1 = np.array([('Status' == x) for x in head_n])
        int_step_2 = np.array([('event' == x) for x in head_n])
        int_step_3 = np.array([('source' == x) for x in head_n])
        int_step_4 = np.array([('doorStatus' == x) for x in head_n])
        int_step_5 = np.array([('motionStatus' == x) for x in head_n])
        int_step_6 = np.array([('pressureStatus' == x) for x in head_n])
        valuec = dum[int_step_1 | int_step_2 | int_step_3 | int_step_4 | int_step_5 | int_step_6]
        if len(behav_c) == 0:
            arr_f = np.squeeze(arr[1:, [time_c, valuec, [0]]])
        if len(behav_c) == 1:
            arr_f = np.squeeze(arr[1:, [time_c, valuec, behav_c]])
        nam_t = arr[1, name_c]
        if len(nam_t) > 0:
            nam = nam_t[0]
        if np.sum(name_c.astype(int)) == 0:
            nam = 'modes'
    return nam, arr_f


def del_sec_basic(arr):
    """
    REQUIRED
    Get an array of intervals between timestamps in ms
    :param arr: an array of timestamps
    :return an array of millisecond intervals
    """
    tmp = np.array([intify_tstmp(x) for x in arr])
    return tmp[1:] - tmp[0:-1]


def extract_sensor_data_behaviors(csv_string, type_s, col):
    """
    REQUIRED
    Transform a csv string from a particular device type into a numpy array with various scrubs in place
    :param csv_string: a comma-delimited string including all records from a single device
    :param type_s: the device type as a string
    :param col: the number of columns in the original csv file
    :return arr: an nx5 array as [timestamp, custom reading, device type, name, behavior]
    """
    if type_s == 'entry':
        str_set = ['open', 'close']
        [flag, col_n, cut] = [0, 7, 1000.0]
        print('Read as Entry')
    elif type_s == 'motion':
        str_set = ['start', 'stop']
        [flag, col_n, cut] = [0, 7, 5000.0]
        print('Read as Motion')
    elif type_s == 'pressure':
        str_set = ['pressure on', 'pressure off']
        [flag, col_n, cut] = [0, 20, 1000.0]
        print('Read as Pressure')
    elif type_s == 'modes':
        str_set = ['none', 'none']
        [flag, col_n, cut] = [1, 5, 0.0]
        print('Read as Modes')
    else:
        str_set = ['none', 'none']
        [flag, col_n, cut] = [1, 6, 0.0]
        print('Read as Other')
    # This grabs the timestamp and value for each row in a single sensor record
    [name_s, raw_arr] = csv_string_to_array_behaviors(csv_string, col)
    c1 = 'entry' in name_s
    c2 = 'Entry' in name_s
    c3 = 'door' in name_s
    c4 = 'Door' in name_s
    if (type_s == 'motion') and (c1 or c2 or c3 or c4):
        type_s = 'entry'
        str_set = ['close', 'open']
    print(name_s)
    if raw_arr.shape[0] < 5:
        flag = 2
        print('Array is too small')
    if flag == 0:
        # First we grab the name of the sensor
        # then we switch boolean strings to binary ints
        val = np.array(raw_arr[:, 1] == 'True').astype(int)
        if np.sum(val) == 0:
            val = np.array(raw_arr[:, 1] == '1').astype(int)
        # this allows a finite differencing to track changes
        diff = val[1:] - val[0:-1]
        ind_d = (diff != 0)
        # then we develop a subset and replaces with descriptive values
        t_tmp = raw_arr[np.r_[[False], ind_d], 0]
        b_tmp = raw_arr[np.r_[[False], ind_d], 2]
        r_tmp = np.zeros(t_tmp.shape).astype(str)
        r_tmp[diff[ind_d] == 1] = str_set[0]
        r_tmp[diff[ind_d] == -1] = str_set[1]
        # we develop an index of intervals that are longer than our cutoff...
        ind_t = del_sec_basic(t_tmp) > cut
        # but BOTH intervals before AND after must be valid, so our master index
        # looks like this:
        ind_f = np.squeeze(np.r_[True, ind_t]*np.r_[ind_t, True])
        int_step = np.c_[t_tmp[ind_f], r_tmp[ind_f]]
        name_str = np.repeat(name_s, int_step.shape[0])
        # Here we take the sensor type so we can identify it later
        type_str = np.repeat(type_s, int_step.shape[0])
        arr = np.c_[int_step, np.c_[name_str, type_str], b_tmp[ind_f]]
        print('Adding Sensor - first two lines:')
        print(arr[0:2, :])
    elif flag == 1:
        int_step = raw_arr
        name_str = np.repeat(name_s, int_step.shape[0])
        # Here we take the sensor type so we can identify it later
        type_str = np.repeat(type_s, int_step.shape[0])
        arr = np.c_[int_step, np.c_[name_str, type_str]]
        print('Adding Modes - first line')
        arr[:, 2] = 'none'
        print(arr[0, :])
    elif flag == 2:
        arr = np.array([['0', '0', '0', '0', '0']])
        print('Adding Nothing')
    return arr


def intify_tstmp(tstmp):
    """
    REQUIRED
    Convert a set of timestamps to millisecond ints for efficient interval calculation
    :param tstmp: an array of timestamps
    :return an array of millisecond totals
    """
    tmp = datetime.datetime.strptime(tstmp[0:19], '%Y-%m-%dT%H:%M:%S')
    val = 0
    if len(tstmp) > 20:
        val = int(tstmp[20:23])
    return int(time.mktime(tmp.timetuple()) * 1000) + val


