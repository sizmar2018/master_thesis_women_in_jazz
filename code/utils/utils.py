import json
import configparser
import numpy as np
import pandas as pd
import re 
from bs4 import BeautifulSoup
import csv
import sys
from SPARQLWrapper import SPARQLWrapper, JSON

class Utils:
    
    def __init__(self,config_path = None):
        if config_path != None :
            self.config = configparser.ConfigParser()
            self.config.read(config_path)
    
    #write content of Wikipedia instruments HTML page to a csv file 
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
        instruments = pd.read_csv('../../data/instruments/instruments.csv',sep=',')
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
            if  r_strip not in 'nan' :   
                clean_roles.append(r_strip)
        
        return list(set(clean_roles))    

    def cluster_role_mfj(self,roles) :
        clean_roles = self.cluster_role(roles)
        clean_roles_final = list()
        for r in clean_roles :
            if 'voice' in r :
                if 'vocal' not in clean_roles_final :
                    clean_roles_final.append('vocal')
            else :
                r_clean = re.sub(r"\/(\W|\w)*", "", r)    
                clean_roles_final.append(r_clean)

        return clean_roles_final        


    #Clean the role syntax and cluster then into smallest roles
    def clean_role(self,roles,is_alb_data) :
       
        roles = roles.lower()
        roles = re.sub(r"\b[0-9]+\b\s*", "", roles)#remove numbers
        roles = re.sub("by", "", roles)
        roles = re.sub("-", " ", roles)
        roles = re.sub(r"\[([A-Za-z0-9_\s\S,]+)\]","", roles)#remove full []
        roles = re.sub(r"\[([\s]*)\]","", roles)#remove empty []
        roles = roles.split(',')

        if is_alb_data :
            clean_roles = self.cluster_role(roles)
        else : 
            clean_roles = self.cluster_role_mfj(roles)

        return clean_roles 

    def clean_artist_name(self,name) :
        clean_name = name.lower()
        clean_name = re.sub(r"\(([0-9]+)\)", "", clean_name)
        clean_name = clean_name.strip()
        return clean_name
    
    def check_musician_role(self,role) :
        musician_role = pd.read_csv("../../data/roles/musician_role_only.csv",sep=',') 
        clean_role = list()
        #print(musician_role['role'])
        for r in role :
            for r2 in musician_role['role'] : 
                #print(r ,"-",r2)
                if r == r2: 
                  clean_role.append(r)

        return clean_role       
           
    def get_albums_info_from_json(self,tuple):
       
        albums_id = np.int64(tuple["id"])
        album_title = tuple["title"]
        album_description = tuple["formats"]
      
        if "descriptions" in album_description[0] :  
            album_description = album_description[0]["descriptions"]
        if 'Compilation' in album_description:
            return None
        
        extra_artists = tuple["extraartists"]
        main_artist_id = set()
        for main_artist in tuple["artists"] :
            if  main_artist['id'] not in main_artist_id :
                    main_artist_id.add(main_artist['id'])
       
        artists = list()
        for art in extra_artists : 
       
            clean_roles = self.clean_role(art["role"],True) 
            clean_roles = self.check_musician_role(clean_roles)

            clean_name = self.clean_artist_name(art["name"])
            if art["id"] in main_artist_id : 
                clean_roles.append("main artist")
                main_artist_id.remove(art["id"])    
            if len(clean_roles) !=0:
                artists.append({"id":art["id"],"name": clean_name,"role": clean_roles})

        for main_artist in tuple["artists"]  :
              if main_artist['id'] in main_artist_id :
                artists.append({"id":main_artist["id"],"name": main_artist['name'],"role": ["main artist"]}) 
        #label
        label = tuple['labels'][0]['name'].split(",")
        return (albums_id,album_title,artists,label)  

    
    def get_concert_genres(self,concert_id) : 
        
        endpoint_url = "https://query.wikidata.org/sparql"
        query = """SELECT  (group_concat(DISTINCT ?genre_name ;separator=";") as ?genre_names) 
        WHERE { 
            { ?concert_mjf wdt:P8300 ?wd_item } .
            { ?concert_mjf wdt:P8300 ?wd_id } .
            
            OPTIONAL { ?concert_mjf wdt:P361 ?wd_part_of } .
            OPTIONAL { ?concert_mjf wdt:P136 ?wd_genre } .
            SERVICE wikibase:label { 
                bd:serviceParam wikibase:language "en" .
                ?wd_genre rdfs:label ?genre_name .
            }
            FILTER(?wd_id =  """ + "\"" + str(concert_id) + "\"" + """)
        }
        
        """

        user_agent = "WDQS-example Python/%s.%s" % (sys.version_info[0], sys.version_info[1])
        # TODO adjust user agent; see https://w.wiki/CX6
        sparql = SPARQLWrapper(endpoint_url, agent=user_agent)
        sparql.setQuery(query)
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert() 
        return results["results"]["bindings"][0]['genre_names']['value'].split(';')

    def get_concert_info_from_json(self,tuple):

        concert_id = np.int64(tuple["id"])
        concert_name = tuple["name"]
        concert_location = tuple["location"]
        concert_date = tuple["date"]
        #concert_genres = self.get_concert_genres(concert_id)
        concert_genres =  tuple["genres"]

        musicians = tuple["musicians"]

        artists = list()
        for m in musicians : 
            #clean_roles = self.clean_role(','.join(m["instruments"]),is_alb_data = False) 
            #clean_name = self.clean_artist_name(m["name"]) 
            artists.append({"id":m["id"],"name": m['name'],"role": m['role']})

        return (concert_id,concert_name,artists,concert_date,concert_location,concert_genres)  


    def load_data_top_5000_albums(self):
        df = pd.read_csv(self.config['DEFAULT']['TOP_5000_PATH'],sep=",")
        df = df.reset_index()
        albums_json = None
        with open(self.config['DEFAULT']['MISSING_ALBUM_PATH'],encoding="UTF-8") as f:
            albums_json = json.load(f)      

        return (df,albums_json)    

 