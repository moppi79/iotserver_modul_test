import daemon, os, time, sys, signal, lockfile, socket, logging, datetime, json, random, configparser, fileinput

from multiprocessing import Process, Queue
from collections import defaultdict

from i2c_thread import thread_i2c, i2c_abruf
from gpio_thread import thread_gpio, gpio_abruf

import RPi.GPIO as GPIO

config = configparser.ConfigParser()
config.read('config.py')

ic_chip = {}

ram = {}
ram['Massage_counter'] = 0
ram['gpio'] = {}

sensor = {}

linee = ''	
with fileinput.input(files=('config_ic.py')) as f:
    for line in f:
        linee = linee + line 
        

exec(linee)



logger = logging.getLogger()
logger.setLevel(logging.ERROR)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
fh = logging.FileHandler(config['GLOBAL']['workingpath']+'/'+config['Slave_Basic']['logname'])
fh.setFormatter(formatter)
logger.addHandler(fh)




i2cswitch = {'adress':int(config['Slave_Basic']['switch_adress'],16),'port':int(config['Slave_Basic']['switch_port'])} #TI-PCA9548A
#i2cswitch = {'adress':0x70,'port':int(config['Slave_Basic']['switch_port'])} #TI-PCA9548A
ic_list = {'host':config['Slave_Basic']['Name'],'zone':config['Slave_Basic']['Zone'], 'switch':int(config['Slave_Basic']['switch'])} #anzahl I2C slaves mit adresse




iss = {}

class gpio:
	
	def __init__(self):# intiate interface and install all ports in server
		
		ram['bus_stack'] = {}
		ram['start_param'] = {}
		for x in ic_chip:
			if ic_chip[x]['bus'] in ram['bus_stack']:
				ram['bus_stack'][ic_chip[x]['bus']][ic_chip[x]['icname']] = ic_chip[x]
			else: 
				ram['bus_stack'][ic_chip[x]['bus']]= {}
				ram['bus_stack'][ic_chip[x]['bus']][ic_chip[x]['icname']] = ic_chip[x]
		

		print (ram['bus_stack'])
		
		for x in ram['bus_stack']:
			for y in ram['bus_stack'][x]:
				ram['bus_'+x] = {}
				#ram['bus_'+x]['queue_in'] =
				#ram['bus_'+x]['queue_out'] =
				call = {}
				exec("call['"+ x +"'] = "+ x +"_abruf()")
				install_data = call[x].install(ram['bus_stack'][x][y])
				print (install_data)
				for z in install_data:
					if z == 'ram':
						ram['bus_stack'][x][y]['ram'] = {}
						ram['bus_stack'][x][y]['ram'] = install_data['ram']
						
						
					else:
						self.data_to_iss(z,x,ram['bus_stack'][x][y]['icname'],install_data[z])

		data_standart = {}	
		data_iss = {}
		sensor_for = 0
		for x in sensor: #only runs on Sensor entrys 
			sensor_for = 1
			b = sensor[x]
			call = {}
			exec("call['"+ sensor[x]['bus'] +"'] = "+ sensor[x]['bus'] +"_abruf()")
			a = call[sensor[x]['bus']].sensor_install(b)
			if b['bus'] in data_standart:
				data_standart[sensor[x]['bus']][x] = {}
				data_standart[sensor[x]['bus']][x] = a[1]
			else:
				data_standart[sensor[x]['bus']] = {}
				data_standart[sensor[x]['bus']][x] = {}
				data_standart[sensor[x]['bus']][x] = a[1]
				
			ram['bus_stack'][sensor[x]['bus']]['sensor'] = {}
			data_iss[sensor[x]['bus']] = {}
			data_iss[sensor[x]['bus']] = a[2]
			ram['bus_stack'][sensor[x]['bus']]['sensor'][x] = sensor[x]

			ram['bus_stack'][sensor[x]['bus']]['sensor_update'] = {}
			
			for g in config['sensors']:
				#print (config['sensors'][x])
				ram['bus_stack'][sensor[x]['bus']]['sensor_update'][g] = ''
				ram['bus_stack'][sensor[x]['bus']]['sensor_update'][g] = config['sensors'][g]

		if sensor_for == 1: #sorting Sensor entrays
			for y in data_standart:
				for t in data_iss[y]:
					new_data = {}
					new_data = data_iss[y][t]
					new_data['data'] = {}
					new_data['data'] = data_standart[y]
					ram['bus_stack'][y]['data_standart'] = {}
					ram['bus_stack'][y]['data_standart'] = data_standart[y]
					print (new_data)
					self.data_to_iss(t,y,"sensor",new_data)
					
			#ram['bus_stack'][sensor[x]]['sensor_update'] = config['sensors']

		
		
		
		self.Prepare_start()# starting all threads
		
		
	def data_to_iss(self,iss_id,system,name,data):
		iss[iss_id] = {}
		iss[iss_id]['sender'] = {}
		iss[iss_id]['update'] = {}
		iss[iss_id]['data'] = {}
		
		iss[iss_id]['sender']['host'] = ic_list['host']
		iss[iss_id]['sender']['zone'] = ic_list['zone']
		iss[iss_id]['sender']['name'] = name
		iss[iss_id]['sender']['system'] = system
		
		iss[iss_id]['update'] = data['update']
		iss[iss_id]['data'] = data['data']
						
		ram['Massage_counter'] = ram['Massage_counter'] + 1
		
		
	
	def skirmish(self, length): #zufallsgenerator
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
	
	def Prepare_start(self):#prepare system and start new treahd
		for x in ram['bus_stack']:
			print ('HIER ########'+x+'#####################')
			self.start(x)


	def start(self,x):
		print ("start")
		print (x)
		ram['gpio'][x] = {}
		ram['gpio'][x]['name'] = x		#thread_run = thread_class()
		
		#install = plugin_class[ram['gpio'][name]['name']]
		config = {} #config data übertragen
		config['host'] = ic_list['host']
		config['zone'] = ic_list['zone']
		config['name'] = ram['gpio'][x]['name']
		ram['gpio'][x]['queue_in'] = Queue() # Queue erstellen iput from Plugin
		ram['gpio'][x]['queue_out'] = Queue() # Queue erstellen send data to Plugin 
		
		if x == "i2c":
			ram['gpio'][x]['prozess'] = Process(target=thread_i2c.run, name=ram['gpio'][x]['name'], args=(config, ram['bus_stack'][x], ram['gpio'][x]['queue_out'], ram['gpio'][x]['queue_in'],logger)) #prozess vorbereiten
		
		if x == "gpio":
			ram['gpio'][x]['prozess'] = Process(target=thread_gpio.run, name=ram['gpio'][x]['name'], args=(config, ram['bus_stack'][x], ram['gpio'][x]['queue_out'], ram['gpio'][x]['queue_in'],logger)) #prozess vorbereiten
		
		
		#ram['gpio'][x]['prozess'] = Process(target=,t.run, name=ram['gpio'][x]['name'], args=(config, ram['bus_stack'][x], ram['gpio'][x]['queue_out'], ram['gpio'][x]['queue_in'],logger)) #prozess vorbereiten
		#ram['gpio'][x]['prozess'] = Process(target=exec("thread_"+x+".run(config, ram['bus_stack'][x], ram['gpio'][x]['queue_out'], ram['gpio'][x]['queue_in'],logger)"), name=ram['gpio'][x]['name'], )
		ram['gpio'][x]['prozess'].start() # Prozzes starten

	
	def end (self):# kill all Threads and queue
		for x in ram['bus_stack']:
			logger.error('end Plugin:'+x)
			#ram['gpio'][x]['prozess'].join()
			ram['gpio'][x]['prozess'].terminate()
			ram['gpio'][x]['queue_in'].close
			ram['gpio'][x]['queue_out'].close
			


	def comparison(self): #Call Hardware
		
		shadow_copy = iss.copy()
		
		for x in shadow_copy: #is data in ISS to send hardware
			new_data = ''
			if 'target' in shadow_copy[x]:#Rufe alle verfügbaren Schnitstellen ab
				for y in ram['gpio']:
					
					#daten in thread hoch laden
					if (shadow_copy[x]['target']['host'] == ic_list['host']) and (shadow_copy[x]['target']['system'] == y):
						print ("ja hier daten")
						ram['gpio'][y]['queue_out'].put(iss[x])
						del iss[x]
						
		
		for y in ram['gpio']: #is new data from hardware to send server/plugins
			new_data = {}
			while ram['gpio'][y]['queue_in'].qsize() != 0:
				vari = self.skirmish(5)
				new_data[vari] = {}
				new_data[vari] = ram['gpio'][y]['queue_in'].get()
			if new_data != {}:
				for o in new_data:
					for z in new_data[o]:
						iss[z] = {}
						iss[z] = new_data[o][z]
						iss[z]['sender']['host'] = ic_list['host']
						iss[z]['sender']['zone'] = ic_list['zone']
						iss[z]['sender']['system'] = y

def fake_data():#set fake data to test modul 
	text = gpio.skirmish('',30)
	iss[text] = {}
	
	iss[text]['sender'] = {}
	iss[text]['sender']['host'] = 'faker'
	iss[text]['sender']['zone'] = 'just'
	iss[text]['sender']['name'] = 'tu was'
	iss[text]['sender']['system'] = 'faker'
	iss[text]['target'] = {}
	iss[text]['target']['host'] = 'Raspi2'
	iss[text]['target']['zone'] = 'balkon'
	iss[text]['target']['name'] = 'demomod'
	iss[text]['target']['system'] = 'gpio'
	iss[text]['data'] = {}
	iss[text]['data']['value'] = 0
	iss[text]['data']['id'] = 13
	iss[text]['data']['hz'] = 50


count = 1
gpio_handler = gpio()


while True:
	
	for x in ram['gpio']:
		if ram['gpio'][x]['prozess'].is_alive() != True:
			gpio_handler.start(x)
	
	
	print ('loop '+str(count))
	count = count + 1
	
	
	
	gpio_handler.comparison()
	zufall = random.randrange(1,3)
	#if (zufall == 6):
	print ('FAKE')
	fake_data()
	time.sleep(0.5)
	if count == 4:
		
		gpio_handler.comparison()
		gpio_handler.end()
		break

print ('############### RAM ###############')
print (ram)
print ('############### ISS ###############')
print (iss)
