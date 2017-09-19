from playground.network.packet.fieldtypes import UINT16, STRING, BOOL
from playground.network.devices.vnic import connect
from playground.network.devices.vnic import VNIC
from playground.network.packet import PacketType
from playground.asyncio_lib.testing import TestLoopEx
from playground.network.testing import MockTransportToStorageStream
from playground.network.testing import MockTransportToProtocol 
from playground.network.common import PlaygroundAddress , StackingProtocol, StackingTransport, StackingProtocolFactory

import playground
import asyncio
import sys , time , os ,logging 

class AccessResource(PacketType):
	
	DEFINITION_IDENTIFIER = "lab1b.student_harsimar.AccessResource"
	DEFINITION_VERSION = "1.0"
	FIELDS = [
		  ]

class VerifyId(PacketType):

	DEFINITION_IDENTIFIER = "lab1b.student_harsimar.VerifyId"
	DEFINITION_VERSION = "1.0"
	FIELDS = [
		 ("id", UINT16)
		 ]

class IdVerification(PacketType):

	DEFINITION_IDENTIFIER = "lab1b.student_harsimar.IdVerification"
	DEFINITION_VERSION = "1.0"
	FIELDS = [
		 ("id", UINT16),
		 ("idresponse", UINT16),
		 ("passcode", STRING)	 
		 ]

class Access(PacketType):

	DEFINITION_IDENTIFIER = "lab1b.student_harsimar.Access"
	DEFINITION_VERSION = "1.0"
	FIELDS = [
		 ("id", UINT16),
		 ("allowed", BOOL)			
		 ]

class EchoClientProtocol(asyncio.Protocol):
	
	def __init__(self):
		print("Client started")		
		self.transport = None    #Set transport to None
	
	def connection_made(self,transport):
		self.transport = transport
		self._deserializer = PacketType.Deserializer() #initialize Deserializer
		packet1 = AccessResource()
		packet1Bytes = packet1.__serialize__()
		self.transport.write(packet1Bytes)
		

	def data_received(self, data):
		self._deserializer = PacketType.Deserializer()		
		self._deserializer.update(data)
		for pkt in self._deserializer.nextPackets():
			print("Client Received = ",pkt)
			if isinstance(pkt,VerifyId): # Checking if the packet is VerifyId
				print("Packet Id received =",pkt.id)				
				print("Sending ID response and passcode back to the server for verification")				
				packet3= IdVerification()
				packet3.id = 5455
				packet3.idresponse = 2488
				packet3.passcode = "abc123"
				packet3Bytes = packet3.__serialize__()
				self.transport.write(packet3Bytes)
			elif isinstance(pkt,Access): # Checking if the packed is Access
				if pkt.allowed == True: # Checking if the allowed attribute is set to True or not.
					print("Got Access.")
					self.connection_lost()
				else :
					print("Access denied due to wrong passcode.")
					self.connection_lost()
			
	def connection_lost(self):
		self.transport = None
		print("Connection Terminated") 

class EchoServerProtocol(asyncio.Protocol):

	def __init__(self):
		print("Server connected to Client")		
		self.transport = None
	
	def connection_made(self,transport):
		print("Received a connection from {}".format(transport.get_extra_info("peername")))		
		self.transport = transport
		self._deserializer = PacketType.Deserializer() #intialize Deserializer
							       

	def data_received(self, data):
		#self._deserializer = PacketType.Deserializer()		
		self._deserializer.update(data)
		for pkt in self._deserializer.nextPackets():
			print("Server Received = ",pkt)
			if isinstance(pkt,AccessResource): # Checking if the packet is AccessResource
				print("Server received request to Access Resource. Generating and Sending an ID back ")  				
				packet2 = VerifyId()					        
				packet2.id = 5455
				packet2Bytes= packet2.__serialize__()
				self.transport.write(packet2Bytes) 
								
			elif isinstance(pkt,IdVerification): # Checking if the packet is IdVerification
				if hasattr(pkt,str("idresponse")): 
					print("Id = ",pkt.id)					
					print("Id Response = ",pkt.idresponse)					
					if hasattr(pkt,str("passcode")) :
						if pkt.passcode == "abc123" :	# If passcode matched , set allowed to True or else, set to False					
							print("Passcode accepted and Authenticity Verified")
							packet4 = Access()
							packet4.id= 5455
							packet4.allowed = True
							packet4Bytes= packet4.__serialize__()
							self.transport.write(packet4Bytes)
						else : 
							print("Passcode wrong. Access Denied.")
							packet4 = Access()
							packet4.id = 5455
							packet4.allowed = False
							packet4Bytes= packet4.__serialize__()
							self.transport.write(packet4Bytes)		

	def connection_lost(self,exc):
		self.transport = None 
class EchoControl:

	"""def __init__(self):
		self.txProtocol = None
		self.transport = None"""

	def buildProtocol(self):
		return EchoClientProtocol()

	"""def connect(self, txProtocol):
		self.transport = transport		
		self.txProtocol = txProtocol
		print("Connection to Server Established!")
		self.txProtocol = txProtocol
		packet1 = AccessResource()
		packet1Bytes = packet1.__serialize__()
		#higherTransport = StackingTransport(self.transport)
		a = PassThrough1()
		a.connection_made(self.transport)
		#a.data_received(self.packet1Bytes)		
		#higherTransport.write(packet1Bytes)		
				
		self.transport.write(packet1Bytes)"""

        	#asyncio.get_event_loop().add_reader(sys.stdin, self.stdinAlert)
        
    #def callback(self, message):
    #    print("Server Response: {}".format(message))
    #    sys.stdout.write("\nEnter Message: ")
    #    sys.stdout.flush()
        
    #def stdinAlert(self):
    #    data = sys.stdin.readline()
    #    if data and data[-1] == "\n":
    #        data = data[:-1] # strip off \n
    #    self.txProtocol.send(data)

class PassThrough1(StackingProtocol):

	def __init__(self):
		self.transport=None
		super().__init__

	def connection_made(self, transport):
		print("Pass through 1 : Connection made called")
		self.transport =transport
		#higherTransport = StackingTransport(transport)		
		self.higherProtocol().connection_made(self.transport)		
		#self._deserializer = PacketType.Deserializer()

	def data_received(self , data):
		#self._deserializer = PacketType.Deserializer()
		print("Pass through 1 : Data Received called")		
		#self._deserializer.update(data)
				
		self.higherProtocol().data_received(data)		
			
	

	def connection_lost(self):
		print("PassThrough 1 connection lost")
		self.transport = None
		

class PassThrough2(StackingProtocol):

	def __init__(self):
		self.transport=None
		super().__init__

	def connection_made(self, transport):
		print("Pass through 2: Connection made called")
		self.transport =transport
		#higherTransport = StackingTransport(transport)
		self.higherProtocol().connection_made(self.transport)		
		

	def data_received(self , data):
		print("Pass through 2 : Data received called")
		self.higherProtocol().data_received(data)

	def connection_lost(self):
		print("PassThrough 2 connection lost")		
		self.transport = None

	
		


#def stdInCallback():
#	choice = input("Enter input: ")
#	return choice

if __name__=="__main__":
    
	echoArgs = {}
	args=sys.argv[1:]
	i=0
	for arg in args:
		if arg.startswith("-"):
			k,v =arg.split("=")
			echoArgs[k]=v
		else:
			echoArgs[i]= arg
			i+=1

	if not 0 in echoArgs:
		sys.exit(USAGE)

	mode = echoArgs[0]
	
	f = StackingProtocolFactory(lambda: PassThrough1(), lambda : PassThrough2())
	loop = asyncio.get_event_loop()
	loop.set_debug(enabled=True)
	ptConnector = playground.Connector(protocolStack = f)
	playground.setConnector("passthrough",ptConnector)

	if mode.lower() == "server" :
		coro= playground.getConnector("passthrough").create_playground_server(lambda: EchoServerProtocol(),101)
		servers = loop.run_until_complete(coro)
		print("Server Started at {}".format(servers.sockets[0].gethostname()))
		print("Waiting for Client to start Interaction!! ")		
		loop.run_forever()
		loop.close()

	else:
		playAddress = mode
		control = EchoControl()
		coro= playground.getConnector("passthrough").create_playground_connection(control.buildProtocol , playAddress , 101)
		transport, protocol = loop.run_until_complete(coro)
		print("Echo Client Connected. Starting UI t:{}. p:{}".format(transport , protocol))
		loop.run_forever()		
		print("Interaction Successful")		
		loop.close()
