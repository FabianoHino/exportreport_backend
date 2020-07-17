
import requests
import json
import imp
import sys, os
sys.path.append(os.path.join(arcpy.env.packageWorkspace,u'..\\cd\\exportreportgp\\'))
from report import Report
class Main:
    
    reportFile = "report.py"
    service_request = "service_request.py"
    data_access = "data_access.py"
    utils = "utils.py"
    init = "__init__.py"
    template = "A4Portrait.mxd"
    
    webmap_as_json = arcpy.GetParameterAsText(0)
    layer = arcpy.GetParameterAsText(1)
    title = arcpy.GetParameterAsText(2)
    subtitle = arcpy.GetParameterAsText(3)
    
    def __init__(self):
        report = Report(self.webmap_as_json.replace('\n',""),self.layer.replace('\n',''), self.title, self.subtitle, self.template)
        report.generate()


        

main = Main()  
