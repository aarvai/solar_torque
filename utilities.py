import numpy as np

from Chandra import Time

from bad_times import nsm, ssm

def overlap(table1, table2):
    # This function looks for overlaps between two sets of ranges 
    # (usually times, formatted in seconds). 
    # It will output a boolean array equal in length to table1.
    # Each input table must be formatted with two columns: 
    # range start and range stop.
    # The output will be True if the corresponding range in table1
    # overlaps with any range in table2.  The output will be
    # otherwise False.
    out = np.zeros(np.size(table1, axis=0), dtype='bool')
    for i in range(np.size(table1, axis=0)):
        s1_s2 = table1[i, 0] < table2[:, 0] 
        s1_e2 = table1[i, 0] <= table2[:, 1]
        e1_s2 = table1[i, 1] < table2[:, 0]
        e1_e2 = table1[i, 1] < table2[:, 1]
        # no overlap occurs when all four parameters above either == 0 or 1
        sum_params = np.sum(np.array([s1_s2, s1_e2, e1_s2, e1_e2]), axis=0)
        olap = (sum_params == 1) | (sum_params == 2) | (sum_params == 3)
        out[i] = np.any(olap)
    return out

def str_to_secs(table):
# This function will take a table of time ranges
# formatted as strings (compatible with bad_times)
# and convert it to a nx2 array in DateTime seconds
    out = np.zeros([len(table), 2])
    for i in range(len(table)):
        t1, t2 = table[i].split()
        out[i, 0] = Time.DateTime(t1).secs
        out[i, 1] = Time.DateTime(t2).secs
    return out    
