from os import chdir

chdir('plots')
print('plotting...')

# Plot solar torques  in 3D
zipvals = zip((X_old, Y_old, Z_old, X_new, Y_new, Z_new),
              ('Old X', 'Old Y', 'Old Z', 'New X', 'New Y', 'New Z'),
              (0, 1, 2, 0, 1, 2))
for var, var_str, col in zipvals:
    fig = figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.plot_surface(R, P, var, cmap='jet')
    ax.scatter(avg_roll, avg_pitch, avg_torque[:,col])
    title(var_str + ' Torques [ft-lbf]')
    xlabel('Roll [deg]')
    ylabel('Pitch [deg]')
    figname = var_str[:3] + '_' + var_str[4] + '_3d.png'
    savefig(figname.lower())    

# Plot new torques by pitch for various roll angles
figure()
zipvals = zip((X_new, Y_new, Z_new),
              ('X', 'Y', 'Z'),
              (1,2,3), 
              ([-0.00006, 0.00008], [-0.0008, 0.0004], [-0.0001, 0.0001]))
zipvals2 = zip((-30, -20, -10, 0, 10, 20, 30),
               ('r:', 'b:', 'g:', 'k', 'g-', 'b-', 'r-'))
for vars, var_str, sub, ylims in zipvals:
    subplot(3,1,sub)
    for roll_i, plot_str in zipvals2:
        i = (R[:,0] == roll_i)
        plot(P[i,:][0], vars[i,:][0], plot_str, label='Roll = ' + str(roll_i))
    plot(avg_pitch, avg_torque[:, sub - 1], '.')
    title('New ' + var_str + ' Torques for Various Roll Angles')
    #legend(loc='best')
    grid()
    xlabel('Pitch Angle [deg]')
    ylabel(var_str + ' Torque [ft-lbf]')
    #ylim(ylims)
tight_layout()
savefig('new_by_pitch_various_rolls.png')

# Plot new torques by roll for various pitch angles
figure()
zipvals = zip((X_new, Y_new, Z_new),
              ('X', 'Y', 'Z'),
              (1,2,3), 
              ([-0.00006, 0.00008], [-0.0008, 0.0004], [-0.0001, 0.0001]))
zipvals2 = zip((45, 70, 90, 110, 135, 155, 180),
               ('r:', 'b:', 'g:', 'k', 'g-', 'b-', 'r-'))
for vars, var_str, sub, ylims in zipvals:
    subplot(3,1,sub)
    for pitch_i, plot_str in zipvals2:
        i = (P[0,:] == pitch_i)
        plot(R[:,i][0], vars[:,i][0], plot_str, label='Pitch = ' + str(pitch_i))
    plot(avg_roll, avg_torque[:, sub - 1], '.')
    title('New ' + var_str + ' Torques for Various Pitch Angles')
    legend(loc='best')
    grid()
    xlabel('Roll Angle [deg]')
    ylabel(var_str + ' Torque [ft-lbf]')
    ylim(ylims)
tight_layout()
savefig('new_by_roll_various_pitches.png')

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
savefig('both_at_0_roll.png')

# Compare old and new torques at zero roll angle  - just pitch torque
figure()
i = (roll == 0)
scatter(pitch[i], torque[i, 1],  c='k', s=2, lw=0)
plot(P[30,:], Y_old[30,:], 'b', label='old', lw=5)
plot(P[30,:], Y_new[30,:], 'r', label='new', lw=5)
title('Y Torques for Zero Roll Angle')
legend(loc='best')
grid()
xlabel('Pitch Angle [deg]')
ylabel('Y Torque [ft-lbf]')
ylim([-0.00012, 0.0000])
tight_layout()
savefig('both_at_0_roll_pitch_only.png')


# Compare old and new torques at 90 deg pitch
figure()
zipvals = zip(((X_old, X_new), (Y_old, Y_new), (Z_old, Z_new)),
              ('X', 'Y', 'Z'),
              (1,2,3), 
              ([-0.00006, 0.00008], [-0.0008, 0.0004], [-0.0001, 0.0001]))
for vars, var_str, sub, ylims in zipvals:
    subplot(3,1,sub)
    i = (pitch == 90)
    scatter(roll[i], torque[i, sub - 1],  c='k', s=2, lw=0)
    plot(R[:,45], vars[0][:,45], 'b', label='old', lw=2)
    plot(R[:,45], vars[1][:,45], 'r', label='new', lw=2)
    title(var_str + ' Torques for 90 Deg Pitch')
    legend(loc='best')
    grid()
    xlabel('Roll Angle [deg]')
    ylabel(var_str + ' Torque [ft-lbf]')
    ylim(ylims)
tight_layout()
savefig('both_at_90_pitch.png')

# Plot torques by time (to identify outliers for filtering)
labels = ('X', 'Y', 'Z')
for i in range(3):
    figure()
    plot_cxctime(t1 + 1/2 * dur, torque[:,i], 'b*')
    title(labels[i] + ' Torque [ft-lbf]')
    savefig('all_' + labels[i].lower() + '_pts_by_time.png')

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
    savefig('all_pts_by_time_' + var_str.lower() + '.png')

# Plot torques by attitude - 2D color plot (to see the raw "averaged" data w/o surface fit)
figure()
for i in range(3):
   subplot(3, 1, i + 1)
   scatter(avg_pitch, avg_roll, c=avg_torque[:,i], marker='o', cmap=cm.jet, lw=0)
   colorbar()
savefig('avg_by_att_2d.png')

# Plot torques by pitch
figure()
for i in range(3):
   subplot(3, 1, i + 1)
   plot(avg_pitch, avg_torque[:,i], '.')
subplot(3, 1, 1)
title('Torques by Pitch')
savefig('avg_by_pitch.png')

# Plot torques by roll
figure()
for i in range(3):
   subplot(3, 1, i + 1)
   plot(avg_roll, avg_torque[:,i], '.')
subplot(3, 1, 1)
title('Torques by Roll')
savefig('avg_by_roll.png')

# Plot torques by attitude - 3D plot (to see the raw "averaged" data w/o surface fit)
fig = figure()
zipvals = zip((311, 312, 313), (0, 1, 2))
for sub, var in zipvals:
   ax = fig.add_subplot(sub, projection = '3d')
   ax.scatter(avg_pitch, avg_roll, avg_torque[:,var])
savefig('avg_by_att_3d.png')

# Plot Number of Dwells by attitude
figure()
subplot(3, 1, 1)
title('Color = Number of Dwells')   
for i in range(3):
   subplot(3, 1, i + 1)
   scatter(avg_pitch, avg_roll, c=num_dwells, marker='o', cmap=cm.jet, lw=0)
   colorbar()
savefig('avg_by_att_num.png')

# Plot Total Duration by attitude
figure()
subplot(3, 1, 1)
title('Color = Total Duration')   
for i in range(3):
   subplot(3, 1, i + 1)
   scatter(avg_pitch, avg_roll, c=total_dur, marker='o', cmap=cm.jet, lw=0)
   colorbar()
savefig('avg_by_att_total_dur.png')

# Plot Duration by time, capping duration at 5 ksec
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
savefig('avg_by_time_dur.png')

# Plot 0 deg Roll through Time
f = open('../pitch_0_roll_thru_time.txt', 'r')
lines = f.readlines()
f.close()
figure()
for line in lines[:2]:
    fields = line.split()
    plot(arange(45,181), fields[1:], label=fields[0], linewidth=5)
for line in lines[2:]:
    fields = line.split()
    plot(arange(45,181), fields[1:], label=fields[0])
legend()
grid()
title('0 Deg Roll Throughout Time')
ylabel('Y-Torque [ft-lbf]')
xlabel('Pitch Angle [deg]')
savefig('new_0_roll_thru_time.png')

chdir('..')    
#close('all')  
    
    
    

# Plot just x in 3D
#fig = figure()
#ax = fig.add_subplot(111, projection='3d')
#ax.scatter(avg_pitch, avg_roll, avg_torque[:,0])