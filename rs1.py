import sys

from jaraco.nxt import messages, Connection
from jaraco.nxt.messages import SetOutputState, RunState
from jaraco.nxt import _enum as enum
from jaraco.nxt.routine import *
import time


version = "0.0.1"


def run():
	"""runs the bot"""

	dev = Connection("COM4") # whichever connection the bot is on, can change

	# read the values from this port
	port1 = enum.InputPort(1)
	port3 = enum.InputPort(3)
	#port = get_port(3)

	# configure the input mode
	dev.send(messages.SetInputMode(
		port1,
		messages.SensorType.light_active,
		messages.SensorMode.boolean))

	dev.send(messages.SetInputMode(
		port3,
		messages.SensorType.light_active,
		messages.SensorMode.boolean))

	# print out the field names once
	#print(', '.join(field[:4] for field in messages.InputValues.fields))
	#print(messages.InputValues.fields[9])

	green_1 = calibrate(dev, "green", port1)
	green_3 = calibrate(dev, "green", port3)
	gray_1 = calibrate(dev, "gray", port1)
	gray_3 = calibrate(dev, "gray", port3)
	blue_1 = calibrate(dev, "blue", port1)
	blue_3 = calibrate(dev, "blue", port3)

	print "green_1 = " + str(green_1)
	print "green_3 = " + str(green_3)
	print "gray_1 = " + str(gray_1)
	print "gray_3 = " + str(gray_3)
	print "blue_1 = " + str(blue_1)
	print "blue_3 = " + str(blue_3)

	forward(dev)

	try:
		while True: # continuously query port status, output values
			sys.stdout.write('\r')
			port1_status = query_status(dev, port1) - 35
			port3_status = query_status(dev, port3) - 35

			if port3_status <= blue_3 and port1_status <= blue_1: # if both sensors read blue, brake.
				sys.stdout.write('port 3: '+str(port3_status))
				sys.stdout.write('  brake  ')
				sys.stdout.write('port 1: '+str(port1_status))
				brake(dev)
		#	else:
		#		pass

			elif port1_status < gray_1: # if righthand port reads "green":

				if port3_status < gray_3:  # if lefthand reads "green" too, forward
					sys.stdout.write('port 3: '+str(port3_status))
					sys.stdout.write(' forward ')
					sys.stdout.write('port 1: '+str(port1_status))
					forward(dev)

				else:	# otherwise, turn right
					sys.stdout.write('port 3: '+str(port3_status))
					sys.stdout.write('  right  ')
					sys.stdout.write('port 1: '+str(port1_status))
					turn_right(dev)

			elif port1_status > green_1: # if righthand port reads "gray":

				if (port3_status < gray_3): # if lefthand port is "green," turn left
					sys.stdout.write('port 3: '+str(port3_status))
					sys.stdout.write('   left  ')
					sys.stdout.write('port 1: '+str(port1_status))
					turn_left(dev)

				else: # if both are gray, reverse?
					sys.stdout.write('port 3: '+str(port3_status))
					sys.stdout.write(' reverse ')
					sys.stdout.write('port 1: '+str(port1_status))
					back_it_up(dev)

		#	if (port1_status > 500 & port3_status < 500):
				# if righthand sensor reads lower, turn left
		#		sys.stdout.write('3'+str(port3_status))
		#		sys.stdout.write('   left  ')
		#		sys.stdout.write('1'+str(port1_status))
		#		turn_left(dev)

		#	elif (port1_status < 500 & port3_status > 500):
				# if lefthand sensor reads lower, turn right
		#		sys.stdout.write(str(port3_status))
		#		sys.stdout.write('  right  ')
		#		sys.stdout.write(str(port1_status))
		#		turn_right(dev)

		#	elif (port1_status < 500) & (port3_status < 500):
		#		sys.stdout.write(str(port3_status))
		#		sys.stdout.write(' forward ')
		#		sys.stdout.write(str(port1_status))
		#		forward(dev)



	except KeyboardInterrupt:
		sys.stdout.write('\n')


def query_status(dev, port):
	"""
	Send the GetInputValues message, then process the
	jaraco.nxt.messages.InputValues reply, printing each
	of the fields in a CSV format.
	"""

	# query for the input values and re-write the line
	dev.send(messages.GetInputValues(port))
	#dev.send2(messages.GetInputValues(port2))
	input_res = dev.receive()
	# print each of the fields
	#values = ', '.join('%4d' % getattr(input_res, field) for field in input_res.fields)
	values = int(getattr(input_res, input_res.fields[9]))
	# carriage return but no line feed so we write over the previous line
	#sys.stdout.write('\r')
	#sys.stdout.write(values)
	return values


def turn_left(conn):

	"""Turn the motor one direction, then the other, then stop it"""

	port_b = get_port('b', OutputPort)   # assign names to ports
	port_c = get_port('c', OutputPort)

	cmd_b = SetOutputState(port_b, motor_on=True, set_power=90, run_state=RunState.running)
	# send slightly more power to port_b to turn left
	cmd_c = SetOutputState(port_c, motor_on=True, set_power=70, run_state=RunState.running)

	conn.send(cmd_b)
	conn.send(cmd_c)

	# brake
	cmd = SetOutputState(port_b)
	conn.send(cmd)
	cmd = SetOutputState(port_c)
	conn.send(cmd)


def turn_right(conn):

	"""Turn the motor one direction, then the other, then stop it"""

	port_b = get_port('b', OutputPort)	# assign names to ports
	port_c = get_port('c', OutputPort)

	cmd_b = SetOutputState(port_b, motor_on=True, set_power=70, run_state=RunState.running)
	# send slightly more power to port_c to turn right
	cmd_c = SetOutputState(port_c, motor_on=True, set_power=90, run_state=RunState.running)

	conn.send(cmd_b)
	conn.send(cmd_c)

	# brake
	cmd = SetOutputState(port_b)
	conn.send(cmd)
	cmd = SetOutputState(port_c)
	conn.send(cmd)


def forward(conn):
	"""turns both motors, theoretically sending th bot forward"""

	port_b = get_port('b', OutputPort)
	port_c = get_port('c', OutputPort)

	cmd_b = SetOutputState(port_b, motor_on=True, set_power=90, run_state=RunState.running)
	cmd_c = SetOutputState(port_c, motor_on=True, set_power=90, run_state=RunState.running)

	conn.send(cmd_b)
	conn.send(cmd_c)

	cmd = SetOutputState(port_b)
	conn.send(cmd)
	cmd = SetOutputState(port_c)
	conn.send(cmd)


def back_it_up(conn):
	"""reverses the bot, apparantly overshot the line"""

	port_b = get_port('b', OutputPort)
	port_c = get_port('c', OutputPort)

	cmd_b = SetOutputState(port_b, motor_on=True, set_power=-80, run_state=RunState.running)
	cmd_c = SetOutputState(port_c, motor_on=True, set_power=-80, run_state=RunState.running)

	conn.send(cmd_b)
	conn.send(cmd_c)

	cmd = SetOutputState(port_b)
	conn.send(cmd)
	cmd = SetOutputState(port_c)
	conn.send(cmd)


def brake(conn):
	"""brakes both motors"""

	port_b = get_port('b', OutputPort)
	port_c = get_port('c', OutputPort)

	cmd_b = SetOutputState(port_b,motor_on=False,set_power=0,use_brake=True)
	cmd_c = SetOutputState(port_c,motor_on=False,set_power=0,use_brake=True)

	conn.send(cmd_b)
	conn.send(cmd_c)


def calibrate(conn, color, port):
	print "place on " + str(color)
	time.sleep(3)
	print "calibrating"

	reading_sum = 0


	for i in range(9):
		time.sleep(.25)
		reading_sum += query_status(conn, port)

	reading_avg = reading_sum/10

	print str(color) + " calibrated for port " + str(port)

	return reading_avg

__name__ == '__main__' and run()
