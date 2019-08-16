#Zeeshan's CEC tool logic
import math
import numpy as np
import datetime
import pandas as pd
import matplotlib.pyplot as plt

def getjsondata(tilt_angles=[0],azimuths_list=[0],lat=-33.93,time_int=30,global_irr_data=[6.61,5.76,5,3.9,2.81,2.37,2.64,3.69,4.79,5.61,6.19,6.74]):
    #angle_input=[0,10] #Taken as User input in degrees for tilt angle
    tilt_angle=tilt_angles
    tilt_angle[:] = [-1*x for x in tilt_angle]
    azimuth=azimuths_list #Taken as User input in degrees
    interval=time_int #User input in minutes and shows option for only 30 or 15 mins 
    latitude=lat
    global_irr=[x/3.6 for x in global_irr_data ]

    interval_length=24*(60/interval)
    #tilt_angle=-1*tilt_angle #For southern hemisphere
    x=str(interval)+'T'
    ax=['15-Jan','15-Feb','15-Mar','15-Apr','15-May','15-Jun','15-July','15-Aug','15-Sep','15-Oct','15-Nov','15-Dec']
    if(interval==30):
        time_series=pd.timedelta_range(0,periods=interval_length,freq="30T")
    else:
         time_series=pd.timedelta_range(0,periods=interval_length,freq="15T")

    days=np.array([15,46,74,105,135,166,196,227,258,288,319,349],dtype=np.int_) #Day number
    #days=np.array([15,46,74,105,135,166,196,227,258,288,319,349],dtype=np.int_)
    #now=datetime.datetime.now()
    for m in tilt_angle:
        #tilt_angle=angle_input[m]
        #tilt_angle=-1*tilt_angle #For southern hemisphere
        for k in range(len(azimuth)):
            for j in range(len(ax)):

                if(j==0):
                    output=pd.DataFrame({'Day': ax[j],'Time interval':time_series})

                    #df = pd.DataFrame(data=[[91],[time_series]])
                    #df 
                    #output2=pd.DataFrame({'Day': '15-Feb','Time interval':time_series})
                    #output3=pd.concat([output,output2],ignore_index=True)
                    #output3
                    hourofday = time_series / np.timedelta64(1, 'h') #gets hour of day from the time_series
                    hourofday=np.asarray(hourofday,dtype=np.float_)

                    #declination=np.full_like(hourofday,1)

                    declination_angle=23.45*np.sin(np.radians(360*(284+days[j])/365))
                    #declination_angle=np.full_like(hourofday,declination_angle)
                    value1=np.degrees(np.arccos(-1*np.arctan(np.radians(latitude))*np.arctan(np.radians(declination_angle))))
                    value2=np.degrees(np.arccos(-1*np.arctan(np.radians(latitude+m))*np.arctan(np.radians(declination_angle))))
                    if (value1 < value2):
                        sunset_angle=value1
                    else:
                        sunset_angle=value2
                    #sunset_angle
                    #sunset_angle=np.full_like(hourofday,sunset_angle)
                    #output['Declination Angle']=output.index
                    output['Declination Angle']=np.round(declination_angle,2)
                    output['Sunset Angle']=np.round(sunset_angle,2)

                    hour_angle=np.full_like(hourofday,1)
                    #h0=np.full_like(hourofday,1)
                    h0=(24/math.pi)*3600*1368*(1+0.033*np.cos(2*math.pi*days[j]/365))*(np.cos(np.radians(latitude))*np.cos(np.radians(declination_angle))*np.sin(np.radians(sunset_angle))+np.radians(declination_angle)*np.sin(np.radians(latitude))*np.sin(np.radians(declination_angle)))*(0.000001/3.6)
                    kt=global_irr[j]/h0
                    # hd is the Daily diffuse radiation and following are the conditions based on the value of kt
                    if(kt>0.17 and kt<0.75):
                        hd=(1.188-2.272*kt+9.473*kt**2-21.865*kt**3+14.648*kt**4)*global_irr[j]
                    elif (kt<0.17):
                        hd=0.99*global_irr[j]
                    elif (kt>0.75 and kt<0.8):
                        hd=(0.632-0.5*kt)*global_irr[j]
                    else:
                        hd=0.2*global_irr[j]
                    a=0.409+0.5016*np.sin(np.radians(sunset_angle)-(math.pi/3))
                    b=0.6609-0.4767*np.sin(np.radians(sunset_angle)-(math.pi/3))
                    rt=np.full_like(hourofday,1)
                    rd=np.full_like(hourofday,1)
                    rb=np.full_like(hourofday,1)
                    interval_rad=np.full_like(hourofday,1)
                    interval_diff=np.full_like(hourofday,1)
                    interval_beam=np.full_like(hourofday,1)
                    theta_z=np.full_like(hourofday,1)
                    theta_t=np.full_like(hourofday,1)
                    total_array=np.full_like(hourofday,1)
                    for i in range(len(hourofday)): 

                        if(abs(hourofday[i]-12)*15 > abs(sunset_angle)):
                            hour_angle[i]=0
                        else:
                            hour_angle[i]=(hourofday[i]-12)*15
                        rt[i]=(math.pi/interval_length)*(a+b*np.cos(np.radians(hour_angle[i])))*(((np.cos(np.radians(hour_angle[i])))-np.cos(np.radians(sunset_angle)))/(np.sin(np.radians(sunset_angle))-np.radians(sunset_angle)*np.cos(np.radians(sunset_angle))))
                        rd[i]=(math.pi/interval_length)*((np.cos(np.radians(hour_angle[i]))-np.cos(np.radians(sunset_angle)))/(np.sin(np.radians(sunset_angle))-np.radians(sunset_angle)*np.cos(np.radians(sunset_angle))))
                        if(hour_angle[i]==0 and hourofday[i]!=12):
                            interval_rad[i]=0
                            interval_diff[i]=0
                            theta_z[i]=0
                            theta_t[i]=0
                            rb[i]=0
                            interval_beam[i]=interval_rad[i]-interval_diff[i]
                            total_array[i]=0
                        else:
                            interval_rad[i]=global_irr[j]*rt[i]
                            interval_diff[i]=rd[i]*hd
                            theta_z[i]=np.degrees(np.arccos(np.sin(np.radians(declination_angle))*np.sin(np.radians(latitude))+np.cos(np.radians(declination_angle))*np.cos(np.radians(latitude))*np.cos(np.radians(hour_angle[i]))))
                            theta_t[i]=np.degrees(np.arccos(np.sin(np.radians(declination_angle))*np.sin(np.radians(latitude))*np.cos(np.radians(m))-np.sin(np.radians(declination_angle))*np.cos(np.radians(latitude))*np.sin(np.radians(m))*np.cos(np.radians(azimuth[k]))+np.cos(np.radians(declination_angle))*np.cos(np.radians(latitude))*np.cos(np.radians(m))*np.cos(np.radians(hour_angle[i]))+np.cos(np.radians(declination_angle))*np.sin(np.radians(latitude))*np.sin(np.radians(m))*np.cos(np.radians(azimuth[k]))*np.cos(np.radians(hour_angle[i]))+np.cos(np.radians(declination_angle))*np.sin(np.radians(m))*np.sin(np.radians(azimuth[k]))*np.sin(np.radians(hour_angle[i]))))
                            if(theta_t[i]>90):
                                rb[i]=0
                            else:
                                rb[i]=np.cos(np.radians(theta_t[i]))/np.cos(np.radians(theta_z[i]))
                            if(interval_diff[i]>interval_rad[i]):
                                interval_beam[i]=0
                                interval_diff[i]=interval_rad[i]
                            else:
                                interval_beam[i]=interval_rad[i]-interval_diff[i]
                            interval_beam[i]=interval_beam[i]*rb[i]
                            interval_diff[i]=interval_diff[i]*((1+np.cos(np.radians(m)))/2)
                            #total_array[i]=interval_beam[i]*rb[i]+interval_diff[i]*((1+np.cos(np.radians(tilt_angle)))/2)
                            total_array[i]=interval_beam[i]+interval_diff[i]

                    #Assigning to output
                    output['Hour Angle']=hour_angle
                    output['Daily extraterr']=np.round(h0,2)
                    output['Daily diffuse radiation']=np.round(hd,2)
                    output['Total radiation (kWh)']=np.round(interval_rad,4)
                    output['Interval diffuse']=np.round(interval_diff,4)
                    output['Interval beam']=np.round(interval_beam,4)
                    output['cos(Theta Z)']=np.round(theta_z,2)
                    output['cos(Theta T)']=np.round(theta_t,2)
                    output['Total Array Radiation (kWh/m2/interval)']=np.round(total_array,4)
                    #output['tilt']=tilt_angle

                else:
                    output2=pd.DataFrame({'Day': ax[j],'Time interval':time_series})

                    #df = pd.DataFrame(data=[[91],[time_series]])
                    #df 
                    #output2=pd.DataFrame({'Day': '15-Feb','Time interval':time_series})
                    #output3=pd.concat([output,output2],ignore_index=True)
                    #output3
                    hourofday = time_series / np.timedelta64(1, 'h') #gets hour of day from the time_series
                    hourofday=np.asarray(hourofday,dtype=np.float_)

                    #declination=np.full_like(hourofday,1)

                    declination_angle=23.45*np.sin(np.radians(360*(284+days[j])/365))
                    #declination_angle=np.full_like(hourofday,declination_angle)
                    value1=np.degrees(np.arccos(-1*np.arctan(np.radians(latitude))*np.arctan(np.radians(declination_angle))))
                    value2=np.degrees(np.arccos(-1*np.arctan(np.radians(latitude+m))*np.arctan(np.radians(declination_angle))))
                    if (value1 < value2):
                        sunset_angle=value1
                    else:
                        sunset_angle=value2
                    #sunset_angle
                    #sunset_angle=np.full_like(hourofday,sunset_angle)
                    #output['Declination Angle']=output.index
                    output2['Declination Angle']=np.round(declination_angle,2)
                    output2['Sunset Angle']=np.round(sunset_angle,2)

                    hour_angle=np.full_like(hourofday,1)
                    #h0=np.full_like(hourofday,1)
                    h0=(24/math.pi)*3600*1368*(1+0.033*np.cos(2*math.pi*days[j]/365))*(np.cos(np.radians(latitude))*np.cos(np.radians(declination_angle))*np.sin(np.radians(sunset_angle))+np.radians(declination_angle)*np.sin(np.radians(latitude))*np.sin(np.radians(declination_angle)))*(0.000001/3.6)
                    kt=global_irr[j]/h0
                    # hd is the Daily diffuse radiation and following are the conditions based on the value of kt
                    if(kt>0.17 and kt<0.75):
                        hd=(1.188-2.272*kt+9.473*kt**2-21.865*kt**3+14.648*kt**4)*global_irr[j]
                    elif (kt<0.17):
                        hd=0.99*global_irr[j]
                    elif (kt>0.75 and kt<0.8):
                        hd=(0.632-0.5*kt)*global_irr[j]
                    else:
                        hd=0.2*global_irr[j]
                    a=0.409+0.5016*np.sin(np.radians(sunset_angle)-(math.pi/3))
                    b=0.6609-0.4767*np.sin(np.radians(sunset_angle)-(math.pi/3))
                    rt=np.full_like(hourofday,1)
                    rd=np.full_like(hourofday,1)
                    rb=np.full_like(hourofday,1)
                    interval_rad=np.full_like(hourofday,1)
                    interval_diff=np.full_like(hourofday,1)
                    interval_beam=np.full_like(hourofday,1)
                    theta_z=np.full_like(hourofday,1)
                    theta_t=np.full_like(hourofday,1)
                    total_array=np.full_like(hourofday,1)
                    for i in range(len(hourofday)):

                        if(abs(hourofday[i]-12)*15 > abs(sunset_angle)):
                            hour_angle[i]=0
                        else:
                            hour_angle[i]=(hourofday[i]-12)*15

                        rt[i]=(math.pi/interval_length)*(a+b*np.cos(np.radians(hour_angle[i])))*((np.cos(np.radians(hour_angle[i])))-np.cos(np.radians(sunset_angle)))/(np.sin(np.radians(sunset_angle))-np.radians(sunset_angle)*np.cos(np.radians(sunset_angle)))
                        rd[i]=(math.pi/interval_length)*((np.cos(np.radians(hour_angle[i]))-np.cos(np.radians(sunset_angle)))/(np.sin(np.radians(sunset_angle))-np.radians(sunset_angle)*np.cos(np.radians(sunset_angle))))

                        if(hour_angle[i]==0 and hourofday[i]!=12):
                            interval_rad[i]=0
                            interval_diff[i]=0
                            theta_z[i]=0
                            theta_t[i]=0
                            rb[i]=0
                            interval_beam[i]=interval_rad[i]-interval_diff[i]
                            total_array[i]=0
                        else:
                            interval_rad[i]=global_irr[j]*rt[i]
                            interval_diff[i]=rd[i]*hd
                            theta_z[i]=np.degrees(np.arccos(np.sin(np.radians(declination_angle))*np.sin(np.radians(latitude))+np.cos(np.radians(declination_angle))*np.cos(np.radians(latitude))*np.cos(np.radians(hour_angle[i]))))
                            theta_t[i]=np.degrees(np.arccos(np.sin(np.radians(declination_angle))*np.sin(np.radians(latitude))*np.cos(np.radians(m))-np.sin(np.radians(declination_angle))*np.cos(np.radians(latitude))*np.sin(np.radians(m))*np.cos(np.radians(azimuth[k]))+np.cos(np.radians(declination_angle))*np.cos(np.radians(latitude))*np.cos(np.radians(m))*np.cos(np.radians(hour_angle[i]))+np.cos(np.radians(declination_angle))*np.sin(np.radians(latitude))*np.sin(np.radians(m))*np.cos(np.radians(azimuth[k]))*np.cos(np.radians(hour_angle[i]))+np.cos(np.radians(declination_angle))*np.sin(np.radians(m))*np.sin(np.radians(azimuth[k]))*np.sin(np.radians(hour_angle[i]))))
                            if(theta_t[i]>90):
                                rb[i]=0
                            else:
                                rb[i]=np.cos(np.radians(theta_t[i]))/np.cos(np.radians(theta_z[i]))
                            if(interval_diff[i]>interval_rad[i]):
                                interval_beam[i]=0
                                interval_diff[i]=interval_rad[i]
                            else:
                                interval_beam[i]=interval_rad[i]-interval_diff[i]
                            interval_beam[i]=interval_beam[i]*rb[i]
                            interval_diff[i]=interval_diff[i]*((1+np.cos(np.radians(m)))/2)
                            #total_array[i]=interval_beam[i]*rb[i]+interval_diff[i]*((1+np.cos(np.radians(tilt_angle)))/2)
                            total_array[i]=interval_beam[i]+interval_diff[i]

                    #Assigning to output
                    output2['Hour Angle']=hour_angle
                    output2['Daily extraterr']=np.round(h0,2)
                    output2['Daily diffuse radiation']=np.round(hd,2)
                    output2['Total radiation (kWh)']=np.round(interval_rad,4)
                    output2['Interval diffuse']=np.round(interval_diff,4)
                    output2['Interval beam']=np.round(interval_beam,4)
                    output2['cos(Theta Z)']=np.round(theta_z,2)
                    output2['cos(Theta T)']=np.round(theta_t,2)
                    output2['Total Array Radiation (kWh/m2/interval)']=np.round(total_array,4)
                    #output2['tilt']=tilt_angle
                    output=pd.concat([output,output2],ignore_index=True)
            #output
            #filename="output_tilt="+str(abs(m))+"_azimuth="+str(azimuth[k])+".xlsx"
            #output.to_excel(filename,index=False)
    return output