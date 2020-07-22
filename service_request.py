import  urllib2
import urllib
import httplib
from urllib2 import Request
import os
import ssl
import arcpy
import shutil
class Service_Request:
    def get(self,url,stream):
        try:

            reqLib = Request(url)
            host = reqLib.get_host()

            url_aux = url.lower()
            reqLib_aux = Request(url_aux)
            host_oux = reqLib.get_selector()
            if reqLib_aux.get_selector().find('mapserver') == -1:
                idx = reqLib_aux.get_selector().index("featureserver")
            else:
                idx = reqLib_aux.get_selector().index("mapserver")
            url_params = urllib2.quote(reqLib.get_selector()[0:idx])
            get_url = '{}{}'.format(url_params,reqLib.get_selector()[idx:len(reqLib.get_selector())])
            
            conn = httplib.HTTPSConnection(host,context=ssl._create_unverified_context())
            arcpy.AddMessage(get_url)
            
            conn.request("GET",get_url)
            response = conn.getresponse()

            return response
        except Exception as ex:
            print(ex.message)
            raise(ex)

# service = Service_Request()
# service.get("https://p118cbarbosa.img.com.br/arcgis/rest/services/CADASTRO_IMOBILIARIO/MapServer/1/5140/attachments/1",None)
