
import requests
import json
import imp
import sys, os
sys.path.append(os.path.join(arcpy.env.packageWorkspace,u'..\\cd\\exportreportgp\\'))
from report import Report
class Main:

    deplibs = "libs/"
    basemaps = "basemaps/"
    reportFile = "report.py"
    service_request = "service_request.py"
    engie_logo = os.path.join(os.path.dirname(os.path.realpath(__file__)), "engie_logo.png")
    data_access = "data_access.py"
    utils = "utils.py"
    init = "__init__.py"
    template = os.path.join(os.path.dirname(os.path.realpath(__file__)), "A4Portrait.mxd")
    fileRoot = os.path.dirname(os.path.realpath(__file__))

    webmap_as_json = arcpy.GetParameterAsText(0)
    layer = arcpy.GetParameterAsText(1)
    title = arcpy.GetParameterAsText(2)
    subtitle = arcpy.GetParameterAsText(3)
    
    def __init__(self):
        report = Report(self.webmap_as_json.replace('\n',""),self.layer.replace('\n',''), self.title, self.subtitle, self.template, self.engie_logo, self.basemaps)
        report.generate()


        

main = Main()  
