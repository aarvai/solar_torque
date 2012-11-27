chdir('plots')

# Plot X-Torque at 0 deg Roll through Time
f = open('../x_0_roll_thru_time.txt', 'r')
lines = f.readlines()
f.close()
figure()
for line in lines[:2]:
    fields = line.split()
    plot(arange(45,181), fields[1:], label=fields[0], linewidth=5)
for line in lines[2:]:
    fields = line.split()
    plot(arange(45,181), fields[1:], label=fields[0])
legend(loc='best')
grid()
title('0 Deg Roll Throughout Time')
ylabel('X-Torque [ft-lbf]')
xlabel('Pitch Angle [deg]')
tight_layout()
savefig('new_x_0_roll_thru_time.png')

# Plot Y-Torque at 0 deg Roll through Time
f = open('../y_0_roll_thru_time.txt', 'r')
lines = f.readlines()
f.close()
figure()
for line in lines[:2]:
    fields = line.split()
    plot(arange(45,181), fields[1:], label=fields[0], linewidth=5)
for line in lines[2:]:
    fields = line.split()
    plot(arange(45,181), fields[1:], label=fields[0])
legend(loc='best')
grid()
title('0 Deg Roll Throughout Time')
ylabel('Y-Torque [ft-lbf]')
xlabel('Pitch Angle [deg]')
tight_layout()
savefig('new_y_0_roll_thru_time.png')

# Plot Z-Torque at 0 deg Roll through Time
f = open('../z_0_roll_thru_time.txt', 'r')
lines = f.readlines()
f.close()
figure()
for line in lines[:2]:
    fields = line.split()
    plot(arange(45,181), fields[1:], label=fields[0], linewidth=5)
for line in lines[2:]:
    fields = line.split()
    plot(arange(45,181), fields[1:], label=fields[0])
legend(loc='best')
grid()
title('0 Deg Roll Throughout Time')
ylabel('Z-Torque [ft-lbf]')
xlabel('Pitch Angle [deg]')
tight_layout()
savefig('new_z_0_roll_thru_time.png')

# Plot Z-Torque at 90 deg Pitch through Time
f = open('../z_90_pitch_thru_time.txt', 'r')
lines = f.readlines()
f.close()
figure()
for line in lines[:2]:
    fields = line.split()
    plot(arange(-30,31), fields[1:], label=fields[0], linewidth=5)
for line in lines[2:]:
    fields = line.split()
    plot(arange(-30,31), fields[1:], label=fields[0])
legend(loc='best')
grid()
title('90 Deg Pitch Throughout Time')
ylabel('Z-Torque [ft-lbf]')
xlabel('Roll Angle [deg]')
tight_layout()
savefig('new_z_90_pitch_thru_time.png')

chdir('..')  