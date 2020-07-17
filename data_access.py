# -*- coding: utf-8 -*-
import arcpy
import sys
import os
import json
import shutil
import uuid
from infra.utils import Utils
from os import listdir
from os.path import isfile, join
from service_request import Service_Request
from scipy.misc import bytescale
class Data_Access:
    def __init__(self,configuration,layer):
        self.configuration = configuration
        self.utils = Utils()
        self.layer_obj = layer
        self.uniqueIDAttachments = []
        self.service_request = Service_Request()
        self.token = self.layer_obj['layer']['token']
        
    def get_data(self):
        try:
            self.load_service_definition(self.layer_obj['layer']['url'])
            url = self.utils.build_url(self.layer_obj,self.token,None)
            response = self.service_request.get(url,None)
            data = []

            if response.status == 200:
                data_response = json.loads(response.read())
                
                if 'features' in data_response:
                    if len(data_response['features']) > 0:
                        data = self.__buid_data_table_main(fields,is_attach,data_response)
                    else:
                        self.set_empty_data(data)
                elif 'error' in data_response:
                    arcpy.AddMessage(data_response['error'])
            
                self.layer_attributes = data_response['features'][0]['attributes']

            return {"data_table":data,"attachmentsttachments":self.uniqueIDAttachments}
        except Exception as ex:
            arcpy.AddMessage(ex)
    
    def __buid_data_table_main(self, data_response):
        is_attach = self.layer_obj['layer']['is_attach']
        fields = self.layer_obj['layer']['fields']
        data = []

        for fd in fields:
            column_name = fd['name']
            column_label = fd['alias']
            value = data_response['features'][0]['attributes'][column_name]
            domain_field = self.get_domain_field(column_name)
            if len(domain_field) > 0:
                coded_values = domain_field[0]['domain']['codedValues']
                value = [cv for cv in coded_values if cv['code'] == value][0]['name']
            data.append([column_label,value])
                        
            if is_attach:
                self.get_attachmentInfos(self.layer_obj['layer']['url'],data_response['features'][0]['attributes']['objectid']) 

        return data  

    def __build_data_table_relationship(selef, data_response, relationship):
        data = []
        fields = relationship['fields']
        is_attach = relationship['is_attach']

        for feature in data_response['features']:
            for fd in fields:
               column_name = fd['name']
               column_label = fd['alias']
               value = feature['attributes'][column_name]
               domain_field = self.get_domain_field(column_name)
               if len(domain_field) > 0:
                   coded_values = domain_field[0]['domain']['codedValues']
                   value = [cv for cv in coded_values if cv['code'] == value][0]['name']
               data.append([column_label,value])
                            
            if is_attach:
                self.get_attachmentInfos(relationship['url'],feature['attributes']['objectid'])                        
            data.append('spacer')
        return data

    def get_data_relationship(self, relationship):
        codigo_imovel = self.layer_attributes[relationship['origin']]
        url = self.utils.build_url(relationship,self.token,codigo_imovel)
        response = self.service_request.get(url,None)
        data = []
        if response.status == 200:
            data_response = json.loads(response.read())
            if 'features' in data_response:
                if len(data_response['features']) > 0:
                    data = self.__build_data_table_relationship(data_response,relationship)
                else:
                    self.set_empty_data(data)
            else:
                self.set_empty_data(data)
           
        return {"data_table":data,"attachments":self.uniqueIDAttachments}  

    def set_empty_data(self,data):
        data.append(["","Nenhum resultado"])
    
    def __get_fields(self):
        fields = self.configuration['layer']['fields']
        fields_layer = []
        self.alias_columns = []

        for fd in fields:
            fields_layer.append(fd['name'])
            self.alias_columns.append(fd['alias'])
        
        return fields_layer

    def __get_relation_fields(self, relship):
        fields = relship['fields']
        fields_rel = []
        columns = []
        self.alias_relcolumns = []
        
        for fd in fields:
            fields_rel.append(fd['name'])
            self.alias_relcolumns.append(fd['alias'])
        
        return fields_rel
  
    def get_attachmentInfos(self, url, objectid):
        url_infos = '{}/{}/attachments?f=json'.format(url,objectid)
        response = self.service_request.get(url_infos,None) 

        if response.status == 200:
            attachmentInfos = json.loads(response.read())
            if 'error' not in attachmentInfos:
                if len(attachmentInfos['attachmentInfos']) > 0:
                    self.download_attachment(attachmentInfos['attachmentInfos'],url,objectid)
        
    def download_attachment(self,attachmentInfos,url,objectid):
        arcpy.AddMessage('downloadattach')
        uniqueID = str(uuid.uuid1())
        self.uniqueIDAttachments = []
        for attachInfo in attachmentInfos:
            url_attach = '{}/{}/attachments/{}'.format(url,objectid,attachInfo['id'])
            folder = '{}{}\\'.format(self.configuration['output_attach'],uniqueID)
            path_img = '{}\{}'.format(folder,''.join(attachInfo['name']).encode('utf-8'))
            response = self.service_request.get(url_attach,None)
            #response2 = self.service_request.get_attachment(url_attach)
            #response.raw.decode_content = True
            
            if not os.path.exists(os.path.dirname(folder)):
                os.makedirs(os.path.dirname(folder))
            arcpy.AddMessage('openread')
            with open(path_img,'wb') as handle:
                for chunck in response.read():
                    handle.write(chunck)
        
        self.uniqueIDAttachments.append(uniqueID)
    
    def load_service_definition(self, url):
        try:
            response = self.service_request.get(url+"?f=pjson",False)
            if response.status_code == 200:
                definition = json.loads(response.content)
                self.definition_fields = definition['fields']
            else:
                arcpy.AddMessage('Error response get service definition')
        except Exception as ex:
            arcpy.AddMessage(ex)
    
    def get_domain_field(self, field_name):
        fields_domain = [fd for fd in self.definition_fields if fd['domain'] != None and fd['name'] == field_name]
        return fields_domain

            
    def get_attachments_in_folder(self,uuid):
        path_img = '{}{}'.format(self.configuration['output_attach'],uuid)
        onlyfiles = [f for f in listdir(path_img) if isfile(join(path_img, f))]

        return onlyfiles

        

 

            
