import logging
import asyncio
import sys
sys.path.insert(0, "..")  # Solo necesario si tu estructura de carpetas lo requiere

from asyncua import uamethod, Server

@uamethod
def checkVisionStatusMethod(parent, CurrentPrescription, TargetRangeMin, TargetRangeMax):
    print(f"Received: CP={CurrentPrescription}, Min={TargetRangeMin}, Max={TargetRangeMax}")
    if(CurrentPrescription > TargetRangeMin and CurrentPrescription < TargetRangeMax):
        return True
    else:
        return False

async def main():
    _logger = logging.getLogger('asyncua')
    
    server = Server()
    await server.init()

    server.set_endpoint('opc.tcp://localhost:4840/')

    await server.import_xml("Gafas.xml")


    print("Servidor OPC UA levantado en opc.tcp://localhost:4840/")
    print("Modelo AAS importado correctamente")
    print("Esperando conexiones de clientes...")
    
    checkVisionStatus = server.get_node("ns=2;i=202")
    server.link_method(checkVisionStatus,checkVisionStatusMethod)
    
    ValueClientName = server.get_node("ns=2;i=211")
    await ValueClientName.set_writable()

    ValueFrameMaterial = server.get_node("ns=2;i=217")
    await ValueFrameMaterial.set_writable()

    ValueFrameColor = server.get_node("ns=2;i=226")
    await ValueFrameColor.set_writable()

    ValueFrameBrand = server.get_node("ns=2;i=229")
    await ValueFrameBrand.set_writable()

    ValueLensType = server.get_node("ns=2;i=235")
    await ValueLensType.set_writable()

    ValueVisionCondition = server.get_node("ns=2;i=241")
    await ValueVisionCondition.set_writable()

    ValueUsageState = server.get_node("ns=2;i=168")
    await ValueUsageState.set_writable()

    ValueLensCondition = server.get_node("ns=2;i=174")
    await ValueLensCondition.set_writable()

    ValueFrameIntegrity = server.get_node("ns=2;i=180")
    await ValueFrameIntegrity.set_writable()

    ValueLastRevisionDate = server.get_node("ns=2;i=183")
    await ValueLastRevisionDate.set_writable()
    
    async with server:
        while True:
            await asyncio.sleep(1)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
