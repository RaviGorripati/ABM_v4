import numpy as np
#import xlrd
import csv
import matplotlib.pyplot as plt
#from scipy.interpolate import spline
import time


# Initial values
MIN_DEPTH=4	# minimum water vailable in well(feets)
water_depth=6
MAX_WATER_DEPTH=900 # If max water depth crossed stoped tube wells digging
AVG_DEPTH=70	# open well avg water depth
YIELD_PER_WELL = 2		# mm rainfall
#VILLAGE_AREA = 8000000	#2 x 4 km

NUM_SEASONS = 3		# every season contains 4 months(Kharif:Jul-OCt, Rabi:Nov-Feb,Summer: Mar-Jun )
NUM_MONTHS = 4		# no of months per season
#NUM_DAYS = 30
MM_TO_FEET = (0.1 / (2.54*12))
PERCOLATION =.40
PER_INC=1
POROSITY=.30
well_depth=0
#min_rainfall=10 #mm
#MAX_RAINY_DAYS=15

farmer_list=[]
crop_list=[]
wells_list=[]	#basic wells data(well_id,farmer_id,depth,lat,long,start date,end date,HP,well type)
s_rainfall=[]	#season rainfall
m_rainfall=[]	#monthly rainfall
ww_data_list=[]
c_data_years=[]
c_data_wells=[]

m_wells_water = []	#monthly wise wells water depth
no_working_well=[] #no of working wells
#no_dry_well=[] 		#no of not working wells
time_period = []	#time , year+month+day wise (year+(month/100)+(day/100))

TUBE_WELLS_TECH=1980
TOTAL_WELLS=76 #Initial well count
WWELL_PER=80	# to take decision for dig borewell or not

# Input data reading

with open('./chittoor1960-2002.csv') as rain:	# Rainfall data
    rain_reader = csv.DictReader(rain)
    for row in rain_reader:
        m_rainfall.append([row['State'],row['District'],int(row['Year']),float(row['Jan']),float(row['Feb']),float(row['Mar']),float(row['Apr']),float(row['May']),float(row['Jun']),float(row['Jul']),float(row['Aug']),float(row['Sep']),float(row['Oct']),float(row['Nov']),float(row['Dec'])])
        s_rainfall.append([int(row['Year']),float(row['Jul'])+float(row['Aug'])+float(row['Sep'])+float(row['Oct']),float(row['Nov'])+float(row['Dec'])+float(row['Jan'])+float(row['Feb']),float(row['Mar'])+float(row['Apr'])+float(row['May'])+float(row['Jun'])])
#print(m_rainfall)
START_YEAR=int(m_rainfall[0][2])	#start year in sheet
#print (START_YEAR)
END_YEAR= int(m_rainfall[len(m_rainfall)-1][2])	#end year in sheet
#print(END_YEAR)

with open('./well_data.csv') as wells:	# Existing wells data
    well_reader=csv.DictReader(wells)
    for row in well_reader:
        wells_list.append([row['well_id'],row['farmer_id'],row['depth'],row['lat'],row['long'],row['start_date'],row['end_date'],row['HP'],row['well_type'],row['Irr_extent'],row['State']])
#print ("wells list",wells_list[1][2])
"""with open('./crops.csv') as crop:		# Major crops info
	crop_reader=csv.DictReader(crop)
	for row in crop_reader:
		crop_list.append([row['Crop_id'],row['Crop_Name'],row['Profit'],row['Min_water'],row['Min_past_rainfall'],row['Crop_duration']])"""

with open('./farmers.csv') as farmer:	# Farmers info
    farmer_reader=csv.DictReader(farmer)
    for row in farmer_reader:
        farmer_list.append([row['Farmer_id'],row['Name'],row['Punchayat'],row['Hamlet'],row['Welth'],row['Type'],row['Extent']])
print("farmer list",farmer_list)
with open('./ww_count.csv') as wells_data:	# working wells data 5 years span wise
    well_reader=csv.DictReader(wells_data)
    for row in well_reader:
        ww_data_list.append([row['year'],row['ww_count']])

for r in ww_data_list:
    c_data_years.append(int(r[0]))
    c_data_wells.append(int(r[1]))

print("collected years")
print(c_data_years)
print("collected wells count")
print(c_data_wells)
y_working_wells=[] 	#Year wise working wells count
w_open_well=[]
w_tube_well=[]
years = []				#years for collecting year wise working wells

ww=0	#working wells count
dw=0	# dry wells count
wtw=0	# working tube wells
wow=0	#working open wells


def new_borewell(status,fi,ex,water_depth,wells,farmers):
    "Retun decidion of digging of new borewell"
    f_in=int(fi)
    water_depth=water_depth
    #print("fun",ex)
    ext=ex
    s=0
    #print("water depth",water_depth)
    if water_depth < MAX_WATER_DEPTH:	# Dig bore well when water not reached to high depth
        f_type=np.random.randint(1,4)	# farmer type
        money=np.random.randint(0,10)
        if status == 0:		# no water in existing well
            if money>5:
                s=1	#dig bore well and update wells list
            else:
                w=0
                if f_type==1:
                    s=1		#dig bore well and update list
                elif f_type==2:
                    s=0
                    ext=0	# no digging
                elif f_type==3:
                    for b in range(len(wells)):	# find working wells count
                        w=w+working_wells(b,water_depth,wells,farmers)
                    if (w/len(wells_list))*100 > WWELL_PER:	# 80 % and more wells working
                        s=1
                    else:
                        s=0
                        ext=0

        else:		# check unirrigated land availability and existing all wells status
            irri_land=0
            for zz in range(len(wells)):
                # print("--",wells_list[zz][1])
                fid= int(wells[zz][1])
                if fid == farmers[f_in][0]:
                    if int(wells[zz][10]) == 1:	# find total irrigiated farm of a particular farmer
                        irri_land=irri_land+int(wells[zz][9])
            print(f_in)
            print("irri_land",irri_land)
            print("total land",farmers[f_in][6])

            if irri_land < int(farmers[f_in][6]):
                unirri_land=int(farmers[f_in][6]) - irri_land
                if unirri_land > 4:
                    new_irri= np.random.randint(1,unirri_land)
                    s=1
                    ext=new_irri
                else:
                    new_irri=unirri_land
                    s=1
                    ext=new_irri
    else:
        s=0
        ext=0
    #print("---S",s)
    #print("extent---",ext)
    return s,ext


def working_wells(wi,water_depth,wells,farmers):
    "Return well status (working or not)"
    print("wi",wi)
    print("len",len(wells))
    """for c in range (len(wells)):
    	print(wells[c][:])"""
      	#print(wells[][])
    if int(wells[wi][10])==1: 	# check with end date for computing water utilization
        #print("hello")
        #w_id=int(wells_list[wi][0])
        well_depth=int(wells[wi][2]) # well depth
        dep=int(well_depth-water_depth)
        
        if dep > MIN_DEPTH:
            status=1		#working well which contains minimum water is 3 feet
        #print("inside")
        #print(ww)
        #working_wells.append([x,y]) #minimum depth of the water to say as working well: 3feet
        else:
            status=0
        #dw=dw+1		#dry wells
        #dry_wells.append([w_id,x,y])
    else:
        #update ded wells count
        status=0

    return status

def update_wells_list(temp,year,new_well_id,f_id,fex,wells,farmers):
    "update wells list with new borewell info"
    tp=[]
    tp=temp
    water= np.random.randint(0,10)
    if year > (TUBE_WELLS_TECH+10):
        depth=np.random.randint(400,900) #tube well depth between 400 to 900
    else:
        depth=np.random.randint(300,400)	#tube well depth between 300 to 400
    if water > 5:
        #wells_list[ex_well_id][10]=2	#update existing well statusas 2
        tp.append([new_well_id,f_id,depth,79.0726490329,13.5493944246,0,12/30/2050,7,1,fex,1])
    else:
        tp.append([new_well_id,f_id,depth,79.0726490329,13.5493944246,0,0,7,1,fex,0])	# failed borewell
    return tp


# simulate year+season-wise

for year in range(START_YEAR,END_YEAR+1, 1):
	print("wells count",len(wells_list))
	#year_rainfall=sum(m_rainfall[year])
	for season in range(1,NUM_SEASONS+1,1): 		# SEASONS: Kharif(July to Oct), Rabi(Nov to Feb), Summer(Mar to June)
		print(year)
		print(season)
		rainfall=int(s_rainfall[year - START_YEAR][season]) #reading season rainfall
		PERCOLATION = PERCOLATION*PER_INC	# percolation increment by 1 percent
		print("rainfall",rainfall)
		print("per",PERCOLATION)
		ww=0
		temp=[]
		if season == 1 or season == 2:
			for r in range(len(wells_list)):		#  Check wells status
				ww= ww + working_wells(r,water_depth,wells_list,farmer_list)
			print("ww",ww)
			water_depth = water_depth - (rainfall*MM_TO_FEET*PERCOLATION / POROSITY)	# Groundwater recharge due to rainfall
			if water_depth < 1:		# set minimum water depth is 3 feets
				water_depth=3
			water_depth = water_depth + ((ww*YIELD_PER_WELL)*MM_TO_FEET) / POROSITY	# Discharge due to utilization
			#update welth of farmers
			if year >= TUBE_WELLS_TECH:		#check tube well technology intoduced or not
				for f in range(len(farmer_list)):		#  Check farmer wells status
					wid=0
					all=1	#all wells are working
					for w in range(len(wells_list)):
						if wells_list[w][1]==farmer_list[f][0]:
							wid=wid+1
							status=int(working_wells(w,water_depth,wells_list,farmer_list))
							#print("f_id",wells_list[w][1])
							if status==0:	# well has no water
								all=0
								# print("wells_list[w][9]",wells_list[w][9])
								nb, extent_1 =new_borewell(status,f,wells_list[w][9],water_depth,wells_list,farmer_list) # sending status, farmer id, extent
								print("nb1",nb)
								print("extent1",extent_1)
								if nb==1:
									nbid=str(f)+'0'+str(wid)
									"""print("nb1",nb)
									for i in range(100):	#generate unique well id
										t=1
										nbid=np.random.randint(100,1000)
										for j in range(len(wells_list)):
											if nbid==wells_list[j][0]:
												t=0
												break
											if t==1:
											i=100"""
									print("nbid",nbid)
									temp=update_wells_list(temp,year,nbid,int(wells_list[w][1]),extent_1,wells_list,farmer_list)#sending new well id, farmer id, extent

					if all ==1:
						if np.random.randint(0,2)==1:	# His well is working but thinking to new borewell for unirrigated land
							nb,extent_2=new_borewell(status,f,int(wells_list[w][9]),water_depth,wells_list,farmer_list)
							if nb==1:
								nbid=str(f)+'0'+str(wid)
								temp=update_wells_list(temp,year,nbid,int(wells_list[w][1]),extent_2,wells_list,farmer_list)

			if len(temp)!=0:
				#print("wells",wells_list)
				#print("temp",temp)
				for t in range(len(temp)):
					#print("temp",temp)
					wells_list.append(temp[t])
				#print("xxxx",wells_list)
		elif season == 3:
			for z in range(len(wells_list)):		#  Check wells status
				t= working_wells(z,water_depth,wells_list,farmer_list)
				ww=ww+t
			water_depth = water_depth - (rainfall*MM_TO_FEET*PERCOLATION / POROSITY)	# Groundwater recharge due to rainfall
			if water_depth < 1:		# set minimum water depth is 3 feets
				water_depth=3
			water_depth = water_depth + ((ww*0.4*YIELD_PER_WELL)*MM_TO_FEET / POROSITY)	# Discharge due to utilization
			y_working_wells.append(ww)
			#print(ww)
			years.append(year)

print(years)
print(y_working_wells)
#print("no of working well")
#print(no_working_well)
z=0
wc=[]
yy=[]
for a in range(1960,2002):
    if a%5==0:
        wc.append(y_working_wells[z])
    z=z+1
wc.append(y_working_wells[z])
print("wc",wc)
w_wells=np.asarray(wc)
years_x=np.asarray(years)

g=plt.figure("working_wells")
plt.xlabel("Years")
plt.ylabel("no_working wells")
plt.plot(c_data_years,w_wells, label='Simulation')
plt.plot(c_data_years,c_data_wells, label='Collected' )
plt.legend()
plt.savefig("working_wells")
g.show()
plt.show()

			