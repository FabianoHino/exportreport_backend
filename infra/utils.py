# -*- coding: utf-8 -*-
import yaml
import os
import shutil
import glob
import arcpy

class Utils:
    def __init__(self):
        self.this_folder = os.path.dirname(os.path.abspath(__file__))

    def get_configuration(self):
        with open(os.path.join(self.this_folder,'configuration.yml'), "r") as ymlfile:
            cfg = yaml.load(ymlfile)       
        return cfg


    def is_image(self,path_img):
        imgs = ['jpeg','jpg','gif','bmp','png','tiff']
        return True

    def remove_all_files(self,folder,is_folder):
       
        if is_folder:
           shutil.rmtree(folder, ignore_errors=True)
        else:
            files = glob.glob(folder+"*")
            for f in files:
                os.remove(f)

    def build_url(self,layer_obj,token, value_where):
        if value_where is None:
            url = ''.join(layer_obj['layer']['url']).encode('utf-8')
            
            if type(layer_obj['layer']['codigo_imovel'] is int):
                where = "{}={}".format(layer_obj['layer']['field_search'],layer_obj['layer']['codigo_imovel'])
            else:
                where = "{}='{}'".format(layer_obj['layer']['field_search'],layer_obj['layer']['codigo_imovel']) 
        else:
            url = ''.join(layer_obj['url']).encode('utf-8')
            if type(value_where) is int:
                where = "{}={}".format(layer_obj['dest'],value_where)
            else:
                where = "{}='{}'".format(layer_obj['dest'],value_where)
        
        if len(token) == 0:
            url = "{}/query?where={}&outFields={}&f=pjson".format(url,where,"*")
        else:
            url = "{}/query?where={}&outFields={}&token={}&f=pjson".format(url,where,"*",token)
            
        return url

    def get_out_fields(self, fields):
        out_fields = [fd['name'] for fd in fields]
        out_fields_formatted = ','.join(elem for elem in out_fields)
        return out_fields_formatted


# utils = Utils()
# path ="C:\\jaraujo\\py_report\\webmap_img\\"
# utils.remove_all_files(path)
