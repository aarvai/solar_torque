nsm = ['2000:228:00:00:00.000 2000:230:00:00:00.000',  # NSM #2 for lunar eclipse demo
       '2000:302:00:00:00.000 2000:304:00:00:00.000',  # NSM #3 for lunar eclipse
       '2001:111:00:00:00.000 2001:113:00:00:00.000',  # NSM #4 earth occultation
       '2004:200:00:00:00.000 2004:202:00:00:00.000',  # NSM #5 for penumbra only eclipse
       '2004:208:00:00:00.000 2004:210:00:00:00.000',  # NSM #6 for eclipse contingency
       '2004:213:00:00:00.000 2004:215:00:00:00.000',  # NSM #7 for eclipse contingency
       '2004:315:00:00:00.000 2004:317:00:00:00.000',  # NSM #8 for BSH out of FSS FOV
       '2008:225:00:00:00.000 2008:229:00:00:00.000',  # NSM #9 for CTU reset
       '2008:292:00:00:00.000 2008:296:00:00:00.000',  # NSM #10 for IU reset
       '2010:150:00:00:00.000 2010:152:00:00:00.000',  # NSM #11 for IU reset
       '2011:299:00:00:00.000 2011:301:00:00:00.000']  # NSM #12 for CTU reset                         
             
ssm = ['2000:048:00:00:00.000 2000:050:00:00:00.000',  # SSM #2 quat update in NPM
       '2011:187:12:00:00.000 2011:192:04:00:00.000',  # SSM #3 for CEBR timeout
       '2012:150:00:00:00.000 2012:153:00:00:00.000']  # SSM #4 for FSS degradation        
       
outliers = ['2000:046:05:55:00.000 2000:046:07:46:00.000',  # extreme outlier in roll torque  
            '2001:202:18:50:00.000 2001:202:21:20:00.000',  # extreme outlier in roll torque  
            '2003:053:08:20:00.000 2003:053:08:55:00.000',  # extreme outlier in roll torque 
            '2003:002:02:40:00.000 2003:002:03:00:00.000',  # extreme outlier in pitch torque 
            '2001:202:18:50:00.000 2001:202:21:20:00.000']  # extreme outlier in yaw torque