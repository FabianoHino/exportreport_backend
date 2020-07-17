# -*- coding: utf-8 -*-
import arcpy
import sys
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
            self.uniqueIDAttachments = []
            url = self.utils.build_url(self.layer_obj,self.token,None)
            fields = self.layer_obj['layer']['fields']
            
            response = self.service_request.get(url,None)
            is_attach = self.layer_obj['layer']['is_attach']
            data = []
           
            if response.status == 200:
                data_response = json.loads(response.read())
                
                if 'features' in data_response:
                    if len(data_response['features']) > 0:
                   
                        for fd in fields:
                           
                            column_name = fd['name']
                            column_label = fd['alias']
                            value = data_response['features'][0]['attributes'][column_name]
                            data.append([column_label,value])
                        
                        if is_attach:
                            self.get_attachmentInfos(self.layer_obj['layer']['url'],data_response['features'][0]['attributes']['OBJECTID'])   
                    else:
                        self.set_empty_data(data)
                elif 'error' in data_response:
                    arcpy.AddMessage(data_response['error'])
            
                self.layer_attributes = data_response['features'][0]['attributes']

            return {"data_table":data,"attachmentsttachments":self.uniqueIDAttachments}
        except Exception as ex:
            arcpy.AddMessage(ex)

    def get_data_relationship(self, relationship):
        self.uniqueIDAttachments = []
        codigo_imovel = self.layer_attributes[relationship['origin']]
        url = self.utils.build_url(relationship,self.token,codigo_imovel)
        fields = relationship['fields']
        is_attach = relationship['is_attach']
        response = self.service_request.get(url,None)
        data = []
        if response.status == 200:
            data_response = json.loads(response.read())
            if 'features' in data_response:
                if len(data_response['features']) > 0:
                    for feature in data_response['features']:
                        for fd in fields:
                            column_name = fd['name']
                            column_label = fd['alias']
                            value = feature['attributes'][column_name]
                            data.append([column_label,value])
                            
                        if is_attach:
                            self.get_attachmentInfos(relationship['url'],feature['attributes']['OBJECTID'])                        
                        data.append('spacer')
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
        arcpy.AddMessage('attachmentINfos')
        url_infos = '{}/{}/attachments?f=pjson&token={}'.format(url,objectid,self.token)
        response = self.service_request.get(url_infos,None)
        arcpy.AddMessage(response.status)
        if response.status == 200:
            attachmentInfos = json.loads(response.read())
            if 'error' not in attachmentInfos:
                if len(attachmentInfos['attachmentInfos']) > 0:
                    self.download_attachment(attachmentInfos['attachmentInfos'],url,objectid)
        
    def download_attachment(self,attachmentInfos,url,objectid):
        uniqueID = str(uuid.uuid1())
        self.uniqueIDAttachments = []
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
        
        self.uniqueIDAttachments.append(uniqueID)
            
    def get_attachments_in_folder(self,uuid):
        path_img = '{}{}'.format(arcpy.env.scratchWorkspace,uuid)
        onlyfiles = [f for f in listdir(path_img) if isfile(join(path_img, f))]
        arcpy.AddMessage(uuid)
        arcpy.AddMessage(len(onlyfiles))
        return onlyfiles

        

 

            
