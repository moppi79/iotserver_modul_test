import daemon, os, time, sys, signal, lockfile, socket, logging, datetime, json, random, configparser, fileinput
from multiprocessing import Process, Queue


ic_class = {}

iss = {}

glo_ram = {}

glo_ram['Massage_counter'] = 0

ic_chip = {}

sensordic = {}

class i2c_abruf:
	
	def sensor_install(self,ic):
		
		print('aaaaa')
		print(ic)
		print('aaaaa')
		sensor_class ={}
		
		print ('from sensors.'+ic['sensor_class']+' import '+ic['sensor_class']+'') 
		print ("sensor_class['"+ic['sensor_class']+"'] = "+ic['sensor_class']+"()")
		
		exec('from sensors.'+ic['sensor_class']+' import '+ic['sensor_class']+'') 
		exec("sensor_class['"+ic['sensor_class']+"'] = "+ic['sensor_class']+"()")
		
		data = sensor_class[ic['sensor_class']].install(ic)
		ret = {}
		for x in data:
			print ('aaabbbb')
			print (data[x])
			new_iss_number = skirmish(30)
			
			ret[new_iss_number] = {}
			ret[new_iss_number]['data'] = {}
			ret[new_iss_number]['data'][x] = {}
			ret[new_iss_number]['data'][x] = data[x]
			ret[new_iss_number]['data'][x]['usable'] = '0'
			ret[new_iss_number]['update'] = {}
			ret[new_iss_number]['update']['new'] = 1
		return (ret)
	
	def install(self,ic):
		ret = {}
		#for x in ic: #Dynamik Load classes
		exec('from module.'+ic['ic_class']+' import '+ic['ic_class']+'') 
		exec("ic_class['"+ic['ic_class']+"'] = "+ic['ic_class']+"()")
			
		#for x in ic: ##Declare all ic Dic (drivers own ram)

		
		#for x in ic:
		classcall = ic_class[ic['ic_class']]
			
		ret['ram'] = {}
		data_install = classcall.install(ic)
		ret['ram'] = data_install[0]
		#iot_ram['data']['i2c_'+str(x)] = ram[ic_chip[x]['icname']][x]['iot']
		
		#for y in ram[ic_chip[x]['icname']][x]['iss']: #create ISS update for gir 
		for y in data_install[1]: #create ISS update for gir 
			
			new_iss_number = skirmish(30)
			
			ret[new_iss_number] = {}
			ret[new_iss_number]['update'] = {}
			
			ret[new_iss_number]['update']['new'] = 1
			ret[new_iss_number]['data'] = {}
			ret[new_iss_number]['data'] = data_install[1][y]
			ret[new_iss_number]['data']['new'] = 1
			ret[new_iss_number]['counter'] = glo_ram['Massage_counter'] 
			
		
		return(ret)

				
				
	def icinit(self):
		for x in ic_chip: ##Declare all ic Dic
			ram[ic_chip[x]['icname']] = {}

		for x in ic_chip:
			classcall = ic_class[ic_chip[x]['ic_class']]
				
			ram[ic_chip[x]['icname']][x] = {}
			ram[ic_chip[x]['icname']][x].update(classcall.install(ic_chip[x]))
	
	def comparison(self,ram,data,logger):
		ret= {}
		ram[1]=2

		classcall = ic_class[ram['class']]
		
		data_return = classcall.comparison(ram['ram'],data,logger)
		glo_ram[ram['ic_name']]['ram'] = data_return[0]

		for y in data_return[1]:
			
			new_iss_number = skirmish(30)
			ret[new_iss_number] = {}
			ret[new_iss_number]['sender'] = {}
			ret[new_iss_number]['update'] = {}
			#ret[new_iss_number]['sender']['name'] = {}
			ret[new_iss_number]['sender']['name'] = ram['ic_name']
			
			ret[new_iss_number]['data'] = {}
			ret[new_iss_number]['data'] = data_return[1][y]
			ret[new_iss_number]['update']['new'] = 0
			
			ret[new_iss_number]['counter'] = glo_ram['Massage_counter'] 
			glo_ram['Massage_counter'] = glo_ram['Massage_counter'] + 1
			#logging.error(json.dumps(iss[new_iss_number]))
		#return sollte dann 1:1 in den jeweiligen RAM 
		#zurückspielbar sein 
		
		return(ret)
		
		'''
		iot Return in den stack 
		
		'''
			
def skirmish(length): #zufallsgenerator
	ausgabe = ''
	for x in range(0,length):
		#print (x)
		zufall = random.randrange(1,4)
	
		if (zufall == 1):
			ausgabe = ausgabe + str(random.randrange(0,10))
		if (zufall == 2):
			ausgabe = ausgabe + chr(random.randrange(65,91))
		if (zufall == 3):
			ausgabe = ausgabe + chr(random.randrange(97,123))
	return(ausgabe)			
			
class thread_i2c: #Thread 
	
	def run(system,chips,in_data,out_data,logger):
		sensor_ram = ''
		count = 1
		print (chips)
		if 'sensor' in chips:
			print (chips['sensor'])
			sensor_ram = {}
			sensor_ram = chips['sensor']
			sensor_conf = chips['sensor_update']
			print (chips['sensor_update'])
			del chips['sensor_update']
			
			del chips['sensor']
		
		print (sensor_ram)
		for x in chips: #intialisre Thread
			exec('from module.'+chips[x]['ic_class']+' import '+chips[x]['ic_class']+'') 
			exec("ic_class['"+chips[x]['ic_class']+"'] = "+chips[x]['ic_class']+"()")
			glo_ram[x] = {}
			glo_ram[x]['ram']  = chips[x]['ram']
			glo_ram[x]['class']  = chips[x]['ic_class']
			glo_ram[x]['ic_name']  = chips[x]['icname']
			glo_ram[x]['sensor_update']  = 2
			glo_ram[x]['sensor_update_time']  = 0
		call = i2c_abruf()
		
		chipname_list = {}
		for x in chips:
			
			chipname_list[x] = {}
			 
		testcount = 0
		while True: #Haupt schleife
			print ('date')
			timer = datetime.datetime.now()
			print (timer.second)
			####HIRT ERIZRT MACHEN !!!!
			print ('loop thread'+str(count))
			count = count + 1

			glo_ram['loop'] = chipname_list
			new_data = ''
			while in_data.qsize() != 0: #new data from Server/plugin
				vardd = skirmish(10)
				
				new_data = {}
				new_data[vardd] = {}
				new_data[vardd] = in_data.get()
			
			new_var = ''
			if new_data != '': #send data to Hardware
				shadow_copy = new_data.copy()
				for x in shadow_copy:
					new_var = call.comparison(glo_ram[new_data[x]['target']['name']],new_data[x],logger)
					out_data.put(new_var)
					if new_data[x]['target']['name'] in glo_ram['loop']:
						del glo_ram['loop'][new_data[x]['target']['name']]
					print('old delte')
					
			for x in glo_ram['loop']: #call Hardware to checkup
				testcount= testcount + 1
				new_var = call.comparison(glo_ram[x],'',logger)
				if new_var != {}:
					out_data.put(new_var)
			#print (new_var)
			#print(in_data.get())
			
			
			time.sleep(0.1)
			if count == 60:
				break
			
	