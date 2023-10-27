from SPARQLWrapper import SPARQLWrapper, JSON
import sys

import networkx as nx
import networkx.algorithms.community as nx_comm


import numpy as np
import pandas as pd
from collections import Counter

import powerlaw
import math
import random

import matplotlib
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import matplotlib.cm as cm

import sys
sys.path.append('./utils')

from utils import *

class Network:
    
    def __init__(self):
      #  self.utils = Utils()
        return
    def create_subgraph(self,G,album_id,album_title,artist_id,artist_name,nb_album,role) :
        artist_id = np.int64("999" + str(artist_id))
        album_id = np.int64(album_id)
        if not G.has_node(album_id) :
            nb_album += 1
            G.add_node(album_id,title= album_title, type='Album' )

        if role.upper().startswith("A&R") :
            return (G,nb_album)    
        if not G.has_node(artist_id) : 
            G.add_node(artist_id,name = artist_name, type='Artist' )

        if not G.has_edge(album_id,artist_id) :   
            G.add_edge(album_id,artist_id,weight = 1)    
        else :
            G[album_id][artist_id]['weight'] = G[album_id][artist_id]['weight'] + 1    
       
        return (G,nb_album)    

    def build_bipartite_network(self,df,albums_json) :  
        G = nx.Graph()
        nb_album = 0
        for i in range(0,len(df)):

            role = df['role'][i]
            #if role.upper().startswith("A&R") :
            #   continue
            album_id = df['album_id'][i]
            album_title = df['title'][i]
            artist_id = df['artist_id'][i]
            artist_name = df['artist_name'][i]
            G,nb_album = self.create_subgraph(G,album_id,album_title,artist_id,artist_name,nb_album,role)
            
        #Json part 
        for alb_tuple in albums_json :      
            tuple_album = self.utils.get_albums_info_from_json(alb_tuple) 
            album_id = tuple_album[0]
            album_title = tuple_album[1]
            for art in tuple_album[2] :
                role = art["role"]
                if 'Compilation' in str(tuple_album[3]) :
                     continue
                artist_id = art["id"]
                artist_name = art["name"]
                role = art["role"]
                 
                G,nb_album= self.create_subgraph(G,album_id,album_title,artist_id,artist_name,nb_album,role)

        return (G,nb_album)
        
    def build_album_projection_network(self,results) :  
       
        G = nx.Graph()
        for alb in results:
            G.add_node(alb['id'], name=alb['title'], col = alb['artists'])
            
            for neighbor in G.nodes(data=True):  #Check for mutual collaboration     
                if neighbor[0] == alb['id'] : #same node 
                    continue
                
                artists = neighbor[1]['col']
                col_set = set()
                for art in alb['artists']:
                    for neighbor_art in artists :
                        if neighbor_art['id'] == art['id'] :
                            if neighbor_art['id'] not in col_set :
                                col_set.add(neighbor_art['id'])
                                if not G.has_edge(alb['id'],neighbor[0]) :
                                        G.add_edge(alb['id'],neighbor[0],weight = 1)    
                                else :
                                        G[alb['id']][neighbor[0]]['weight'] = G[alb['id']][neighbor[0]]['weight'] + 1 

        #remove artists attribut/ allow to save 
        for (n,d) in G.nodes(data=True):
            del d["col"]
        
        return G   
 


    def build_collaborators_projection_network(self,results) :
        G = nx.Graph()
        for alb in results:
            artists = alb['artists']
            for i in range(0,len(artists)-1):  #Check for mutual collaboration     
                treated = set()
                for j in range(i+1,len(artists)): 
                    art_in = artists[i]
                    art_out = artists[j] 

                    if art_out['id'] in treated or art_in['id'] in treated  or  art_in['id'] == art_out['id'] :
                        continue    

                    treated.add(art_in['id'])
                    if not G.has_node(art_in['id']) :
                        G.add_node(art_in['id'], name = art_in['name'])                        
                    if not G.has_node(art_out['id']):
                        G.add_node(art_out['id'], name = art_out['name'])     
                

                    if not G.has_edge(art_in['id'],art_out['id']) :
                        G.add_edge(art_in['id'],art_out['id'],weight = 1)    
                    else :
                        G[art_in['id']][art_out['id']]['weight'] = G[art_in['id']][art_out['id']]['weight'] + 1  
        return G
    
    def save_graph(self,g,path) :
        nx.write_gexf(g,path)

    def get_network_info(self,g):
        print("nb nodes: ",len(g.nodes))
        print("nb edges: ",len(g.edges))
        deg = dict(nx.degree(g))
        deg = list(deg.values())
        print("Min node degree: ",np.min(deg))
        print("Max node degree: ",np.max(deg))
        print("Avg node degree: ",np.mean(deg))


    def get_degree_centrality(self,g):
        degree_centralities =nx.degree_centrality(g).values()
        print(np.max(degree_centralities))
        print(np.min(degree_centralities))
        print(np.avg(degree_centralities))

    def get_pearson_correlation(self,g):
        r = nx.degree_pearson_correlation_coefficient(g)
        print(f"{r:3.1f}")    


    def get_avg_clustering_coefficent(self,g) :
        print("Average clustering coefficient : ", nx.average_clustering(g))


    def plot_hist_clustering_coeff_by_Amount(self,g) :
        clustering_coefficients= nx.clustering(g).values()
        clustering_coefficients_occ = Counter(clustering_coefficients)

        fig, ax = plt.subplots()
        plt.hist(clustering_coefficients,bins=10)

        plt.ylabel("Amount")
        plt.xlabel("Local Clustering coefficient")
        plt.savefig("local-clust-coeff_hist_log.eps", format="eps")
        plt.show()


    def get_transitivity(self,g):
        print("Transitivity : ", nx.transitivity(g))