# coding=utf-8

import arcpy
import sys
reload(sys)
sys.setdefaultencoding('utf8')
import os
import json
import shutil
import uuid
from utils import Utils
from os import listdir
from os.path import isfile, join
from service_request import Service_Request


class Data_Access:
    def __init__(self,layer):

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
            self.uniqueIDAttachments = []

            if response.status == 200:
                data_response = json.loads(response.read())
                
                if 'features' in data_response:
                    if len(data_response['features']) > 0:
                        data = self.__buid_data_table_main(data_response)
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
        self.uniqueIDAttachments = []
        attributes = data_response['features'][0]['attributes']
        for fd in fields:
            
            column_name = fd['name']
            column_label = fd['alias']
            value = attributes[column_name]
            domain_field = self.get_domain_field(column_name)
            
            if self.is_date(data_response['fields'],column_name,value):
                value = self.utils.date_format(value)

            if len(domain_field) > 0:
                value = self.__set_domain_value(domain_field,value)

            
            data.append([column_label,value])
                        
            if is_attach:
                
                arcpy.AddMessage("DISPLAY FIELD"+str(self.display_field))
                arcpy.AddMessage("DISPLAY FIELD MAIN"+attributes[self.display_field])
                self.display_field_value = attributes[self.display_field]
                self.get_attachmentInfos(self.layer_obj['layer']['url'],attributes) 

        
        return data  

    def __build_data_table_relationship(self, data_response, relationship):
        data = []
        fields = relationship['fields']
        is_attach = relationship['is_attach']
        self.uniqueIDAttachments = []
        for feature in data_response['features']:
            for fd in fields:
               column_name = fd['name']
               column_label = fd['alias']
               value = feature['attributes'][column_name]
               domain_field = self.get_domain_field(column_name)
               
               if self.is_date(data_response['fields'],column_name,value):
                   value = self.utils.date_format(value)

               if len(domain_field) > 0:
                   value = self.__set_domain_value(domain_field,value)
               data.append([column_label,value])
                            
            if is_attach:
             
                self.display_field_value = feature['attributes'][self.display_field]
                self.get_attachmentInfos(relationship['url'],feature['attributes'])                        
            data.append('spacer')
        return data
    
    def __set_domain_value(self,domain_field,value):
        
        if value is None or str(value).strip() is "":
            return ""
        
        coded_values = domain_field[0]['domain']['codedValues']
        domain = [cv for cv in coded_values if cv['code'] == value]

        if len(domain) == 0:
            value_field = value
        else:
            value_field = domain[0]['name']
        return value_field

    def get_data_relationship(self, relationship):
        self.load_service_definition(relationship['url'])
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
  
    def get_attachmentInfos(self, url, attributes):
        arcpy.AddMessage('attachmentINfos')
        objectid = self.get_objectid(attributes)
        url_infos = '{}/{}/attachments?f=pjson&token={}'.format(url,objectid,self.token)
        response = self.service_request.get(url_infos,None)
        if response.status == 200:
            attachmentInfos = json.loads(response.read())
            if 'error' not in attachmentInfos:
                if len(attachmentInfos['attachmentInfos']) > 0:
                    self.download_attachment(attachmentInfos['attachmentInfos'],url,objectid)
            else:
                arcpy.AddMessage("Error request: " + response['error'])
     
    def get_objectid(self, attributes):
        for (k,v) in attributes.items():
            if k.lower() == 'objectid':
                return attributes[k]
        
    def download_attachment(self,attachmentInfos,url,objectid):
        self.uniqueIDAttachments = []
        uniqueID = str(uuid.uuid1())
        
        if(len(attachmentInfos) > 0):
            for attachInfo in attachmentInfos:
                url_attach = '{}/{}/attachments/{}?token={}'.format(url,objectid,attachInfo['id'],self.token)
                folder = '{}{}\\'.format(arcpy.env.scratchWorkspace,uniqueID)
                path_img = '{}\{}'.format(folder,''.join(attachInfo['name']).encode('utf-8'))
                response = self.service_request.get(url_attach,None)
                #response.raw.decode_content = True
                
                if not os.path.exists(os.path.dirname(folder)):
                    os.makedirs(os.path.dirname(folder))

                with open(path_img,'wb') as handle:
                    for chunk in response.read():
                        handle.write(chunk)
        
            self.uniqueIDAttachments.append({"name":uniqueID,"display_field":self.display_field_value})

    def load_service_definition(self, url):
        try:
            url_definition = '{}?token={}&f=pjson'.format(url,self.token)
            response = self.service_request.get(url_definition,None)
            if response.status == 200:
                definition = json.loads(response.read())
                self.definition_fields = definition['fields']
                arcpy.AddMessage("DEFINITION "+definition['displayField'])
                self.display_field = definition['displayField']
            else:
                arcpy.AddMessage('Error response get service definition')
        except Exception as ex:
            arcpy.AddMessage(ex)
    
    def get_domain_field(self, field_name):
        fields_domain = [fd for fd in self.definition_fields if 'domain' in fd and fd['domain'] != None and fd['name'] == field_name]
        return fields_domain


    def is_date(self, fields_response, column_name,value):
     
        for itens in fields_response:
            if itens['name'].lower() == column_name.lower() and itens['type'] == 'esriFieldTypeDate':
                return True
        return False


    def get_attachments_in_folder(self,uuid):
        path_img = '{}{}'.format(arcpy.env.scratchWorkspace,uuid)
        onlyfiles = [f for f in listdir(path_img) if isfile(join(path_img, f))]
        arcpy.AddMessage(uuid)
        arcpy.AddMessage(len(onlyfiles))
        return onlyfiles

        

 

            
