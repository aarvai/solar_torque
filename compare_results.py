from os import chdir

from Chandra import Time

from utilities import read_MCC_results, find_closest, find_last_before, \
                      find_first_after, append_rss, ceil_to_value

# Inputs


print('comparing results...')
chdir('plots')

# Import predictions and actuals from MCC results text files
t_mcc, pred_old, act = read_MCC_results('../MCC_table_tests/orig_mom_pred_vs_tlm.txt')
t_mcc, pred_new, act = read_MCC_results('../MCC_table_tests/new_mom_pred_vs_tlm.txt')

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
act_torq = (act[i2_mcc] - act[i1_mcc]) / dur_dwells
errs_old_torq = act_torq - pred_old_torq
errs_new_torq = act_torq - pred_new_torq
errs_old_torq = append_rss(errs_old_torq)
errs_new_torq = append_rss(errs_new_torq)

# Plot histograms 
zipvals = zip((errs_old, errs_new, errs_old_torq, errs_new_torq), 
              ('Old ', 'New ', 'Old ', 'New '),
              (' Momentum', ' Momentum', ' Solar Torque', ' Solar Torque'),
              ('ft-lbf-sec', 'ft-lbf-sec', 'ft-lbf', 'ft-lbf'),
              ('mom_old', 'mom_new', 'torq_old', 'torq_new'),
              (1, 1, .00001, .00001))
for plot_log in [True, False]:
    for var, varstr1, varstr2, xlab, figname, d_bin in zipvals:
        figure() 
        labels = ('Roll', 'Pitch', 'Yaw', 'Total')
        max_error = ceil_to_value(abs(np.max(var)), d_bin)
        #max_error = ceil(abs(np.max(var))) 
        for i in range(4):
            subplot(4, 1, i + 1)
            if plot_log == True:
                hist(var[:, i], bins=arange(-max_error, max_error + d_bin, d_bin), 
                     log=True)
            else:  
                hist(var[:, i], bins=arange(-max_error, max_error + d_bin, d_bin))
            title(varstr1 + labels[i] + varstr2 + ' Prediction Errors')
            xlabel(xlab)
            ylabel('Occurrences')
            xlim((-max_error, max_error))
        tight_layout()
        if plot_log == True:  
            savefig('hist_' + figname + '_log.png')
        else:
            savefig('hist_' + figname + '.png')

#close('all')
   
chdir('..')    