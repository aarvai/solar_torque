To generate a new solar torque table:

1.  In a pylab Ska environment console: execfile('solar_torque.py') 
after tweaking the desired start and end times.

2.  Review the plots generated in the local "plots" folder, making
tweaks to solar_torque.py as needed.

3.  Use Matlab FOT Tool's MCC to compute the current momentum and 
solar torque errors using the flight environment:

    a.  Use Combined_Backstop_Maneuver_Summary.txt in 
        /home/aarvai/python/solar_torque/test_files
        while calls UNLOAD_check in the same directory.

    b.  Manually cut off maneuvers to:
        Start: 2012:202:05:00:00.000
        End:   2012:300:00:00:00.000

    c.  Use initial conditions A_LOADREVIEW_2012202.050004.txt.
    
    d.  Switch to System Momentum plot.

    e.  Use Ephemeris File Chandra_12150_12301.stk. 
    
    f.  On Momentum plot, overlay telemetry

    g.  Export Plot2Text as mom_pred_vs_tlm.txt
    
    h.  Save PNG.

    i.  Save workspace.	     
 
4.  Create a new solar torque table using the outputs of Step 1.  In a 
local version of Matlab, run "make_new_solarPressureTorqueTable.m".

5.  Work with the Software Manager to deploy the new solar torque table
"solarPressureTorqueTable.mat" to GRETA.

6.  Repeat Step 3 using the new testing version of MCC with the new
solar torque table.  Save the results to a different file.

7.  Back in the python console, execfile('compare_results.py') to ensure
errors have sufficiently decreased.
    
    