from os import chdir

from Chandra import Time

from utilities import read_MCC_results, find_closest, find_last_before, \
                      find_first_after, append_rss, ceil_to_value

print('comparing results...')
chdir('plots')

# Import predictions and actuals from MCC results text files
t_mcc1, pred_old, act1 = read_MCC_results('../MCC_tests/orig_mom_pred_vs_tlm.txt')
t_mcc2, pred_new, act2 = read_MCC_results('../MCC_tests/new_mom_pred_vs_tlm.txt')
if all(act1 == act2) & all(t_mcc1 == t_mcc2):
    act = act1
    t_mcc = t_mcc1
else:  print('actuals and/or times do not match between input files')

# Identify good dwell start and stop times 
# (uses results from solar_torque.py)
t1_filt = x['AOPCADMD'].times[i1]  
t2_filt = x['AOPCADMD'].times[i2]
t_npm_filt = array([t1_filt, t2_filt]).transpose() # good dwell pairs
i_prop_start = find_first_after(t_mcc[0], t_npm_filt[:,0])
i_prop_stop = find_last_before(t_mcc[-1], t_npm_filt[:,1])
t_npm_prop = t_npm_filt[i_prop_start[0]:i_prop_stop[0], :] # pairs w/in prop

# Compute momentum errors throughout propagation
errs_old = act - pred_old
errs_new = act - pred_new
errs_old = append_rss(errs_old)
errs_new = append_rss(errs_new)

# Find dwell start and stop times in MCC results
i1_mcc = find_first_after(t_npm_prop[:,0], t_mcc)
i2_mcc = find_last_before(t_npm_prop[:,1], t_mcc)

# Compute solar torque errors throughout propagation
dur_dwells = atleast_2d(t_mcc[i2_mcc] - t_mcc[i1_mcc]).transpose()
dur_dwells = hstack((dur_dwells, dur_dwells, dur_dwells))
pred_old_torq = (pred_old[i2_mcc] - pred_old[i1_mcc]) / dur_dwells
pred_new_torq = (pred_new[i2_mcc] - pred_new[i1_mcc]) / dur_dwells
# for actuals, use momentum predictions from Eng Archive - means have smaller errors
act_torq = (mom_2[i_prop_start[0]:i_prop_stop[0], :] - mom_1[i_prop_start[0]:i_prop_stop[0], :]) / dur_dwells
errs_old_torq = act_torq - pred_old_torq
errs_new_torq = act_torq - pred_new_torq
errs_old_torq = append_rss(errs_old_torq)
errs_new_torq = append_rss(errs_new_torq)

# Append RSS to momentum and torque
act = append_rss(act)
pred_old = append_rss(pred_old)
pred_new = append_rss(pred_new)
act_torq = append_rss(act_torq)
pred_old_torq = append_rss(pred_old_torq)
pred_new_torq = append_rss(pred_new_torq)
 
# Plot histograms 
zipvals = zip(((errs_old, errs_new), (errs_old_torq, errs_new_torq)), 
              (' Momentum', ' Solar Torque'),
              ('mom', 'torq'),
              ('ft-lbf-sec', 'ft-lbf'),
              ('5-min pts', 'Dwells'),
              (0.5, .000005))
for plot_log in [True, False]:
    for var, varstr, figname, xlab, ylab, d_bin in zipvals:
        figure(figsize=[16,11])
        labels = ('Roll', 'Pitch', 'Yaw', 'Total')
        max_error = max(abs(np.max(var[0])), abs(np.max(var[1])))
        max_bin = ceil_to_value(max_error, d_bin)
        for i in range(4):
            subplot(2, 2, i + 1)
            hist(var[0][:, i], bins=arange(-max_bin, max_bin + d_bin, d_bin), 
                 alpha=.1, hatch='/', color='b', log=plot_log, label='old')
            hist(var[1][:, i], bins=arange(-max_bin, max_bin + d_bin, d_bin), 
                 alpha=.1, hatch='\\', color='r', log=plot_log, label='new')
            legend()     
            title(labels[i] + varstr + ' Prediction Errors')
            xlabel(xlab)
            ylabel(ylab)
            xlim((-max_bin, max_bin))
            if plot_log == True:  
                savefig('hist_' + figname + '_log.png')
            else:
                savefig('hist_' + figname + '.png')

# Plot Attitudes (easier to see than in MCC)
x2 = fetch.Msidset(['PITCH', 'ROLL'], Time.DateTime(t_mcc[0]).date, Time.DateTime(t_mcc[-1]).date)
figure(figsize=[16,5.5])
subplot(2,1,1)
plot_cxctime(x2['PITCH'].times, x2['PITCH'].vals)
title('MCC Attitudes')
ylabel('Pitch [deg]')
subplot(2,1,2)
plot_cxctime(x2['ROLL'].times, x2['ROLL'].vals)
ylabel('Roll [deg]')
savefig('mcc_atts.png')

# Plot Momentum (easier to see than in MCC)
figure(figsize=[16,11])
ylab = ['X', 'Y', 'Z', 'Total']
for i in range(4):
    subplot(4,1,i+1)
    plot_cxctime(t_mcc, act[:,i], 'k', label='Actual')
    plot_cxctime(t_mcc, pred_old[:,i], 'b', label='Old Pred')
    plot_cxctime(t_mcc, pred_new[:,i], 'r', label='New Pred')
    ylabel(ylab[i] + ' Mom [ft-lbf-sec]')
    grid()
    if i == 0:
        legend()
        title('Predictions vs Actual Momentum')
savefig('mcc_comp_mom.png')        
    
# Plot Momentum Errors
figure(figsize=[16,11])
ylab = ['X', 'Y', 'Z', 'Total']
for i in range(4):
    subplot(4,1,i+1)
    plot_cxctime(t_mcc, errs_old[:,i], 'b.', label='Old Pred', markersize=5, mew=0)
    plot_cxctime(t_mcc, errs_new[:,i], 'r.', label='New Pred', markersize=5, mew=0)
    ylabel(ylab[i] + ' Mom Errors [ft-lbf-sec]')
    grid()
    if i == 0:
        legend()
        title('Momentum Errors')
savefig('mcc_comp_mom_errs.png')  

# Plot Torques
figure(figsize=[16,11])
ylab = ['X', 'Y', 'Z', 'Total']
for i in range(4):
    subplot(4,1,i+1)
    plot_cxctime(array([t_mcc[0], t_mcc[-1]]), array([0,0]), 'w.', mew=0, markersize=0) #needed for x-axes to match up with momentum plots
    plot_cxctime(t_mcc[i1_mcc] + dur_dwells[:,0] / 2, act_torq[:,i], 'k.', label='Actual', markersize=10, mew=0)
    plot_cxctime(t_mcc[i1_mcc] + dur_dwells[:,0] / 2, pred_old_torq[:,i], 'b.', label='Old Pred', markersize=10, mew=0)
    plot_cxctime(t_mcc[i1_mcc] + dur_dwells[:,0] / 2, pred_new_torq[:,i], 'r.', label='New Pred', markersize=10, mew=0)
    ylabel(ylab[i] + ' Torque [ft-lbf]')
    grid()
    if i == 0:
        legend()
        title('Predictions vs Actual Torque')
savefig('mcc_comp_torq.png')    

# Plot Torque Errors
figure(figsize=[16,11])
ylab = ['X', 'Y', 'Z', 'Total']
for i in range(4):
    subplot(4,1,i+1)
    plot_cxctime(array([t_mcc[0], t_mcc[-1]]), array([0,0]), 'w.', mew=0, markersize=0) #needed for x-axes to match up with momentum plots
    plot_cxctime(t_mcc[i1_mcc] + dur_dwells[:,0] / 2, errs_old_torq[:,i], 'b.', label='Old Pred', markersize=10, mew=0)
    plot_cxctime(t_mcc[i1_mcc] + dur_dwells[:,0] / 2, errs_new_torq[:,i], 'r.', label='New Pred', markersize=10, mew=0)
    ylabel(ylab[i] + ' Torque Errors [ft-lbf]')
    grid()
    if i == 0:
        legend()
        title('Torque Errors')
savefig('mcc_comp_torq_errs.png')   


#close('all')
   
chdir('..')    
