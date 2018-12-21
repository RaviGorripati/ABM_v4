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
YIELD_PER_WELL = 0.4		# mm rainfall
#VILLAGE_AREA = 8000000	#2 x 4 km
#START_YEAR = 1960
#END_YEAR = 2002
NUM_SEASONS = 3		# every season contains 4 months(Kharif:Jul-OCt, Rabi:Nov-Feb,Summer: Mar-Jun )
NUM_MONTHS = 4		# no of months per season
#NUM_DAYS = 30
MM_TO_FEET = (0.1 / (2.54*12))
PERCOLATION =.40
PER_INC=0.1
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
#d_wells_water = []	#day wise wells water depth

no_working_well=[] #no of working wells
#no_dry_well=[] 		#no of not working wells
time_period = []	#time , year+month+day wise (year+(month/100)+(day/100))

TUBE_WELLS_TECH=1980
TOTAL_WELLS=76 #Initial well count
WWELL_PER=70	# to take decision for dig borewell or not

# Input data reading

with open('./chittoor1960-2002.csv') as rain:	# Rainfall data
	rain_reader = csv.DictReader(rain)
	for row in rain_reader:
		m_rainfall.append([row['State'],row['District'],int(row['Year']),float(row['Jan']),float(row['Feb']),float(row['Mar']),float(row['Apr']),float(row['May']),float(row['Jun']),float(row['Jul']),float(row['Aug']),float(row['Sep']),float(row['Oct']),float(row['Nov']),float(row['Dec'])])
		s_rainfall.append([int(row['Year']),float(row['Jul'])+float(row['Aug'])+float(row['Sep'])+float(row['Oct']),float(row['Nov'])+float(row['Dec'])+float(row['Jan'])+float(row['Feb']),float(row['Mar'])+float(row['Apr'])+float(row['May'])+float(row['Jun'])])
#print(row['first_name'], row['last_name'])
#print(m_rainfall)
START_YEAR=1960			#int(m_rainfall[0][2])	#start year in sheet
#print (START_YEAR)
END_YEAR= int(m_rainfall[len(m_rainfall)-1][2])	#end year in sheet
#print(END_YEAR)
#print(m_rainfall)
#print(s_rainfall)
with open('./well_data.csv') as wells:	# Existing wells data
	well_reader=csv.DictReader(wells)
	for row in well_reader:
		wells_list.append([row['well_id'],row['farmer_id'],row['depth'],row['lat'],row['long'],row['start_date'],row['end_date'],row['HP'],row['well_type'],row['Irr_extent'],row['State']])
	#print ("wells list",wells_list)
"""with open('./crops.csv') as crop:		# Major crops info
	crop_reader=csv.DictReader(crop)
	for row in crop_reader:
		crop_list.append([row['Crop_id'],row['Crop_Name'],row['Profit'],row['Min_water'],row['Min_past_rainfall'],row['Crop_duration']])"""

with open('./farmers.csv') as farmer:	# Farmers info
	farmer_reader=csv.DictReader(farmer)
	for row in farmer_reader:
		farmer_list.append([row['Farmer_id'],row['Name'],row['Punchayat'],row['Hamlet'],row['Welth'],row['Type'],row['Extent']])

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


def new_borewell(year,status,farmer_id,extent,water_depth):
	"Retun decidion of digging of new borewell"
	f_id=int(farmer_id)
	water_depth=int(water_depth)
	extent=int(extent)
	s=0
	tp=[]
	#print("water depth",water_depth)
	if water_depth < MAX_WATER_DEPTH:	# Dig bore well when water not reached to high depth
		f_type=np.random.randint(1,4)	# farmer type
		money=np.random.randint(0,2)
		if status == 0:		# no water in existing well
			if money==1:
				s=1	#dig bore well and update wells list
			else:
				w=0
				if f_type==1:
					s=1		#dig bore well and update list
				elif f_type==2:
					s=0
					extent=0	# no digging 
				elif f_type==3:
					for b in range(len(wells_list)):	# find working wells count
						w=w+working_wells(b,water_depth)
					if (w/len(wells_list))*100 > WWELL_PER:	# 70 % and more wells working
						s=1
					else:
						s=0
						extent=0

		else:		# check unirrigated land availability and existing all wells status 
			irri_land=0
			for zz in range(len(wells_list)):
				if int(wells_list[zz][1])==int(f_id):
					if int(wells_list[zz][10]) == 1:	# find total irrigiated farm of a particular farmer
						irri_land=irri_land+int(wells_list[zz][9])
			#print(f_id)
			#print("irri_land",irri_land)
			#print("total land",farmer_list[f_id][6])

			if irri_land < int(farmer_list[f_id][6]):
				unirri_land=int(farmer_list[f_id][6]) - irri_land
				if unirri_land > 4:
					new_irri= np.random.randint(1,unirri_land)
					s=1
					extent=new_irri
				else:
					new_irri=unirri_land
					s=1
					extent=new_irri
	else:
		s=0
		extent=0

	water= np.random.randint(0,2)	# water or no water
	if year > (TUBE_WELLS_TECH+10):
		depth=np.random.randint(400,900) #tube well depth between 400 to 900
	else:
		depth=np.random.randint(300,400)	#tube well depth between 300 to 400
	if water > 0:
		#wells_list[ex_well_id][10]=2	#update existing well statusas 2
		tp.append([len(wells_list),f_id,depth,79.0726490329,13.5493944246,0,12/30/2050,7,extent,1])
		#update_wells_list(temp,year,w,len(wells_list),int(wells_list[w][1]),extent)
	else:
		tp.append([len(wells_list),f_id,depth,79.0726490329,13.5493944246,0,0,7,extent,0])	# failed borewell

	#print("S",s)
	#print("extent",extent)
	return tp
						

def working_wells(wi,water_depth):
	"Return well status (working or not)"
	if int(wells_list[wi][10])==1: 	# check well is working or not computing water utilization
		#print("hello")
		well_depth=int(wells_list[wi][2]) # well depth
		dep=well_depth-water_depth
		#print("dep",dep)
		if dep > MIN_DEPTH:
			status=1		#working well which contains minimum water is 3 feet
		else:
			status=0
	else:
		status=0
		#update ded wells count
	return status

def update_wells_list(temp,year,ex_well_id,new_well_id,f_id,extent):
	"update wells list with new borewell info"
	tp=[]
	tp=temp
	water= np.random.randint(0,2)
	if year > (TUBE_WELLS_TECH+10):
		depth=np.random.randint(400,900) #tube well depth between 400 to 900
	else:
		depth=np.random.randint(300,400)	#tube well depth between 300 to 400
	if water > 0:
		#wells_list[ex_well_id][10]=2	#update existing well statusas 2
		tp.append([new_well_id,f_id,depth,79.0726490329,13.5493944246,0,12/30/2050,7,extent,1])
	else:
		tp.append([new_well_id,f_id,depth,79.0726490329,13.5493944246,0,0,7,extent,0])	# failed borewell
	return tp


# simulate year+season-wise

for year in range(START_YEAR,END_YEAR+1, 1):
	#year_rainfall=sum(m_rainfall[year])
	for season in range(1,NUM_SEASONS+1,1): 		# SEASONS: Kharif(July to Oct), Rabi(Nov to Feb), Summer(Mar to June)
		rainfall=int(s_rainfall[year - START_YEAR][season]) #reading season rainfall 
		PERCOLATION = PERCOLATION*PER_INC	# percolation increment by 1 percent
		ww=0
		temp=[]
		if season == 1 or season == 2:
			for r in range(len(wells_list)):		#  Check wells status
				ww= ww+working_wells(r,water_depth)
				#print("ww",ww)		
			water_depth = water_depth - (rainfall*MM_TO_FEET*PERCOLATION / POROSITY)	# Groundwater recharge due to rainfall
			if water_depth < 1:		# set minimum water depth is 3 feets
				water_depth=3
			water_depth = water_depth + ((ww*YIELD_PER_WELL)*MM_TO_FEET) / POROSITY	# Discharge due to utilization
			#update welth of farmers
			if year >= TUBE_WELLS_TECH:		#check tube well technology intoduced or not
				for w in range(len(wells_list)):		#  Check wells status
					status=int(working_wells(w,water_depth))
					#print("f_id",wells_list[w][1])
					if status==0:	# well has no water
						temp.append(new_borewell(year,status,int(wells_list[w][1]),int(wells_list[w][9]),water_depth)) # sending status, farmer id, extent
						#print("nb1",nb)
						#print("extent1",extent)
						#if nb==1:
						#temp=update_wells_list(temp,year,w,len(wells_list),int(wells_list[w][1]),extent)	#sending new well id, farmer id, extent
					elif np.random.randint(0,2)==1:	# His well is working but thinking to new borewell for unirrigated land
						temp.append(new_borewell(year,status,int(wells_list[w][1]),int(wells_list[w][9]),water_depth))
						#print("nb2",nb)
						#print("extent2",extent)
						#if nb==1:
						#temp=update_wells_list(temp,year,w,len(wells_list),int(wells_list[w][1]),extent)
			if len(temp)!=0:
				wells_list.append(temp)
		elif season == 3:
			for z in range(len(wells_list)):		#  Check wells status
				t= working_wells(z,water_depth)
				ww=ww+t		
			water_depth = water_depth - (rainfall*MM_TO_FEET*PERCOLATION / POROSITY)	# Groundwater recharge due to rainfall
			if water_depth < 1:		# set minimum water depth is 3 feets
				water_depth=3
			water_depth = water_depth + ((ww*0.3*YIELD_PER_WELL)*MM_TO_FEET / POROSITY)	# Discharge due to utilization
			y_working_wells.append(ww)
			#print(ww)
			years.append(year)



	

	
	#w_open_well.append(wow)
	#w_tube_well.append(wtw)

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

#wells_data=np.asarray(ww_data_list)
#no_working_wells=np.asarray(no_working_well)
#no_dry_wells = np.asarray(no_dry_well)
#time_periods=np.asarray(time_period)
#syear_working_wells=np.asarray(y_working_wells)
years_x=np.asarray(years)
#w_open_wells=np.asarray(w_open_well)
#w_tube_wells=np.asarray(w_tube_well)



g=plt.figure("working_wells")
#plt.ylim(0,400)
plt.xlabel("Years")
plt.ylabel("no_working wells")
plt.plot(c_data_years,w_wells, label='Simulation')
plt.plot(c_data_years,c_data_wells, label='Collected' )
plt.legend()
plt.savefig("working_wells")
g.show()
plt.show()



			