import logging
import asyncio
import sys
sys.path.insert(0, "..")  # Solo necesario si tu estructura de carpetas lo requiere

from asyncua import uamethod, Server, ua
from asyncua.server.users import User, UserRole
from asyncua.server.user_managers import UserManager

@uamethod
def checkVisionStatusMethod(parent, CurrentPrescription, TargetRangeMin, TargetRangeMax):
    print(f"Received: CP={CurrentPrescription}, Min={TargetRangeMin}, Max={TargetRangeMax}")
    if(CurrentPrescription > TargetRangeMin and CurrentPrescription < TargetRangeMax):
        return True
    else:
        return False

class CustomUserManager(UserManager):
    def __init__(self):
        # Define users and their roles
        self.users = {
            "admin": {"password": "admin", "role": UserRole.Admin},
            "alvaro": {"password": "alvaro", "role": UserRole.User},
        }
    
    def get_user(self, iserver, username=None, password=None, certificate=None):
        if username and password:
            user = self.users.get(username)
            if user and user["password"] == password:
                print(f"Authenticated user: {username}, role: {user['role']}")
                return User(role=user["role"])
        print(f"Failed authentication for: {username}")
        return None

async def main():
    _logger = logging.getLogger('asyncua')
    
    # Create server with custom user manager
    server = Server()
    server.iserver.user_manager = CustomUserManager()
    await server.init()

    server.set_endpoint('opc.tcp://localhost:4840/')

    await server.import_xml("Gafas.xml")

    print("Servidor OPC UA levantado en opc.tcp://localhost:4840/")
    print("Modelo AAS importado correctamente")
    print("Esperando conexiones de clientes...")

    # --- Add System object and ScheduledMeeting node ---
    system_uri = "http://example.com/system"
    system_idx = await server.register_namespace(system_uri)
    print(f"System namespace index: {system_idx}")
    objects = server.nodes.objects
    system_obj = await objects.add_object(system_idx, "System")
    meeting_nodeid = ua.NodeId("System.ScheduledMeeting", system_idx)
    meeting_node = await system_obj.add_variable(meeting_nodeid, "ScheduledMeeting", [], varianttype=ua.VariantType.String)
    await meeting_node.set_writable()
    await meeting_node.set_attr_bit(ua.AttributeIds.AccessLevel, ua.AccessLevel.CurrentWrite)
    await meeting_node.set_attr_bit(ua.AttributeIds.UserAccessLevel, ua.AccessLevel.CurrentWrite)
    print(f"ScheduledMeeting NodeId: {meeting_node.nodeid}")
    # ---------------------------------------------------

    # Set up nodes - all users can read, but write permissions are checked per request
    checkVisionStatus = server.get_node("ns=2;i=202")
    server.link_method(checkVisionStatus, checkVisionStatusMethod)
    
    # Set all nodes with explicit permissions - AccessLevel writable, UserAccessLevel read-only
    ValueClientName = server.get_node("ns=2;i=211")
    await ValueClientName.set_attr_bit(ua.AttributeIds.AccessLevel, ua.AccessLevel.CurrentWrite)
    await ValueClientName.write_attribute(ua.AttributeIds.UserAccessLevel, ua.DataValue(ua.Variant(ua.AccessLevel.CurrentRead, ua.VariantType.Byte)))

    ValueFrameMaterial = server.get_node("ns=2;i=217")
    await ValueFrameMaterial.set_attr_bit(ua.AttributeIds.AccessLevel, ua.AccessLevel.CurrentWrite)
    await ValueFrameMaterial.write_attribute(ua.AttributeIds.UserAccessLevel, ua.DataValue(ua.Variant(ua.AccessLevel.CurrentRead, ua.VariantType.Byte)))

    ValueFrameColor = server.get_node("ns=2;i=226")
    await ValueFrameColor.set_attr_bit(ua.AttributeIds.AccessLevel, ua.AccessLevel.CurrentWrite)
    await ValueFrameColor.write_attribute(ua.AttributeIds.UserAccessLevel, ua.DataValue(ua.Variant(ua.AccessLevel.CurrentRead, ua.VariantType.Byte)))

    ValueFrameBrand = server.get_node("ns=2;i=229")
    await ValueFrameBrand.set_attr_bit(ua.AttributeIds.AccessLevel, ua.AccessLevel.CurrentWrite)
    await ValueFrameBrand.write_attribute(ua.AttributeIds.UserAccessLevel, ua.DataValue(ua.Variant(ua.AccessLevel.CurrentRead, ua.VariantType.Byte)))

    ValueLensType = server.get_node("ns=2;i=235")
    await ValueLensType.set_attr_bit(ua.AttributeIds.AccessLevel, ua.AccessLevel.CurrentWrite)
    await ValueLensType.write_attribute(ua.AttributeIds.UserAccessLevel, ua.DataValue(ua.Variant(ua.AccessLevel.CurrentRead, ua.VariantType.Byte)))

    ValueVisionCondition = server.get_node("ns=2;i=241")
    await ValueVisionCondition.set_attr_bit(ua.AttributeIds.AccessLevel, ua.AccessLevel.CurrentWrite)
    await ValueVisionCondition.write_attribute(ua.AttributeIds.UserAccessLevel, ua.DataValue(ua.Variant(ua.AccessLevel.CurrentRead, ua.VariantType.Byte)))

    ValueLastRevisionDate = server.get_node("ns=2;i=183")
    await ValueLastRevisionDate.set_attr_bit(ua.AttributeIds.AccessLevel, ua.AccessLevel.CurrentWrite)
    await ValueLastRevisionDate.write_attribute(ua.AttributeIds.UserAccessLevel, ua.DataValue(ua.Variant(ua.AccessLevel.CurrentRead, ua.VariantType.Byte)))

    # Nodes that only admin can write - set UserAccessLevel to read-only
    ValueUsageState = server.get_node("ns=2;i=168")
    await ValueUsageState.set_attr_bit(ua.AttributeIds.AccessLevel, ua.AccessLevel.CurrentWrite)
    await ValueUsageState.write_attribute(ua.AttributeIds.UserAccessLevel, ua.DataValue(ua.Variant(ua.AccessLevel.CurrentRead, ua.VariantType.Byte)))

    ValueLensCondition = server.get_node("ns=2;i=174")
    await ValueLensCondition.set_attr_bit(ua.AttributeIds.AccessLevel, ua.AccessLevel.CurrentWrite)
    await ValueLensCondition.write_attribute(ua.AttributeIds.UserAccessLevel, ua.DataValue(ua.Variant(ua.AccessLevel.CurrentRead, ua.VariantType.Byte)))

    ValueFrameIntegrity = server.get_node("ns=2;i=180")
    await ValueFrameIntegrity.set_attr_bit(ua.AttributeIds.AccessLevel, ua.AccessLevel.CurrentWrite)
    await ValueFrameIntegrity.write_attribute(ua.AttributeIds.UserAccessLevel, ua.DataValue(ua.Variant(ua.AccessLevel.CurrentRead, ua.VariantType.Byte)))

    async with server:
        while True:
            await asyncio.sleep(1)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
