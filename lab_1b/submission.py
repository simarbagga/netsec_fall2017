from playground.network.packet.fieldtypes import UINT16, STRING, BOOL
from playground.network.devices.vnic import connect
from playground.network.devices.vnic import VNIC
from playground.network.packet import PacketType
import playground

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


def basicTest():
	packet1 = AccessResource()
	packet1Bytes = packet1.__serialize__()
	packet1a = AccessResource.Deserialize(packet1Bytes)
	if packet1 == packet1a:
	   print("Packet 1 sent successfully!, Access Requested from Client to Server")

	packet2 = VerifyId()
	packet2.id = 5455
	packet2Bytes = packet2.__serialize__()
	packet2a = VerifyId.Deserialize(packet2Bytes)
	if packet2 == packet2a:
	   print("Packet 2 sent successfully!, Id Verification requested by sending an Id")

	packet3 = IdVerification()
	packet3.id= 5455
	packet3.idresponse= 2488
	packet3.passcode= "abc123"
	packet3Bytes = packet3.__serialize__()
	packet3a = IdVerification.Deserialize(packet3Bytes)
	if packet3 == packet3a:
           print("Packet 3 sent successfully!, Id Verification by sending the Id,IdResponse and a passcode ")

	packet4 = Access()
	packet4.id= 5455
	packet4.allowed= "true"
	packet4Bytes = packet4.__serialize__()
	packet4a = Access.Deserialize(packet4Bytes)
	if packet4 == packet4a:
	   print("Packet 4 sent successfully!, Access given by sending the id back along with the allowed=true... Woohoo")	

if __name__=="__main__":
	basicTest()






