import json
import configparser
import numpy as np
import pandas as pd
import re 
from bs4 import BeautifulSoup
import csv

class Utils:
    
    def __init__(self,config_path = None):
        if config_path != None :
            self.config = configparser.ConfigParser()
            self.config.read(config_path)
    
    def get_instruments() :
        
        url = "../../data/instruments.html"
        page = open(url)
        soup = BeautifulSoup(page.read())
        ul = soup.find("ul")
        with open('../../data/instruments.csv', 'w', encoding='Windows-1252') as f:
            for li in ul.findChildren('li',recursive=False) :
                main_inst = li.find('a').text
                sub_ul = li.find('ul')  
                sub_instruments = ''
                if sub_ul != None :
                    for sub_li in sub_ul.findChildren('li',recursive=False) : 
                        sub_inst = sub_li.find('a').text
                        sub_inst = sub_inst.replace("\n","")
                        sub_instruments += sub_inst +  ","
                sub_instruments = sub_instruments + main_inst
                csv_line = (main_inst,sub_instruments)
                w = csv.writer(f)
                w.writerow(csv_line)


    def cluster_role(self,roles) : 
        instruments = pd.read_csv('../../data/instruments.csv',sep=',')
        instruments['sub_instru'] = instruments['sub_instru'].apply(lambda x :x.split(','))
        clean_roles = list()
        for r in  roles :          
            r_strip = r.strip()
            is_found = False
            for i in range(0,len(instruments)) :
                for inst in instruments['sub_instru'][i] :
                    if  inst.lower() in  r_strip: 
                        r_strip = instruments['instru'][i].lower()
                        is_found = True
                if is_found :
                    break        
            clean_roles.append(r_strip)
        clean_roles  = list(set(clean_roles))
        return clean_roles    

    def clean_role(self,roles) :
       
        roles = roles.lower()
        roles = re.sub(r"\b[0-9]+\b\s*", "", roles)#remove numbers
        roles = re.sub("by", "", roles)
        roles = re.sub("-", " ", roles)
        roles = re.sub(r"\[([A-Za-z0-9_\s\S,]+)\]","", roles)#remove full []
        roles = re.sub(r"\[([\s]*)\]","", roles)#remove empty []
        roles  = roles.split(',')

        clean_roles = self.cluster_role(roles)
       
        return clean_roles 

    def clean_artist_name(self,name) :
        clean_name = name.lower()
        clean_name = re.sub(r"\(([0-9]+)\)", "", clean_name)
        clean_name = clean_name.strip()
        return clean_name

    def get_albums_info_from_json(self,tuple):
       
        albums_id = np.int64(tuple["id"])
        album_title = tuple["title"]
        album_description = tuple["formats"]
        album_style =  None
        if "styles" in tuple :  
              album_style =  tuple["styles"]
        if "descriptions" in album_description[0] :  
            album_description = album_description[0]["descriptions"]
        if 'Compilation' in album_description:
            return None
        
        extra_artists = tuple["extraartists"]
        artists = list()
        
        for art in extra_artists : 
            clean_roles = self.clean_role(art["role"]) 
            clean_name =  self.clean_artist_name(art["name"])
            artists.append({"id":art["id"],"name":clean_name,"role": clean_roles})
        #label
        label = tuple['labels'][0]['name']
        return (albums_id,album_title,artists,label,album_style)  

    def load_data_top_5000_albums(self):
        df = pd.read_csv(self.config['DEFAULT']['TOP_5000_PATH'],sep=",")
        df = df.reset_index()
        albums_json = None
        with open(self.config['DEFAULT']['MISSING_ALBUM_PATH'],encoding="UTF-8") as f:
            albums_json = json.load(f)      

        return (df,albums_json)    

 