import json
import tinytuya

cloud = tinytuya.Cloud()
DEVICE_ID = "eb322c9cdb943bba14yguj"

datos = cloud.getstatus(DEVICE_ID)
print(json.dumps(datos, indent=2))