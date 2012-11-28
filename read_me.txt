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

    e.  Use Ephemeris File Chandra_12150_13001.stk. 
    
    f.  On Momentum plot, overlay telemetry.

    g.  Export Plot2Text as mom_pred_vs_tlm.txt
    
    h.  Save PNG.

    i.  Save workspace (although MCC probably can't import it - too large).	     
 
4.  Create a new solar torque table using the outputs of Step 1.  In a 
local version of Matlab, run "make_new_solarPressureTorqueTable.m".

5.  Work with the Software Manager to deploy the new solar torque table
"solarPressureTorqueTable.mat" to GRETA.

6.  Repeat Step 3 using the new testing version of MCC with the new
solar torque table.  Save the results to a different file.

7.  Back in the python console, execfile('compare_results.py') to ensure
errors have sufficiently decreased.  Note that this script relies on 
data from Step 1.

8.  If it is desired to compare the results at key attitudes (e.g. zero 
roll for X and Y torques, 90 deg pitch for Z torques), un-comment the 
write-to-file commands at the end of solar_torque.py and add descriptive
notes for the current run.  For example, "2000-2001" when only using 
2000 and 2001 data.  This will append the parameters to the existing 
text files.  Reformat new text to match current format.  Re-run Step 1
as necessary.  Then plot results in python using 
execfile('compare_thru_time.py').
    
    