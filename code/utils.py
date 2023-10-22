import json
import configparser
import numpy as np
import pandas as pd

class Utils:
    
    def __init__(self,config_path = None):
        if config_path != None :
            self.config = configparser.ConfigParser()
            self.config.read(config_path)


    def get_albums_info_from_json(self,tuple):
        #print(tuple)
        albums_id = np.int64(tuple["id"])
        album_title = tuple["title"]
        album_description = tuple["formats"]
       
        if "descriptions" in album_description[0] :  
            album_description = album_description[0]["descriptions"]
        
        extra_artists = tuple["extraartists"]
        artists = list()
        for art in extra_artists : 
            artists.append({"id":art["id"],"name":art["name"],"role": art["role"]})
        #label
        #rank  
        return (albums_id,album_title,artists,album_description)  

    def load_data_top_5000_albums(self):
        df = pd.read_csv(self.config['DEFAULT']['TOP_5000_PATH'],sep=",")
        df = df.reset_index()
        albums_json = None
        with open(self.config['DEFAULT']['MISSING_ALBUM_PATH'],encoding="UTF-8") as f:
            albums_json = json.load(f)      

        return (df,albums_json)    

 