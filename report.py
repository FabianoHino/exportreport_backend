# -*- coding: utf-8 -*-
import sys
sys.path.append(".")
import arcpy
import os
import io
import uuid
import json
import reportlab
from reportlab.platypus import SimpleDocTemplate, Image, Table, TableStyle, Spacer, Paragraph, Frame
from reportlab.lib.pagesizes import letter,A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet, TA_CENTER
from reportlab.lib.units import inch, cm
from reportlab.lib import colors
from reportlab.pdfgen.canvas import Canvas
from functools import partial
from utils import Utils
from data_access import Data_Access

from PyPDF2 import PdfFileMerger
from pdfrw import PdfReader
from pdfrw.toreportlab import makerl
from pdfrw.buildxobj import pagexobj

class Report:

        
    def __init__(self,web_map_as_json,layer, title, subtitle, templateMXD, engie_logo):
        try:
            
            arcpy.AddMessage("INIT REPORT")
            self.title = title
            self.subtitle = subtitle
            self.report_elements = []
            self.engie_logo = engie_logo
            #self.__build_title_subtitle()
            layer_json = layer.replace('\\n','')
            #layer_json = str(''.join(layer.replace('\\n','')).encode('utf-8'))
            self.layer_obj = json.loads(layer_json)
            self.templateMXD = templateMXD
            
            self.utils = Utils()
            self.data_access = Data_Access(self.layer_obj)
            self.web_map_as_json = web_map_as_json.replace('\\n','')
            self.web_map_as_pdf = ""

        except Exception as ex:
            print(ex)
            arcpy.AddMessage(ex)
            

    def generate(self):
        try:
            self.__build_table()
            self.__build_relationship_table()
            self.__build_web_map()
            self.__build_pdf()
        except Exception as ex:
            print(ex)
            arcpy.AddMessage(ex)

    def __build_web_map(self):
        arcpy.AddMessage("BUILD WEB MAP")
        template_mxd = self.templateMXD
        path_webmap_img = arcpy.env.scratchWorkspace

        result = arcpy.mapping.ConvertWebMapToMapDocument(self.web_map_as_json, template_mxd)
        mxd = result.mapDocument
        df = arcpy.mapping.ListDataFrames(mxd, 'Webmap')[0]

        output = 'webmap_{}.pdf'.format(str(uuid.uuid1()))

        self.web_map_as_pdf = os.path.join(path_webmap_img, output)
        arcpy.mapping.ExportToPDF(mxd, self.web_map_as_pdf, df_export_width = 400,df_export_height =680, resolution = 150)

        del mxd

    def __build_table(self):
        arcpy.AddMessage("BUILD TABLE")
        data = self.data_access.get_data()
        arcpy.AddMessage("data ")
        data_table = data['data_table']
        arcpy.AddMessage("data_table")
        title_table = self.layer_obj['layer']['title']
        self.__build_title_table(title_table)
        table_principal = Table(data_table,colWidths=[8 * cm, 12 * cm])
        style = self.__table_style(len(data_table))
        table_principal.setStyle(style)

        self.report_elements.append(table_principal)
        self.__set_spacer(0.1)

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
            df = []
        
            for uuid in uuids:
                uuid_name = uuid['name']
                uuid_df = uuid['display_field']
                files_attach = self.data_access.get_attachments_in_folder(uuid_name)
                for file in files_attach:
                    path_img = '{}{}\\{}'.format(arcpy.env.scratchWorkspace,uuid_name,file)
                    img_attach = Image( path_img)
                    img_attach._restrictSize(3*inch, 3*inch)
                    file_img.append(img_attach)
                    df.append(uuid_df)

                    if len(file_img) == 2:
                        data.append(file_img)
                        data.append(df)
                        file_img = []
                        df = []

                if len(file_img) > 0:
                    data.append(file_img)
                    data.append(df)
        
                if len(data) > 0:
                    self.__set_position_attach(data)
        except Exception as ex:
            print(ex)
            arcpy.AddMessage(ex.message)
    
    def __title_table_style(self):
         return TableStyle([
            ('BACKGROUND', (0,0),(4,0), "#00AAFF"),
            ('TEXTCOLOR',(0,0),(-1,0), colors.white),
            ('ALIGN',(0,0),(-1,-1),'CENTER'),
            ('FONTSIZE', (0,0), (-1,0), 11),
            ('BOTTOMPADDING', (0,0), (-1,0), 12),
            # ('BOX', (0,0), (-1,-1), 0.25, colors.black)
        ]) 

    def __table_style(self, lines):
        
        return TableStyle([
            ('BACKGROUND', (0,0),(0,lines), '#00AAFF'),
            ('BACKGROUND', (1,0),(1,-1), '#e7f7ff'),
            ('TEXTCOLOR',(0,0),(0,-1), colors.white),
            ('ALIGN',(0,0),(-1,-1),'LEFT'),
            ('FONTSIZE', (0,0), (-1,0), 10),
            ('LINEABOVE', (0,0), (-1,-1), 0.25, colors.white),
            # ('BOTTOMPADDING', (0,0), (-1,0), 12)
        ])


    def __build_title_subtitle(self):
       
        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name='Center1', alignment=TA_CENTER))
        title_header = '<font size="18">'+self.title + '</font><br /><br />\n<font size="13">' + self.subtitle + '</font>'
        img = Image(self.engie_logo,1.8 * inch, 1.3 * inch)
        table_header = Table([[img,Paragraph(title_header, styles['Center1'])]],colWidths=[1 * cm,19 * cm],rowHeights =[2.5* cm])
        style = self.__build_style_header()    
        table_header.setStyle(style)
            
        #self.report_elements.append(table_header)
        #self.__set_spacer(0.2)
        return [table_header]

    def header(canvas, doc, content):
        canvas.saveState()
        w, h = content.wrap(doc.width, doc.topMargin)
        content.drawOn(canvas, doc.leftMargin, doc.height + doc.topMargin - h)
        canvas.restoreState()
            
    def __build_style_header(self):
        return TableStyle([
            ('TEXTCOLOR',(0,0),(0,-1), colors.black),
            ('VALIGN',(1,0),(-1,-1),'MIDDLE'),
            ('VALIGN',(0,0),(-1,-1),'MIDDLE'),
            ('ALIGN',(0,0),(-1,-1),'LEFT'),
            ('BOX', (0,0), (-1,-1),0.25,colors.gray),
            ('BOTTOMPADDING', (0,0), (-1,0), 10)
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
        arcpy.AddMessage('finish Create table')
        style = self.__table_style_images()
        arcpy.AddMessage('STYLE')
        table_img.setStyle(style)
        self.report_elements.append(table_img)

    @staticmethod
    def _header_footer(canvas,doc):
        canvas.saveState()
        styles = getSampleStyleSheet()
        # Footer
        footer = Paragraph('', styles['Normal'])
        w, h = footer.wrap(doc.width, doc.bottomMargin)
        footer.drawOn(canvas, doc.leftMargin, h)

        # Release the canvas
        canvas.restoreState()

    def __build_pdf(self):
        try:
            arcpy.AddMessage("SimpleDocTemplate")
            uniqueID = str(uuid.uuid1())
            path_report = os.path.join(arcpy.env.scratchWorkspace, 'report_{0}.pdf'.format(uniqueID))
            path_report_merged = os.path.join(arcpy.env.scratchWorkspace, 'report_{0}_merged.pdf'.format(uniqueID))

            arcpy.AddMessage(path_report)
            doc = SimpleDocTemplate(path_report, pagesize=A4,showBoundary=0, leftMargin=0,rightMargin=0, topMargin=95, bottomMargin=45, allowSplitting=1)

            doc.build(self.report_elements)
            arcpy.AddMessage("INIT MERGE")
          
            merger = PdfFileMerger()
            merger.append(path_report)
            merger.append(self.web_map_as_pdf)

            arcpy.AddMessage("WRITE MERGE")
            
            merger.write(path_report_merged)       
            merger.close()
            arcpy.AddMessage("CLOSE MERGE")
            self.__set_page_number(path_report_merged)

            arcpy.AddMessage("build completed!")
            arcpy.SetParameter(4, path_report_merged)

        except Exception as ex:
            print(ex)
            arcpy.AddMessage(ex.message)

    def __set_page_number(self, path_report):
        try:
            reader = PdfReader(path_report)
            pages = [pagexobj(p) for p in reader.pages]
                

            canvas = Canvas(path_report)

            for page_num, page in enumerate(pages, start=1):

                # Add page
                canvas.setPageSize((page.BBox[2], page.BBox[3]))
                canvas.doForm(makerl(canvas, page))

                # Draw footer
                footer_text_main = "ENGIE BRASIL ENERGIA S.A."
                footer_text_address = "Rua Paschoal Apóstolo Pítsica, 5064 - 88025-255 - Florianópolis - Santa Catarina - Brasil"
                footer_text_page = "Página %s de %s" % (page_num, len(pages))
                x1 = 75
                x2 = 360
                x3 = 480
                
                canvas.saveState()

                
                header_text = self.__build_title_subtitle()
                f = Frame(inch, inch, 6.26*inch, 10.5*inch)
                
                f.addFromList(header_text,canvas)
                                    
                canvas.setFont('Times-Roman', 10)
                canvas.drawString(page.BBox[2]-x2, 40, footer_text_main)
                canvas.drawString(page.BBox[2]-x3, 20, footer_text_address)
                canvas.drawString(page.BBox[2]-x1, 20, footer_text_page)
                canvas.restoreState()

                canvas.showPage()

            canvas.save()
        except Exception as ex:
            print(ex)
            arcpy.AddMessage(ex.message)
            

