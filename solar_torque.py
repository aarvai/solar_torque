import numpy as np
from matplotlib import pyplot as pp
from scipy import optimize
from mpl_toolkits.mplot3d import Axes3D

from Chandra import Time
from Ska.engarchive import fetch_eng as fetch
from Ska.Matplotlib import plot_cxctime

from utilities import overlap, str_to_secs, read_torque_table, write_torque_table
from bad_times import nsm, ssm, outliers

close('all')

# Inputs
t_start = '2010:001'
t_stop = '2013:001'
min_alt = 66400000 #m from center of earth
min_dur = 6000 #sec (Shorter dwells yielded inaccurate readings although most outliers below 2500 sec)

# Fetch data
print('fetching data...')
msids = ['AOSYMOM1', 'AOSYMOM2', 'AOSYMOM3', 
         'AOPCADMD', 'AOACASEQ', 'DIST_SATEARTH', 
         'PITCH', 'ROLL']
x = fetch.Msidset(msids, t_start, t_stop, stat='5min')
#start interp 1 day later to ensure even intervals
interp_start = Time.DateTime(Time.DateTime(t_start).secs + 86400).date 
x.interpolate(dt=300.0, start=interp_start)

# Identify dwell start and stop times
print('identifying dwell start and stop times...')
npm = (x['AOPCADMD'].vals == 'NPNT') & (x['AOACASEQ'].vals == 'KALM') 
if any(~npm[:2]) | any(~npm[-3:]):
    raise StandardError('Timeframe must start and end in Normal Point mode + 15 minute pad.')
i1_npm = ~npm[:-3] & npm[1:-2] & npm[2:-1] & npm[3:]  # transition must be followed by 10 min NPM
i2_npm = npm[:-3] & npm[1:-2] & npm[2:-1] & ~npm[3:]  # transition must be preceded by 10 min NPM
i1_npm = append(append(zeros(2, dtype='bool'), i1_npm), zeros(1, dtype='bool')) # delay start time by 5 min
i2_npm = append(append(zeros(2, dtype='bool'), i2_npm), zeros(1, dtype='bool')) 
i1_npm[nonzero(i1_npm)[0][-1]] = False  # need pairs:  discard last start
i2_npm[nonzero(i2_npm)[0][0]] = False   # need pairs:  discard first stop
if sum(i1_npm) != sum(i2_npm):
    raise StandardError('NPM start and stop times do not correlate.')
t1_npm = x['AOPCADMD'].times[i1_npm]
t2_npm = x['AOPCADMD'].times[i2_npm] 
t_npm = array([t1_npm, t2_npm]).transpose() 

# Identify dwells with momentum unloads
print('filtering dumps, nsm/ssm events, short dwells, perigees, and outliers...')
aounload = fetch.Msid('AOUNLOAD', t_start, t_stop)
dump = aounload.vals != 'MON '
if any(dump[:1]) | any(dump[-2:]):
    raise StandardError('Timeframe must not start or end with a momentum dump.')
i1_dump = ~dump[:-1] & dump[1:]
i2_dump = dump[:-1] & ~dump[1:]
if sum(i1_dump) != sum(i2_dump):
    raise StandardError('Dump start and stop times do not correlate.')
t1_dump = aounload.times[nonzero(i1_dump)[0] + 1]
t2_dump = aounload.times[nonzero(i2_dump)[0] + 1]
t_dump = array([t1_dump, t2_dump]).transpose()
bad_dump = overlap(t_npm, t_dump)

# Identify dwells during NSM and SSM events
t_nsm = str_to_secs(nsm)
bad_nsm = overlap(t_npm, t_nsm)
t_ssm = str_to_secs(ssm)
bad_ssm = overlap(t_npm, t_ssm)

# Identify dwells that are too short for accurate reading
bad_short = (t_npm[:,1] - t_npm[:,0]) < min_dur

# Identify dwells with low altitude (gravity gradient torques will dominate)
i1_npm_ind = nonzero(i1_npm)[0]
i2_npm_ind = nonzero(i2_npm)[0]
min_dwell_alt = array([min(x['DIST_SATEARTH'].vals[i1_npm_ind[i]:i2_npm_ind[i]]) for i in range(len(i1_npm_ind))])
bad_low = min_dwell_alt < min_alt

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

# For attitudes with more than one torque, compute an average
print('averaging torques for attitudes with more than one dwell...')
num_atts = len(unique(atts))
avg_pitch = zeros(num_atts)
avg_roll = zeros(num_atts)
avg_torque = zeros((num_atts, 3))
num_dwells = zeros(num_atts)
total_dur = zeros(num_atts)
for i in range(num_atts):
    att = unique(atts)[i]
    avg_pitch[i] = att[0]
    avg_roll[i] = att[1]
    a = all(att == atts, axis=1)
    num_dwells[i] = sum(a)
    total_dur[i] = sum(dur[a])
    avg_torque[i,:] = dur[a].dot(torque[a,:]) / sum(dur[a]) #weighted by dur
avg_atts = [(avg_pitch[i], avg_roll[i]) for i in range(num_atts)]     

# Fit a smooth surface to the computed torques 
print('fitting data...')
def model_x(att, a, b, c, d):
    return a + b*att[0] + c*att[0]**2 + d*att[1] 
def model_y(att, a, b, c, d, e):
   return a + b*att[0] + c*att[0]**2 + d*att[0]**3 + e*att[0]**4
def model_z(att, a, b):
    return a + b*att[1]
avg_atts_array = array(avg_atts).transpose()
x0 = [ -1.39208956e-05,   2.07021035e-07,  -5.43520011e-10,   5.35834362e-07]
y0 = [ -2.06922329e-04,   7.14278290e-06,  -8.11274024e-08,   2.09825998e-10,   2.94297844e-13]
z0 = [  1.00000000e-05,  -3.07692308e-06]
x_params, x_covar = optimize.curve_fit(model_x, avg_atts_array, avg_torque[:,0], p0=x0, sigma=1/total_dur, maxfev=1000000)    
y_params, y_covar = optimize.curve_fit(model_y, avg_atts_array, avg_torque[:,1], p0=y0, sigma=1/total_dur, maxfev=1000000) 
z_params, z_covar = optimize.curve_fit(model_z, avg_atts_array, avg_torque[:,2], p0=z0, sigma=1/total_dur, maxfev=1000000) 

# Compute new torques to match MCC's solar torque table format
p = arange(45, 181)
r = arange(-30, 31)
P, R = meshgrid(p, r)
X_new = model_x((P, R), *x_params)
Y_new = model_y((P, R), *y_params)
Z_new = model_z((P, R), *z_params)

# Compute errors
x_err = model_x(avg_atts_array, *x_params) - avg_torque[:,1]
y_err = model_y(avg_atts_array, *y_params) - avg_torque[:,1]
z_err = model_z(avg_atts_array, *z_params) - avg_torque[:,1]
x_err_ss = sum(x_err.dot(x_err))
y_err_ss = sum(y_err.dot(y_err))
z_err_ss = sum(z_err.dot(z_err))

# Compute original errors (to see how much the automated software improved the fit)
x_err = model_x(avg_atts_array, *x0) - avg_torque[:,1]
y_err = model_y(avg_atts_array, *y0) - avg_torque[:,1]
z_err = model_z(avg_atts_array, *z0) - avg_torque[:,1]
x0_err_ss = sum(x_err.dot(x_err))
y0_err_ss = sum(y_err.dot(y_err))
z0_err_ss = sum(z_err.dot(z_err))

# Write new torques to comma-delimited text files for easy import into MCC
conv = 1.3558179483318882 # ft-lbf --> N-m
write_torque_table(X_new * conv, 'new_x_torques.txt')
write_torque_table(Y_new * conv, 'new_y_torques.txt')
write_torque_table(Z_new * conv, 'new_z_torques.txt')

# Import old solar torque tables
X_old = read_torque_table('old_x_torques.txt') / conv
Y_old = read_torque_table('old_y_torques.txt') / conv
Z_old = read_torque_table('old_z_torques.txt') / conv

# Print parameter summary to file (helpful for surface fitting)
f = open('param_summary.txt', 'w')
f.write('model:  \n \n')
f.write('x_params: \n')
f.write(str(x_params) + '\n')
f.write('y_params: \n')
f.write(str(y_params) + '\n')
f.write('z_params: \n')
f.write(str(z_params) + '\n \n')
f.write('SS Errors:  ' + str([x_err_ss, y_err_ss, z_err_ss]) + '\n')
f.write('Original SS Errors:  ' + str([x0_err_ss, y0_err_ss, z0_err_ss]))
f.close()

# Print zero roll values to file for analysis through time
#f = open('x_0_roll_thru_time.txt', 'a')
#f.write('\n' + 'old  ' + str(X_old[30,:]))
#f.write('\n' + 'new  ' + str(X_new[30,:]))
#f.close()
#f = open('y_0_roll_thru_time.txt', 'a')
#f.write('\n' + 'old  ' + str(Y_old[30,:]))
#f.write('\n' + 'new  ' + str(Y_new[30,:]))
#f.close()
#f = open('z_90_pitch_thru_time.txt', 'a')
#f.write('\n' + 'old  ' + str(Z_old[:,45]))
#f.write('\n' + 'new  ' + str(Z_new[:,45]))
#f.close()

# execfile('run_plots.py')