from playground.network.packet.fieldtypes import UINT16, STRING, BOOL
from playground.network.devices.vnic import connect
from playground.network.devices.vnic import VNIC
from playground.network.packet import PacketType
from playground.asyncio_lib.testing import TestLoopEx
from playground.network.testing import MockTransportToStorageStream
from playground.network.testing import MockTransportToProtocol 


import playground
import asyncio

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
		self.transport = transport
		self._deserializer = PacketType.Deserializer() #intialize Deserializer
							       

	def data_received(self, data):
		self._deserializer = PacketType.Deserializer()		
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

def basicUnitTest():
	
	
	loop= asyncio.get_event_loop()
	playground.getConnector().create_playground_server(lambda: EchoServerProtocol(), 8000)   
	playground.getConnector().create_playground_connection(lambda: EchoClientProtocol(), "20174.1.1.1", 8000) 	
	client = EchoClientProtocol()                           # Initialize Client Protocol
	server = EchoServerProtocol()                           # Initialize Server Protocol
	cTransport , sTransport = MockTransportToProtocol.CreateTransportPair(client,server)
	
	#transportToServer = MockTransportToProtocol(server)		
	#transportToClient = MockTransportToProtocol(client)
	packet1 = AccessResource()
	packet1Bytes = packet1.__serialize__()			
	server.connection_made(sTransport)
	client.connection_made(cTransport)
	server.data_received(packet1Bytes)        
	

if __name__=="__main__":
    basicUnitTest()
print("Basic Unit Test Successful.")
