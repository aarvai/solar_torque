# Plot old solar torques 
fig = figure()
ax = fig.add_subplot(111, projection='3d')
ax.plot_surface(R, P, X_old, cmap='jet')

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
title('Color = Number of Dwells')
subplot(3, 1, 2)
scatter(avg_pitch, avg_roll, c=num_dwells, marker='o', cmap=cm.jet, lw=0)
colorbar()
subplot(3 ,1, 3)
scatter(avg_pitch, avg_roll, c=num_dwells, marker='o', cmap=cm.jet, lw=0)
colorbar()

figure(9)
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