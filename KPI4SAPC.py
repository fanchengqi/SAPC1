#!/usr/bin/python

import sys
import os
import glob
import datetime
import xml.etree.ElementTree as ET

print "##########################################################"
print "            Welcom to SAPC KPI Management Tool            "
print "               (Last update: 2019-02-14)                  "
print "##########################################################"

pmf_xmlns='{http://www.3gpp.org/ftp/specs/archive/32_series/32.435#measCollec}'
measType_dict={}
pmfdata_TOC={}   #dictionary with Time/Group/Object/Counter
pmfdata_T={}   #dictionary with Time
pmfdata_T_Hourly={}   #dictionary with Time Hourly
pmfdata_O={}   #dictionary with Object
pmfdata_C={}   #dictionary with Counter
Gauge_measInfoId=["OSProcessingUnit", "policyControlFunctionCapacityMeasuresGroup"]

nowTime=datetime.datetime.now().strftime('%Y%m%d.%H%M')
fromTime='20181204.1630'
toTime='20181204.1645'

for filename in glob.glob('./*.xml'):        #'A20181204.1645+0800-1650+0800_1.xml'
    i=filename.rfind('\\')
    filename=filename[i+1:]
    beginTime = filename[1:14]
    beginTime_hourly = filename[1:12] + "00H"

    if beginTime>=fromTime and beginTime<=toTime:
        pmfdata_T[beginTime] = beginTime
        pmfdata_T_Hourly[beginTime_hourly] = beginTime_hourly
        print "Parsing %s ..." % filename
        tree = ET.parse(filename)
        root = tree.getroot()
        for measInfo in root.findall('./'+pmf_xmlns+'measData'+'/'+pmf_xmlns+'measInfo'):
            measInfoId=measInfo.get('measInfoId')
            for measType in measInfo.findall(pmf_xmlns+'measType'):
                measType_dict[measType.get('p')]=measType.text
                pmfdata_C[measType.text]=measType.text
            for measValue in measInfo.findall(pmf_xmlns + 'measValue'):
                measObjLdn=measValue.get('measObjLdn')
                pmfdata_O[measObjLdn]=measObjLdn
                for r in measValue.findall(pmf_xmlns + 'r'):
                    #Gauge counters
                    if measInfoId in Gauge_measInfoId:
                        #Granularity data
                        pmfdata_TOC[beginTime, measObjLdn, measType_dict[r.get('p')]] = \
                            int(r.text)
                        #Hourly data using the latest granularity
                        pmfdata_TOC[beginTime_hourly, measObjLdn, measType_dict[r.get('p')]] = \
                            int(r.text)
                        #No SYSTEM LEVEL data for Gauge counters
                        #########################################
                    #Peg counters
                    else:
                        #Granularity data
                        pmfdata_TOC[beginTime, measObjLdn, measType_dict[r.get('p')]] = \
                            int(r.text)
                        #Hourly data using the sum of granularity
                        if (beginTime_hourly, measObjLdn, measType_dict[r.get('p')]) in pmfdata_TOC:
                            pmfdata_TOC[beginTime_hourly, measObjLdn, measType_dict[r.get('p')]] \
                                += int(r.text)
                        else:
                            pmfdata_TOC[beginTime_hourly, measObjLdn, measType_dict[r.get('p')]] \
                                = int(r.text)
                        #SYSTEM LEVEL data using the sum of Obj
                        if(beginTime, "_SYSTEM_", measType_dict[r.get('p')]) in pmfdata_TOC:
                            pmfdata_TOC[beginTime, "_SYSTEM_", measType_dict[r.get('p')]] \
                                += int(r.text)
                        else:
                            pmfdata_TOC[beginTime, "_SYSTEM_", measType_dict[r.get('p')]] \
                                = int(r.text)
                        #Hourly SYSTEM LEVEL data using the sum of granularity and Obj
                        if(beginTime_hourly, "_SYSTEM_", measType_dict[r.get('p')]) in pmfdata_TOC:
                            pmfdata_TOC[beginTime_hourly, "_SYSTEM_", measType_dict[r.get('p')]] \
                                += int(r.text)
                        else:
                            pmfdata_TOC[beginTime_hourly, "_SYSTEM_", measType_dict[r.get('p')]] \
                                = int(r.text)

print pmfdata_TOC

