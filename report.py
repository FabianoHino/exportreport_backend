# -*- coding: utf-8 -*-
import sys
sys.path.append(".")
import arcpy
import os
import io
import uuid
import json
import reportlab
from reportlab.platypus import SimpleDocTemplate, Image, Table, TableStyle, Spacer
from reportlab.lib.pagesizes import letter,A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.lib import colors

from infra.utils import Utils
from data_access import Data_Access


class Report:

    def __init__(self,web_map_as_json,layer):
        try:
            arcpy.AddMessage("INIT REPORT")
            self.report_elements = []
            layer_json = str(''.join(layer.replace('\\n','')).encode('utf-8'))
            self.layer_obj = json.loads(layer_json)

            self.utils = Utils()
            self.configuration = self.utils.get_configuration()
            self.data_access = Data_Access(self.configuration,self.layer_obj)
            self.web_map_as_json = web_map_as_json.replace('\\n','')

        except Exception as ex:
            print(ex)
            arcpy.AddMessage(ex)
            

    def generate(self):
        try:
            self.__build_table()
            self.__build_relationship_table()
            self.__build_web_map()
            self.__build_pdf("report.pdf")
        except Exception as ex:
            print(ex)
            arcpy.AddMessage(ex)

    def __build_web_map(self):
        arcpy.AddMessage("BUILD WEB MAP")
        template_mxd = self.configuration['template_mxd']
        path_webmap_img = self.configuration['output_webmap_img']

        result = arcpy.mapping.ConvertWebMapToMapDocument(self.web_map_as_json, template_mxd)
        mxd = result.mapDocument
        df = arcpy.mapping.ListDataFrames(mxd, 'Webmap')[0]

        output = 'webmap_{}.jpg'.format(str(uuid.uuid1()))
        output_file = os.path.join(path_webmap_img, output)
        arcpy.mapping.ExportToJPEG(mxd, output_file)

        img = Image(output_file)
        self.report_elements.append(img)
        del mxd
        del output_file

    def __build_table(self):
        arcpy.AddMessage("BUILD TABLE")
        data = self.data_access.get_data()
        arcpy.AddMessage("data")
        data_table = data['data_table']
        arcpy.AddMessage("data_table")
        title_table = self.layer_obj['layer']['title']
        self.__build_title_table(title_table)
        table_principal = Table(data_table,colWidths=[8 * cm, 12 * cm])
        style = self.__table_style(len(data_table))
        table_principal.setStyle(style)

        self.report_elements.append(table_principal)
        self.__set_spacer(0.1)

        arcpy.AddMessage(len(data['attachmentsttachments']))
        if len(data['attachmentsttachments']) > 0:
            self.__build_attachments(data['attachmentsttachments'])

    def __build_title_table(self, title):
        table_title = Table([[title]],colWidths=[20 * cm])
        style = self.__title_table_style()
        table_title.setStyle(style)
        self.report_elements.append(table_title)

    def __build_relationship_table(self):
        arcpy.AddMessage("BUILD RELATIONSHIP TABLE ")
        relationships = self.layer_obj['layer']['relationship']
        for relship in relationships:
            title = relship['title']
            self.__build_title_table(title)
            data = self.data_access.get_data_relationship(relship)
            data_table_relationship = data['data_table']
            data_rel_aux = []
            if 'spacer' in data_table_relationship:
                if data_table_relationship.count('spacer') > 0:
                    for data_rel in data_table_relationship:
                        if data_rel != 'spacer':
                            data_rel_aux.append(data_rel)
                        else:
                            self.__create_table_rel(data_rel_aux)
                            self.__set_spacer(0.2)
                            data_rel_aux = []
                else:
                    self.__create_table_rel(data_table_relationship)
                    self.__set_spacer(0.1)
            else:
                self.__create_table_rel(data_table_relationship)
                self.__set_spacer(0.1)
            if len(data['attachments']) > 0:
                self.__build_attachments(data['attachments'])
    
    def __create_table_rel(self,data):
        table_rel = Table(data, colWidths=[8 * cm, 12 * cm])
        style = self.__table_style(len(data))    
        table_rel.setStyle(style)
        self.report_elements.append(table_rel)
        
    def __build_attachments(self,uuids):
        try:
            arcpy.AddMessage("BUILD ATTACHMENTS")
            data = []
            file_img = []
        
            for uuid in uuids:
                files_attach = self.data_access.get_attachments_in_folder(uuid)
                for file in files_attach:
                    path_img = '{}{}\\{}'.format(self.configuration['output_attach'],uuid,file)
                    img_attach = Image( path_img)
                    img_attach.width=0.3*inch
                    img_attach.height=0.3*inch
                    img_attach.drawWidth=3*inch
                    img_attach.drawHeight=3*inch
                    file_img.append(img_attach)  

                    if len(file_img) == 2:
                        data.append(file_img)
                        file_img = []

                if len(file_img) > 0:
                    data.append(file_img)    
        
                if len(data) > 0:
                    self.__set_position_attach(data)
        except Exception as ex:
            print(ex)
            arcpy.AddMessage(ex.message)
    
    def __title_table_style(self):
         return TableStyle([
            ('BACKGROUND', (0,0),(4,0), colors.Color(0.7,0.7,0.7)),
            ('TEXTCOLOR',(0,0),(-1,0), colors.black),
            ('ALIGN',(0,0),(-1,-1),'CENTER'),
            ('FONTSIZE', (0,0), (-1,0), 11),
            ('BOTTOMPADDING', (0,0), (-1,0), 12),
            # ('BOX', (0,0), (-1,-1), 0.25, colors.black)
        ]) 

    def __table_style(self, lines):
        
        return TableStyle([
            ('BACKGROUND', (0,0),(0,lines), colors.Color(0.9,0.9,0.9)),
            ('TEXTCOLOR',(0,0),(-1,0), colors.black),
            ('ALIGN',(0,0),(-1,-1),'LEFT'),
            ('FONTSIZE', (0,0), (-1,0), 10),
            ('LINEABOVE', (0,0), (-1,-1), 0.25, colors.white),
            # ('BOTTOMPADDING', (0,0), (-1,0), 12)
        ])

    def __table_style_images(self):
        return TableStyle([
            ('ALIGN',(0,0),(-1,-1),'CENTER'),
            ('FONTSIZE', (0,0), (-1,0), 10),
            ('BOTTOMPADDING', (0,0), (-1,0), 12)
        ])

        return col_widths

    def __set_spacer(self, size):
        self.report_elements.append(Spacer(1, size*inch))

    def __set_position_attach(self,data):
        table_img = Table(data, colWidths=[10 * cm])
        style = self.__table_style_images()
        table_img.setStyle(style)
        self.report_elements.append(table_img)


    def __build_pdf(self,file_name):
        try:
            arcpy.AddMessage("SimpleDocTemplate")
            uniqueID = str(uuid.uuid1())
            path_report = os.path.join(arcpy.env.scratchWorkspace, 'report_{0}.pdf'.format(uniqueID))
            arcpy.AddMessage(path_report)
            doc = SimpleDocTemplate(path_report, pagesize=A4,showBoundary=0, leftMargin=0,rightMargin=0, topMargin=12, bottomMargin=5, allowSplitting=1)
            doc.build(self.report_elements)
            
            arcpy.AddMessage("build completed!")
            arcpy.SetParameter(2, path_report)
            
            self.utils.remove_all_files(self.configuration['output_attach'],True)
            self.utils.remove_all_files(self.configuration['output_webmap_img'],False)
        except Exception as ex:
            print(ex)
            arcpy.AddMessage(ex.message)
        
        

