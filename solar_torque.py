import numpy as np
from matplotlib import pyplot as pp
#from Scientific.Functions.LeastSquares import leastSquaresFit
from scipy import optimize
from mpl_toolkits.mplot3d import Axes3D

from Chandra import Time
from Ska.engarchive import fetch_eng as fetch
from Ska.Matplotlib import plot_cxctime

from utilities import overlap, str_to_secs, read_torque_table, write_torque_table
from bad_times import nsm, ssm, outliers

close('all')

# Inputs
t_start = '2000:001'
t_stop = '2012:300'
min_alt = 66400000 #m from center of earth
min_dur = 2500 #sec (shorter dwells yielded inaccurate readings)

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
    raise StandardError('Timeframe must start and end in Normal Point mode + 10 minute pad.')
i1_npm = ~npm[:-2] & npm[1:-1] & npm[2:] 
i2_npm = npm[:-2] & npm[1:-1] & ~npm[2:]
i1_npm = append(zeros(2, dtype='bool'), i1_npm)  # delay start time by 5 min
i2_npm = append(append(zeros(1, dtype='bool'), i2_npm), zeros(1, dtype='bool'))
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
    avg_torque[i,:] = dur[a].dot(torque[a,:]) / sum(dur[a])  
avg_atts = [(avg_pitch[i], avg_roll[i]) for i in range(num_atts)]     

# Fit a smooth surface to the computed torques using fit approach #5
print('fitting data...')
def model_x(att, a, b, c):
    return a + b*att[0] + c*att[1]
def model_y(att, a, b, c, d):
    return a + b*sin(att[0]*c + d) 
def model_z(att, a, b):
    return a + b*att[1]
avg_atts_array = array(avg_atts).transpose()
x0 = [ -6.24346074e-06,   6.51787933e-08,   7.25513601e-07]
y0 = [ -6.46051399e-05,  -4.08457660e-05,   4.69801335e-02,   1.46983147e+00]
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
f.write('model:  fit #5 (different models for each)  \n \n')
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
#f = open('pitch_0_roll_thru_time.txt', 'a')
#f.write('\n' + 'old  ' + str(Y_old[30,:]))
#f.close()

# execfile('run_plots.py')

# fit #1:  http://stackoverflow.com/questions/12617985/fitting-a-linear-surface-with-numpy-least-squares
# has the model:   a + b*pitch + c*pitch^2 + d*roll + e*roll^2 + f*pitch*roll  = torque
# result:  params = array([a, b, c, d, e, f])
# A = make_A_matrix(avg_pitch, avg_roll)
# x_params, x_resid, rank, sigma = lstsq(A, avg_torque[:,0])
# y_params, x_resid, rank, sigma = lstsq(A, avg_torque[:,1])
# z_params, x_resid, rank, sigma = lstsq(A, avg_torque[:,2])

#fit 2:  http://www.velocityreviews.com/forums/t329682-surface-fitting-library-for-python.html
#x_data = [((avg_pitch[i], avg_roll[i]), avg_torque[i,0]) for i in range(num_atts)]
#y_data = [((avg_pitch[i], avg_roll[i]), avg_torque[i,1]) for i in range(num_atts)]
#z_data = [((avg_pitch[i], avg_roll[i]), avg_torque[i,2]) for i in range(num_atts)]
#x_init_params = [0, 0, 0]
#y_init_params = [0, 0, 0]
#z_init_params = [0, 0, 0]
#def model(params, xy):
#    a, b, c = params
#    x, y = xy
#    return a*x + b*y + c
#x_fit_params, x_chisquared = leastSquaresFit(model, x_init_params, x_data)    
#y_fit_params, y_chisquared = leastSquaresFit(model, y_init_params, y_data) 
#z_fit_params, z_chisquared = leastSquaresFit(model, z_init_params, z_data) 

#fit 3:  http://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.curve_fit.html
#print('fitting data...')
#def model(att, a, b, c, d, e, f, g, h, i):
#    return a + b*att[0] + c*att[1] + d*sin(att[0]*e + f) + g*sin(att[1]*h + i)
#avg_atts_array = array(avg_atts).transpose()
#x0 = [-0.000011, 0.0000001, 0.00001,  0,       0,          0,       0, 0, 0]
#y0 = [-0.000060, 0,         0,       -0.00005, 0.04363323, 1.91986, 0, 0, 0]
#z0 = [0,         0,        -0.000015, 0,       0,          0,       0, 0, 0]
#x_params, x_covar = optimize.curve_fit(model, avg_atts_array, avg_torque[:,0], p0=x0, sigma=total_dur, maxfev=1000000)    
#y_params, y_covar = optimize.curve_fit(model, avg_atts_array, avg_torque[:,1], p0=y0, sigma=total_dur, maxfev=1000000) 
#z_params, z_covar = optimize.curve_fit(model, avg_atts_array, avg_torque[:,2], p0=z0, sigma=total_dur, maxfev=1000000) 

# fit #4:  slightly different model
#print('fitting data...')
#def model(att, a, b, c, d, e, f, g, h):
#    return a + b*att[0] + c*att[0]*att[0] + d*att[1] + e*att[1]*att[1] * f*sin(att[0]*g + h) 
#avg_atts_array = array(avg_atts).transpose()
#x0 = [-0.000011, 0.0000001, 0,  0.00001,  0,  0,       0,          0     ]
#y0 = [-0.000060, 0,         0,  0,        0, -0.00005, 0.04363323, 1.91986]
#z0 = [0,         0,         0, -0.000015, 0,  0,       0,          0     ]
#x_params, x_covar = optimize.curve_fit(model, avg_atts_array, avg_torque[:,0], p0=x0, sigma=total_dur, maxfev=1000000)    
#y_params, y_covar = optimize.curve_fit(model, avg_atts_array, avg_torque[:,1], p0=y0, sigma=total_dur, maxfev=1000000) 
#z_params, z_covar = optimize.curve_fit(model, avg_atts_array, avg_torque[:,2], p0=z0, sigma=total_dur, maxfev=1000000) 

# fit #5:  different model for each axis
#print('fitting data...')
#def model_x(att, a, b, c):
#    return a + b*att[0] + c*att[1]
#def model_y(att, a, b, c, d):
#    return a + b*sin(att[0]*c + d) 
#def model_z(att, a, b):
#    return a + b*att[1]
#avg_atts_array = array(avg_atts).transpose()
#x0 = [ -6.24346074e-06,   6.51787933e-08,   7.25513601e-07]
#y0 = [ -6.46051399e-05,  -4.08457660e-05,   4.69801335e-02,   1.46983147e+00]
#z0 = [  4.74038890e-06,  -1.35816177e-06]
#x_params, x_covar = optimize.curve_fit(model_x, avg_atts_array, avg_torque[:,0], p0=x0, sigma=total_dur, maxfev=1000000)    
#y_params, y_covar = optimize.curve_fit(model_y, avg_atts_array, avg_torque[:,1], p0=y0, sigma=total_dur, maxfev=1000000) 
#z_params, z_covar = optimize.curve_fit(model_z, avg_atts_array, avg_torque[:,2], p0=z0, sigma=total_dur, maxfev=1000000) 








#Per http://www.coursehero.com/file/5970417/lec13nonlinearregression/:
#There are several approaches, some easier to use and some are more robust. leastSquaresFit in 

#Scientific.Functions.LeastSquares 
#use: fit=leastSquaresFit(funct,params,data) 
#comments: pretty easy to use, often works fine (converges on a reasonable answer), but will quickly run away with difficult fits. 
#returns: tuple of fitted parameters and error 

#curve_fit in scipy.optimize 
#use: fit=curve_fit (funct,xdata,ydata,p0=params0) 
#comments: not quite as convenient, but more robust almost always will converge. 
#returns: tuple of fitted parameters, covariance matrix sin( t + ) 