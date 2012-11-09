%make_new_solarPressureTorqueTable.m
clear solarPressureTorqueTable
solarPressureTorqueTable = zeros(61,136,3)
solarPressureTorqueTable(:,:,1) =csvread('new_x_torques.txt')
solarPressureTorqueTable(:,:,2) =csvread('new_y_torques.txt')
solarPressureTorqueTable(:,:,3) =csvread('new_z_torques.txt')
save solarPressureTorqueTable.mat solarPressureTorqueTable