import numpy as np
from matplotlib import pyplot as pp
from Scientific.Functions.LeastSquares import leastSquaresFit
from scipy import optimize

from Chandra import Time
from Ska.engarchive import fetch_eng as fetch
from Ska.Matplotlib import plot_cxctime

from utilities import overlap, str_to_secs
from bad_times import nsm, ssm, outliers

close('all')

# Inputs
t_start = '2000:001'
t_stop = Time.DateTime().date
min_alt = 66400000 #m from center of earth
min_dur = 1200 #sec 

# Fetch data
print('fetching data...')
msids = ['AOSYMOM1', 'AOSYMOM2', 'AOSYMOM3', 
         'AOPCADMD', 'AOACASEQ', 'DIST_SATEARTH', 
         'PITCH', 'ROLL']
x = fetch.Msidset(msids, t_start, t_stop, stat='5min')
x.interpolate(dt=300)

# Identify dwell start and stop times
print('identifying dwell start and stop times...')
npm = (x['AOPCADMD'].vals == 'NPNT') & (x['AOACASEQ'].vals == 'KALM') 
if any(~npm[:2]) | any(~npm[-3:]):
    warn('Timeframe must start and end in Normal Point mode + 10 minute pad.')
i1_npm = ~npm[:-2] & npm[1:-1] & npm[2:] 
i2_npm = npm[:-2] & npm[1:-1] & ~npm[2:]
i1_npm = append(zeros(2, dtype='bool'), i1_npm)  # delay start time by 5 min
i2_npm = append(append(zeros(1, dtype='bool'), i2_npm), zeros(1, dtype='bool'))
i1_npm[nonzero(i1_npm)[0][-1]] = False  # need pairs:  discard last start
i2_npm[nonzero(i2_npm)[0][0]] = False   # need pairs:  discard first stop
if sum(i1_npm) != sum(i2_npm):
    warn('NPM start and stop times do not correlate.')
t1_npm = x['AOPCADMD'].times[i1_npm]
t2_npm = x['AOPCADMD'].times[i2_npm] 
t_npm = array([t1_npm, t2_npm]).transpose() 

# Identify dwells with momentum unloads
print('filtering dumps, nsm/ssm events, short dwells, perigees, and outliers...')
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

# Identify dwells less than 20 minutes (too short for accurate reading)
bad_short = (t_npm[:,1] - t_npm[:,0]) < min_dur

# Identify dwells with low altitude (gravity gradient torques will dominate)
bad_low = ((x['DIST_SATEARTH'].vals[i1_npm] < min_alt) | 
           (x['DIST_SATEARTH'].vals[i2_npm] < min_alt))

# Identify dwells that have previously been flagged as outliers
t_outliers = str_to_secs(outliers)
bad_outliers = overlap(t_npm, t_outliers)

# Filter bad dwells 
bad = bad_dump | bad_nsm | bad_ssm | bad_short | bad_low | bad_outliers
i1 = i1_npm
i2 = i2_npm
i1[nonzero(i1)[0][bad]] = False  #index for good dwell start times
i2[nonzero(i2)[0][bad]] = False  #index for good dwell stop times

# Collect average attitude and torque for each dwell
t1 = x['AOPCADMD'].times[i1]
t2 = x['AOPCADMD'].times[i2]
dur = t2 - t1
pitch_1 = x['PITCH'].vals[i1]
pitch_2 = x['PITCH'].vals[i2]
pitch = array(mean(array([pitch_1, pitch_2]), axis=0), dtype='int')
roll_1 = x['ROLL'].vals[i1]
roll_2 = x['ROLL'].vals[i2]
roll = array(mean(array([roll_1, roll_2]), axis=0), dtype='int')
atts = [(pitch[i], roll[i]) for i in range(len(roll))]
mom_1 = array([x['AOSYMOM1'].vals[i1], 
               x['AOSYMOM2'].vals[i1], 
               x['AOSYMOM3'].vals[i1]]).transpose()
mom_2 = array([x['AOSYMOM1'].vals[i2], 
               x['AOSYMOM2'].vals[i2], 
               x['AOSYMOM3'].vals[i2]]).transpose()
torque = (mom_2 - mom_1) / array([dur, dur, dur]).transpose()

# Compute average torque for each attitude
print('computing average torque for each attitude...')
num_atts = len(unique(atts))
avg_pitch = zeros(num_atts)
avg_roll = zeros(num_atts)
avg_torque = zeros((num_atts, 3))
num_dwells = zeros(num_atts)
for i in range(num_atts):
    att = unique(atts)[i]
    avg_pitch[i] = att[0]
    avg_roll[i] = att[1]
    a = all(att == atts, axis=1)
    num_dwells[i] = sum(a)
    avg_torque[i,:] = dur[a].dot(torque[a,:]) / sum(dur[a])  
avg_atts = [(avg_pitch[i], avg_roll[i]) for i in range(num_atts)]     

# Compute average torque for each attitude
print('fitting data...')
# http://stackoverflow.com/questions/12617985/fitting-a-linear-surface-with-numpy-least-squares
# has the model:   pitch*a + roll*b + c = torque
A = array([avg_pitch, avg_roll, ones(num_atts)]).transpose()
x_params, x_resid, rank, sigma = lstsq(A, avg_torque[:,0])


# or http://www.velocityreviews.com/forums/t329682-surface-fitting-library-for-python.html
x_data = [((avg_pitch[i], avg_roll[i]), avg_torque[i,0]) for i in range(num_atts)]
y_data = [((avg_pitch[i], avg_roll[i]), avg_torque[i,1]) for i in range(num_atts)]
z_data = [((avg_pitch[i], avg_roll[i]), avg_torque[i,2]) for i in range(num_atts)]
x_init_params = [0, 0, 0]
y_init_params = [0, 0, 0]
z_init_params = [0, 0, 0]
def model(params, xy):
    a, b, c = params
    x, y = xy
    return a*x + b*y + c
x_fit_params, x_chisquared = optimize.curve_fit(model, x_init_params, x_data)    
y_fit_params, y_chisquared = optimize.curve_fit(model, y_init_params, y_data) 
z_fit_params, z_chisquared = optimize.curve_fit(model, z_init_params, z_data) 

# Plot torques by time (to identify outliers for filtering)
print('plotting...')
for i in range(3):
    figure(i+1)
    plot_cxctime(t1 + 1/2 * dur, torque[:,i], 'b*')

# Plot torques by time, colored by roll, pitch, and dur (again for outliers)
zipvals = zip((4, 5, 6), 
              (roll_1, pitch_1, dur), 
              ('Roll', 'Pitch', 'Duration'))
for fig, var, var_str in zipvals:
    figure(fig)
    
    subplot(3,1,1)
    title('Color = ' + var_str)
    scatter(t1 + 1/2 * dur, torque[:,0], c=var, lw=0)
    ylim([-0.00006, 0.00008])
    colorbar()
    
    subplot(3, 1, 2)
    scatter(t1 + 1/2 * dur, torque[:,1], c=var, lw=0)
    ylim([-0.0008, 0.0004])
    colorbar()
    
    subplot(3, 1, 3)
    scatter(t1 + 1/2 * dur, torque[:,2], c=var, lw=0)
    ylim([-0.0001, 0.0001])
    colorbar()

# Plot torques by attitude (to see the raw "averaged" data w/o surface fit)
figure(7)
subplot(3, 1, 1)
scatter(avg_pitch, avg_roll, c=avg_torque[:,0], marker='o', cmap=cm.jet, lw=0)
colorbar()
subplot(3, 1, 2)
scatter(avg_pitch, avg_roll, c=avg_torque[:,1], marker='o', cmap=cm.jet, lw=0)
colorbar()
subplot(3 ,1, 3)
scatter(avg_pitch, avg_roll, c=avg_torque[:,2], marker='o', cmap=cm.jet, lw=0)
colorbar()


figure(8)
subplot(3, 1, 1)
scatter(avg_pitch, avg_roll, c=num_dwells, marker='o', cmap=cm.jet, lw=0)
colorbar()
subplot(3, 1, 2)
scatter(avg_pitch, avg_roll, c=num_dwells, marker='o', cmap=cm.jet, lw=0)
colorbar()
subplot(3 ,1, 3)
scatter(avg_pitch, avg_roll, c=num_dwells, marker='o', cmap=cm.jet, lw=0)
colorbar()
