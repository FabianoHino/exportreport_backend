from report import Report
import requests
import json
class Main:

    # Input bMap json
#     webmap_as_json =  '''
#     {
#         "mapOptions":{
#             "showAttribution":true,
#             "extent":{
#                 "xmin":-5745167.002455485,
#                 "ymin":-3418802.4728408577,
#                 "xmax":-5720707.153404261,
#                 "ymax":-3409926.2229312537,
#                 "spatialReference":{
#                     "wkid":102100
#                 }
#             },
#             "spatialReference":{
#                 "wkid":102100
#             },
#             "scale":36111.909643
#         },
#         "operationalLayers":[
#             {
#                 "id":"defaultBasemap_0",
#                 "title":"Mapa Topográfico Mundial",
#                 "opacity":1,
#                 "minScale":0,
#                 "maxScale":0,
#                 "url":"https://services.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer"
#             },
#             {
#                 "id":"FC_LOTE_CB_4016",
#                 "title":"FC_LOTE_CB - gisdata.sde.CDI_LOTE_1",
#                 "opacity":1,
#                 "minScale":0,
#                 "maxScale":0,
#                 "layerDefinition":{
#                     "drawingInfo":{
#                     "renderer":{
#                         "type":"simple",
#                         "label":"",
#                         "description":"",
#                         "symbol":{
#                             "color":[
#                                 245,
#                                 232,
#                                 203,
#                                 255
#                             ],
#                             "outline":{
#                                 "color":[
#                                 110,
#                                 110,
#                                 110,
#                                 255
#                                 ],
#                                 "width":0.4,
#                                 "type":"esriSLS",
#                                 "style":"esriSLSSolid"
#                             },
#                             "type":"esriSFS",
#                             "style":"esriSFSSolid"
#                         }
#                     }
#                     }
#                 },
#                 "token":"eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICI3N3FNallpWE1CWnYxUUVyMGxqdUFZVlZLcjNMMEVUSkhuR1YxX1FIa2djIn0.eyJqdGkiOiJiMTJiNGIxMS02OTc4LTQwMjEtOTMxZi1lNGZmMjZmMGZiNDciLCJleHAiOjE1OTE4OTkxMTYsIm5iZiI6MCwiaWF0IjoxNTkxODg0NzE2LCJpc3MiOiJodHRwczovL3AxMTBjaXZpdGFzLmltZy5jb20uYnIvYXV0aC9yZWFsbXMvQ2l2aXRhcyIsImF1ZCI6Imdlb3BvcnRhbCIsInN1YiI6ImJhNDU0YmRhLWEwMDAtNDI4MC05MTQzLTdmZDc2NTY4ZDQ1ZSIsInR5cCI6IkJlYXJlciIsImF6cCI6Imdlb3BvcnRhbCIsIm5vbmNlIjoiOWZjYmNiMWEtZGQyYS00ODlhLTkzMGQtYzJjOTExZjYwNDE5IiwiYXV0aF90aW1lIjoxNTkxODg0NzEzLCJzZXNzaW9uX3N0YXRlIjoiMWJlY2FhYTgtNmJiMC00NjRiLTg2NzgtOTA0Mzg0YTliMGViIiwiYWNyIjoiMSIsImFsbG93ZWQtb3JpZ2lucyI6WyIqIl0sInJlYWxtX2FjY2VzcyI6eyJyb2xlcyI6WyJraWVtZ210IiwiQWRtaW5pc3RyYWRvciIsImtpZS1tZ210IiwidW1hX3Byb3RlY3Rpb24iLCJyZXN0LWFsbCIsInVtYV9hdXRob3JpemF0aW9uIiwia2llLXNlcnZlciJdfSwicmVzb3VyY2VfYWNjZXNzIjp7ImNpdml0YXMtZXMiOnsicm9sZXMiOlsia2llbWdtdCIsIkFkbWluaXN0cmFkb3IiLCJraWUtbWdtdCIsInVtYV9wcm90ZWN0aW9uIiwiYWRtaW4iLCJyZXN0LWFsbCIsImtpZS1zZXJ2ZXIiXX0sInJlYWxtLW1hbmFnZW1lbnQiOnsicm9sZXMiOlsidmlldy1pZGVudGl0eS1wcm92aWRlcnMiLCJ2aWV3LXJlYWxtIiwibWFuYWdlLWlkZW50aXR5LXByb3ZpZGVycyIsImltcGVyc29uYXRpb24iLCJyZWFsbS1hZG1pbiIsImNyZWF0ZS1jbGllbnQiLCJtYW5hZ2UtdXNlcnMiLCJxdWVyeS1yZWFsbXMiLCJ2aWV3LWF1dGhvcml6YXRpb24iLCJxdWVyeS1jbGllbnRzIiwicXVlcnktdXNlcnMiLCJtYW5hZ2UtZXZlbnRzIiwibWFuYWdlLXJlYWxtIiwidmlldy1ldmVudHMiLCJ2aWV3LXVzZXJzIiwidmlldy1jbGllbnRzIiwibWFuYWdlLWF1dGhvcml6YXRpb24iLCJtYW5hZ2UtY2xpZW50cyIsInF1ZXJ5LWdyb3VwcyJdfSwiYXJjZ2lzLXNlcnZlciI6eyJyb2xlcyI6WyJnaXNzZXJ2ZXItdXNlciJdfSwiYWNjb3VudCI6eyJyb2xlcyI6WyJtYW5hZ2UtYWNjb3VudCIsIm1hbmFnZS1hY2NvdW50LWxpbmtzIiwidmlldy1wcm9maWxlIl19LCJnZW9wb3J0YWwiOnsicm9sZXMiOlsiZ2VvcG9ydGFsLXVzZXIiXX19LCJuYW1lIjoiQWRtaW5pc3RyYWRvciBBZG1pbmlzdHJhZG9yIiwicHJlZmVycmVkX3VzZXJuYW1lIjoiYWRtaW4iLCJnaXZlbl9uYW1lIjoiQWRtaW5pc3RyYWRvciIsImZhbWlseV9uYW1lIjoiQWRtaW5pc3RyYWRvciIsImVtYWlsIjoiYWRtaW5AYWRtaW4uY29tIn0.kkapCRgiyuB-Qenwf_Sa8y55zoWE_CtQ7cqgvYOjHhJljEyiRkh1_6V9CReF-ktzoCS9isA7sinLTjHiQCH7Va3ZSLr_jWYWVmKu7O55NX3NwTtdQYxC0kBaurAEsCqarklCvOV9J-3WQbQtxpqRMv7WUrmGGxrjvd1OpajUlt5B4-aDXQdYQuYhLuFmnHcnWN-evuxdkb39qY8VO8JjlAj51JE58skkB_l7WTvysk1VPiSLq0XuCxQd9xbbn5y_bhtZLYEUNAGnvUw_hBR4YXqzU3HRI3_7JyM3dskzJsyxFTIY_feCFspDI7J02mRbq1JSw1YlCrHrMs9WKJdFzQ",
#                 "url":"https://p110civitas.img.com.br/arcgis/rest/services/Civitas/FC_LOTE_CB/FeatureServer/0"
#             }
#         ],
#         "exportOptions":{
#             "outputSize":[
#                 670,
#                 500
#             ],
#             "dpi":96
#         },
#         "layoutOptions":{
#             "titleText":"Impressão",
#             "authorText":"Professional Services",
#             "copyrightText":"Imagem Sistema de Informações Ltda",
#             "customTextElements":[
#                 {
#                     "Date":"11/06/2020 11:30:52"
#                 }
#             ],
#             "scaleBarOptions":{
#                 "metricUnit":"esriKilometers",
#                 "metricLabel":"km",
#                 "nonMetricUnit":"esriMiles",
#                 "nonMetricLabel":"mi"
#             },
#             "legendOptions":{
#                 "operationalLayers":[
#                     {
#                     "id":"FC_LOTE_CB_4016"
#                     }
#                 ]
#             }
#         }
#         }
#     ''' 

#     layer = ''' 
#     {
# 	"layer":{
#       "title":"Lotes",
#       "url":"https://p118cbarbosa.img.com.br/arcgis/rest/services/CADASTRO_IMOBILIARIO/MapServer/1",
#       "field_search":"nu_inscricao_imobiliaria",
#       "codigo_imovel":"301001003590000",
#       "is_attach":true,
#       "fields":[
#          {
#             "name":"nu_inscricao_imobiliaria",
#             "alias":"Inscrição imobiliária"
#          },
#          {
#             "name":"nu_lote",
#             "alias":"Número de medida do lote"
#          },
#          {
#             "name":"cd_quadra",
#             "alias":"Código da quadra"
#          }
#       ],
#       "relationship":[
#          {
#             "title":"INFORMAÇÕES PARA EDIFICAÇÃO",
#             "url":"https://p118cbarbosa.img.com.br/arcgis/rest/services/CADASTRO_IMOBILIARIO/MapServer/2",
#             "origin":"nu_inscricao_imobiliaria",
#             "dest":"insc_tecni",
#             "is_attach":true,
#             "fields":[
#                {
#                   "name":"insc_tecni",
#                   "alias":"Inscrição ténica"
#                },
#                {
#                   "name":"num_pavi",
#                   "alias":"Número de pavimentos"
#                }
#             ]
#          },
#          {
#             "title":"CADASTRO DO IMOVEL",
#             "url":"https://p118cbarbosa.img.com.br/arcgis/rest/services/CADASTRO_IMOBILIARIO/MapServer/5",
#             "origin":"cd_lote",
#             "dest":"numero_cadastro",
#             "is_attach":true,
#             "fields":[
#                {
#                   "name":"tipo_edificacao",
#                   "alias":"Tipo educação"
#                },
#                {
#                   "name":"padrao",
#                   "alias":"Padrão"
#                },
#                {
#                   "name":"utilizacao",
#                   "alias":"Utilização"
#                }
#             ]
#          }
#       ]
#    }
# }
#     '''
    webmap_as_json = arcpy.GetParameterAsText(0)
    layer = arcpy.GetParameterAsText(1)
    def __init__(self):
        report = Report(self.webmap_as_json.replace('\n',""),self.layer.replace('\n',''))
        #report = Report(self.webmap_as_json,self.title,self.matricula)
        report.generate()

main = Main()  