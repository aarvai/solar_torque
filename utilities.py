def overlap(table1, table2):
    # This function looks for overlaps between two sets of ranges 
    # (usually times, formatted in seconds). 
    # It will output an array equal in length to table1.
    # Each input table must be formatted with two columns: 
    # range start and range stop.
    # The output will be 1 if the corresponding range in table1
    # overlaps with any range in table2.  The output will be
    # otherwise zero.
    out = zeros(size(table1, axis=0))
    for i in range(size(table1, axis=0)):
        s1_s2 = table1[i, 0] < table2[:, 0] 
        s1_e2 = table1[i, 0] <= table2[:, 1]
        e1_s2 = table1[i, 1] < table2[:, 0]
        e1_e2 = table1[i, 1] < table2[:, 1]
        # no overlap occurs when all four parameters above either == 0 or 1
        sum_params = sum(array([s1_s2, s1_e2, e1_s2, e1_e2]), axis=0)
        olap = (sum_params == 1) | (sum_params == 2) | (sum_params == 3)
        out[i] = any(olap)
    return out


