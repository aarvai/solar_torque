import numpy as np
from matplotlib import pyplot as pp

from Chandra import Time
from Ska.engarchive import fetch_eng as fetch
from Ska.Matplotlib import plot_cxctime

from utilities import overlap

# Inputs
t_start = '2000:001'
t_stop = Time.DateTime().date
min_alt = 66400000 #m from center of earth

# Fetch data
msids = ['AOSYMOM1', 'AOSYMOM2', 'AOSYMOM3', 
         'AOPCADMD', 'AOACASEQ', 'DIST_SAT_EARTH', 
         'PITCH', 'ROLL']
x = fetch.Msidset(msids, t_start, t_stop, stat='5min')

# Identify dwell start and stop times
npm = (x['AOPCADMD'].vals == 'NPNT') & (x['AOACASEQ'].vals == 'KALM') 

if any(~npm[:2]) | any(~npm[-3:]):
    warn('Timeframe must start and end in Normal Point mode + 10 minute pad.')

i1_npm = ~npm[:-2] & npm[1:-1] & npm[2:] 
i2_npm = npm[:-2] & npm[1:-1] & ~npm[2:]

if sum(i1_npm) != sum(i2_npm):
    warn('NPM start and stop times do not correlate.')

t1_npm = x['AOPCADMD'].times[nonzero(i1_npm)[0] + 2] # delay start time by 5 min
t2_npm = x['AOPCADMD'].times[nonzero(i2_npm)[0] + 1]
t_npm = array([t1_npm, t2_npm])

# Identify dwells with momentum unloads
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
t_dump = array([t1_dump, t2_dump])
bad_dump = overlap(t_npm, t_dump)

# Identify dwells with sim moves
tscmove = fetch.Msid('3TSCMOVE', t_start, t_stop)
sim = tscmove.vals == 'MOVE'
if any(sim[:1]) | any(sim[-2:]):
    warn('Timeframe must not start or end with a sim translation.')
i1_sim = ~sim[:-1] & sim[1:]
i2_sim = sim[:-1] & ~sim[1:]
if sum(i1_sim) != sum(i2_sim):
    warn('Sim move start and stop times do not correlate.')
t1_sim = tscmove.times[nonzero(i1_sim)[0] + 1]
t2_sim = tscmove.times[nonzero(i2_sim)[0] + 1]
t_sim = array([t1_sim, t2_sim])
bad_sim = overlap(t_npm, t_sim)

# Filter dwells during NSM and SSM events
bad_times = ['2012:150' 

