import json
import configparser
import numpy as np
import pandas as pd
import re 

class Utils:
    
    def __init__(self,config_path = None):
        if config_path != None :
            self.config = configparser.ConfigParser()
            self.config.read(config_path)

    def clean_role(self,role) : 
        role = role.lower()
        role = re.sub("by", "", role)
        role = re.sub("-", " ", role)
        role = re.split(r"\[([A-Za-z0-9_\s\S,]+)\]", role)[0]
        return role 

    def get_albums_info_from_json(self,tuple):
        
        albums_id = np.int64(tuple["id"])
        album_title = tuple["title"]
        album_description = tuple["formats"]
       
        if "descriptions" in album_description[0] :  
            album_description = album_description[0]["descriptions"]
        if 'Compilation' in album_description:
            return None
        
        extra_artists = tuple["extraartists"]
        artists = list()
        
        for art in extra_artists : 
            clean_roles = list()
            for r in art["role"]:
                role = self.clean_role(r)   
                role = role.strip()
                if "a&r" not in role :
                    clean_roles.append(role)
            artists.append({"id":art["id"],"name":art["name"],"role": clean_roles})
        #label
        label = tuple['labels'][0]['name']
        return (albums_id,album_title,artists,label)  

    def load_data_top_5000_albums(self):
        df = pd.read_csv(self.config['DEFAULT']['TOP_5000_PATH'],sep=",")
        df = df.reset_index()
        albums_json = None
        with open(self.config['DEFAULT']['MISSING_ALBUM_PATH'],encoding="UTF-8") as f:
            albums_json = json.load(f)      

        return (df,albums_json)    

 