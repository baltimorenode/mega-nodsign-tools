#!/usr/bin/python
"""
This is a reimplementation of the Pixelflut protocol
Pixel update commands are sent to the Arduino Mega on the sign
All other commands are handled locally in this script
"""

debug = True

import serial, socket # sys, time
from threading import Thread
from SocketServer import ThreadingMixIn

class PfServer(Thread):
	def __init__(self, ip, port, ser):
		Thread.__init__(self)

	def run(self):
		while True:
			data = conn.recv(256) #command from client
			if data == 'EXIT':
				conn.send("Thank you for playing")
				break #end thread
			if data == 'HELP':
				conn.send(self.Help())
			if data == 'SIZE':
				conn.send("SIZE " + self.Get_Size() + "\r\n")
			if data[0:2] == 'PX':
				vals = data.split(" ")
				print(vals)
				if len(vals) == 3: #try get
					row = int(vals[1])
					col = int(vals[2])
					if row >=1 and row <=24 and col >=1 and col <=48:
						print("get")
						conn.send("PX " + self.Get_Pixel(row, col)  + "\r\n")
				if len(vals) == 4: #try set
					row = vals[1]
					col = vals[2]
					color = vals[3] #need to add checks on color
					if row >=1 and row <=24 and col >=1 and col <=48:
						self.Set_Pixel(row, col, color)
			print data #local echo

	def Get_Pixel (self, row, col):
		""" To cut down on serial traffic use local frame buffer """
		return str(Frame_Buffer[row][col]) #need to remove "0x" and left pad 0s

	@classmethod
	def Get_Size (self):
		""" the nodesign has a size of 24x48 """
		return "24 48" #size of sign

	@classmethod
	def Help (self):
		""" helpfull message for the user """
		return "\t:SUPPORTED COMMANDS:\r\nHELP - returns this helpfull information\r\nSIZE - returns screen size (24 by 48)\r\nPX <x> <y> - get color value of pixel X,Y\r\nPX <x> <y> <rrggbb> - set color value of pixel X,Y\r\n(please note r g b max value is 16)\r\n"

	def Set_Pixel (self, row, col, color):
		""" send new pixel to sign then update local frame buffer """
		temp_LSB = int(color[1:1])
		temp_MSB = int(color[3:1]) *16 + int(color[5:])
		if debug:
			print(row, col, color)
		else:
			self.ser.write(chr(row))
			self.ser.write(chr(col))
			self.ser.write(chr(temp_MSB))
			self.ser.write(chr(temp_LSB))
		Frame_Buffer[row][col] = color

#global
Frame_Buffer = []
for y in range(24):
	temp = []
	for x in range(48):
		temp.append(hex(x + y))
	Frame_Buffer.append(temp)

ser_port = '/dev/ttyACM0' #default id for Arduino on Linux
baud_rate = 115200
try:
	print("Connecting to sign")
	if debug:
		nodesign = '/dev/null'
	else:
		nodesign = serial.Serial(ser_port, baud_rate)
except serial.SerialException:
	print("Unable to connect to sign")
	exit()

# Multithreaded Python server : TCP Server Socket Program Stub
TCP_IP = '0.0.0.0'
TCP_PORT = 1337
BUFFER_SIZE = 32  # Usually 1024, but we need quick response 

tcpServer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcpServer.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
tcpServer.bind((TCP_IP, TCP_PORT))
threads = []
 
while True: 
    tcpServer.listen(4)
    print "Multithreaded Python server : Waiting for connections from TCP clients..."
    (conn, (ip,port)) = tcpServer.accept()
    newthread = PfServer(ip,port, nodesign)
    newthread.start()
    threads.append(newthread)
 
for t in threads:
    t.join()
