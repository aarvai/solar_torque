import numpy as np
from matplotlib import pyplot as pp

from Chandra import Time
from Ska.engarchive import fetch_eng as fetch
from Ska.Matplotlib import plot_cxctime

from utilities import overlap, str_to_secs
from bad_times import nsm, ssm

# Inputs
t_start = '2012:001'
t_stop = Time.DateTime().date
min_alt = 66400000 #m from center of earth

# Fetch data
print('fetching data...')
msids = ['AOSYMOM1', 'AOSYMOM2', 'AOSYMOM3', 
         'AOPCADMD', 'AOACASEQ', 'DIST_SATEARTH', 
         'PITCH', 'ROLL']
x = fetch.Msidset(msids, t_start, t_stop, stat='5min')

# Identify dwell start and stop times
npm = (x['AOPCADMD'].vals == 'NPNT') & (x['AOACASEQ'].vals == 'KALM') 
if any(~npm[:2]) | any(~npm[-3:]):
    warn('Timeframe must start and end in Normal Point mode + 10 minute pad.')
i1_npm = ~npm[:-2] & npm[1:-1] & npm[2:] 
i2_npm = npm[:-2] & npm[1:-1] & ~npm[2:]
i1_npm[nonzero(i1_npm)[0][-1]] = False  # need pairs:  discard last start
i2_npm[nonzero(i2_npm)[0][0]] = False   # need pairs:  discard first stop
if sum(i1_npm) != sum(i2_npm):
    warn('NPM start and stop times do not correlate.')
t1_npm = x['AOPCADMD'].times[nonzero(i1_npm)[0] + 2] # delay start time by 5 min
t2_npm = x['AOPCADMD'].times[nonzero(i2_npm)[0] + 1] 
t_npm = array([t1_npm, t2_npm]).transpose() 

# Create index that matches dwell start and stop times
i1 = append(zeros(2, dtype='bool'), i1_npm)
i2 = append(append(zeros(1, dtype='bool'), i2_npm), zeros(1, dtype='bool'))

# Identify dwells with momentum unloads
print('filtering dumps, nsm events, and ssm events...')
aounload = fetch.Msid('AOUNLOAD', t_start, t_stop)
dump = aounload.vals != 'MON '
if any(dump[:1]) | any(dump[-2:]):
    warn('Timeframe must not start or end with a momentum dump.')
i1_dump = ~dump[:-1] & dump[1:]
i2_dump = dump[:-1] & ~dump[1:]
if sum(i1_dump) != sum(i2_dump):
    warn('Dump start and stop times do not correlate.')
t1_dump = aounload.times[nonzero(i1_dump)[0] + 1]
t2_dump = aounload.times[nonzero(i2_dump)[0] + 1]
t_dump = array([t1_dump, t2_dump]).transpose()
bad_dump = overlap(t_npm, t_dump)

# Identify dwells during NSM and SSM events
t_nsm = str_to_secs(nsm)
bad_nsm = overlap(t_npm, t_nsm)
t_ssm = str_to_secs(ssm)
bad_ssm = overlap(t_npm, t_ssm)

# Identify dwells with zero duration
bad_short = (t_npm[:,1] - t_npm[:,0]) == 0

# Filter bad dwells 
bad = bad_dump | bad_nsm | bad_ssm | bad_short 
t_npm_filt = t_npm[~bad, :]  #do I even use this?
dur = t_npm_filt[:,1] - t_npm_filt[:,0]


i1[nonzero(i1)[0][bad]] = False
i2[nonzero(i2)[0][bad]] = False

#i1[nonzero(i1)[0][bad]] = False


# Collect momentum and attitude data

#pitch_1 = x['PITCH'].vals[i1]
#pitch_2 = x['PITCH'].vals[i2]
#roll_1 = x['ROLL'].vals[i1]
#roll_2 = x['ROLL'].vals[i2]
#mom_1 = array([x['AOSYMOM1'].vals[i1], x['AOSYMOM2'].vals[i1], x['AOSYMOM3'].vals[i1]]).transpose()
#mom_2 = array([x['AOSYMOM1'].vals[i2], x['AOSYMOM2'].vals[i2], x['AOSYMOM3'].vals[i2]]).transpose()
#torque = (mom_2 - mom_1) / dur

