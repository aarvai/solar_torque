# Plot solar torques  in 3D
zipvals = zip((X_old, Y_old, Z_old, X_new, Y_new, Z_new),
              ('Old X', 'Old Y', 'Old Z', 'New X', 'New Y', 'New Z'))
for var, var_str in zipvals:
    fig = figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.plot_surface(R, P, var, cmap='jet')
    title(var_str + ' Torques [ft-lbf]')
    xlabel('Roll [deg]')
    ylabel('Pitch [deg]')

# Compare old and new torques at zero roll angle
figure()
zipvals = zip(((X_old, X_new), (Y_old, Y_new), (Z_old, Z_new)),
              ('X', 'Y', 'Z'),
              (1,2,3), 
              ([-0.00006, 0.00008], [-0.0008, 0.0004], [-0.0001, 0.0001]))
for vars, var_str, sub, ylims in zipvals:
    subplot(3,1,sub)
    i = (roll == 0)
    scatter(pitch[i], torque[i, sub - 1],  c='k', s=2, lw=0)
    plot(P[30,:], vars[0][30,:], 'b', label='old', lw=2)
    plot(P[30,:], vars[1][30,:], 'r', label='new', lw=2)
    title(var_str + ' Torques for Zero Roll Angle')
    legend(loc='best')
    grid()
    xlabel('Pitch Angle [deg]')
    ylabel(var_str + ' Torque [ft-lbf]')
    ylim(ylims)
tight_layout()
    
# Plot torques by time (to identify outliers for filtering)
print('plotting...')
labels = ('X', 'Y', 'Z')
for i in range(3):
    figure()
    plot_cxctime(t1 + 1/2 * dur, torque[:,i], 'b*')
    title(labels[i] + ' Torque [ft-lbf]')

# Plot torques by time, colored by roll, pitch, and dur (again for outliers)
zipvals = zip((roll_1, pitch_1, dur), ('Roll', 'Pitch', 'Duration'))
for var, var_str in zipvals:
    figure()
    
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
figure()
for i in range(3):
   subplot(3, 1, i + 1)
   scatter(avg_pitch, avg_roll, c=avg_torque[:,i], marker='o', cmap=cm.jet, lw=0)
   colorbar()
   
# Plot Number of Dwells by attitude
figure()
subplot(3, 1, 1)
title('Color = Number of Dwells')   
for i in range(3):
   subplot(3, 1, i + 1)
   scatter(avg_pitch, avg_roll, c=num_dwells, marker='o', cmap=cm.jet, lw=0)
   colorbar()
   
# Plot Duration by attitude, capping duration at 5 ksec
figure()
i = dur < 5000
subplot(3, 1, 1)
scatter(t1[i] + 1/2 * dur[i], torque[i,0], c=dur[i], lw=0)
ylim([-0.00006, 0.00008])
colorbar()
title('Color = Duration')
subplot(3, 1, 2)
scatter(t1[i] + 1/2 * dur[i], torque[i,1], c=dur[i], lw=0)
ylim([-0.0008, 0.0004])
colorbar()
subplot(3, 1, 3)
scatter(t1[i] + 1/2 * dur[i], torque[i,2], c=dur[i], lw=0)
ylim([-0.0001, 0.0001])
colorbar()

# Plot histograms of prediction errors 
pred, act = read_MCC_results('orig_mom_pred_vs_tlm.txt')
errs = act - pred
figure()
labels = ('Roll', 'Pitch', 'Yaw')
max_error = ceil(abs(np.max(errs)))
for i in range(3):
    subplot(3, 1, i + 1)
    hist(errs[:, i], bins=arange(-max_error, max_error + 1))
    title(labels[i] + ' Momentum Prediction Errors')
    xlabel('ft-lbf-sec')
    ylabel('Occurrences')
    xlim((-max_error, max_error))
tight_layout()    