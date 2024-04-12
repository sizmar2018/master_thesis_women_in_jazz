import networkx as nx
import networkx.algorithms.community as nx_comm


import numpy as np
import pandas as pd
from collections import Counter
from collections import defaultdict

import powerlaw
from scipy import stats
import math
import random

import matplotlib
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import matplotlib.cm as cm

import sys
sys.path.append('./utils')

from utils import *

plot_color = "#8EACCD"

class Network:
    
    def __init__(self):
      #  self.utils = Utils()
        return
    
    def create_subgraph(self,G,album,artist,title_keyword,date_keyword,genre_keyword,is_role_specific,role=None) :
        
        artist_id = np.int64("999" + str(artist['id'])) #Albums and artists can have the same id
        album_id = np.int64(album['id'])
 
        if not G.has_node(album_id) : #subgenres
            #G.add_node(album_id, type='Album',name=album[title_keyword],byear=album[date_keyword],eyear=2024,genres=album[genre_keyword] if len(album[genre_keyword]) >= 0 else list())
             G.add_node(album_id, type='Album',name=album[title_keyword],byear=album[date_keyword],eyear=2024)
        if not G.has_node(artist_id) : 
            #G.add_node(artist_id, type='Artist',name = artist["name"],byear=album[date_keyword],eyear=2024,genres=set(album[genre_keyword]) if len(album[genre_keyword]) >= 0 else set(),
             #          subgenres=set(album["genres"]) if (len(album["genres"]) >= 0) and ('' not in album["genres"]) else set())
            G.add_node(artist_id, type='Artist',name = artist["name"],byear=album[date_keyword],eyear=2024)
       # else: 
        #    G.nodes[artist_id]['genres']|=set(album[genre_keyword])
         #   G.nodes[artist_id]['subgenres']|=set(album["genres"])
      
      
        if not G.has_edge(album_id,artist_id) :   
            if is_role_specific : 
                if role not in artist['role'] :
                    G.add_edge(album_id,artist_id,weight = 1)     
            else :   
                G.add_edge(album_id,artist_id,weight = 1)            
        else :
            if is_role_specific : 
              if role not in artist['role'] :
                G[album_id][artist_id]['weight'] = G[album_id][artist_id]['weight'] + 1  
            else :
                G[album_id][artist_id]['weight'] = G[album_id][artist_id]['weight'] + 1    
       
        return G  
    
    def build_bipartite_network(self,results,title_keyword,artist_keyword,date_keyword,genre_keyword,date_min=None,data_max=None) :  
        G = nx.Graph()
        for alb in results :    
            #if int(alb[date_keyword].split("-")[0]) < 2000   :
            if date_min != None :
                if int(alb[date_keyword].split("-")[0]) >= date_min and int(alb[date_keyword].split("-")[0]) <= data_max :    
                    for art in alb[artist_keyword] :         
                            G = self.create_subgraph(G,alb,art,title_keyword,date_keyword,genre_keyword,False)
            else : 
                for art in alb[artist_keyword] :         
                   G = self.create_subgraph(G,alb,art,title_keyword,date_keyword,genre_keyword,False)
        return G



    def build_role_specific_network(self,results,title_keyword,artist_keyword,date_keyword,genre_keyword,role) :
        G = nx.Graph()
        for alb in results :    
            for art in alb[artist_keyword] :            
                G = self.create_subgraph(G,alb,art,title_keyword,date_keyword,genre_keyword,True,role)
        return G
  
    #deprecated
    def build_album_projection_network(self,results,title_keyword,part_keyword,date_keyword) :  


        """
        G = nx.Graph()
        for alb in results:
            if len(alb[part_keyword] ) == 0:  
                    continue
            G.add_node(alb['id'], name = alb[title_keyword], col = alb[part_keyword],byear=alb[date_keyword],eyear=2024)
           # print(alb['id'])
            for neighbor in G.nodes(data=True):  # Check for mutual collaboration     
                
                if neighbor[0] == alb['id'] : #same node 
                    continue
                
                artists = neighbor[1]['col']
                col_set = set()
                for art in alb[part_keyword]:
                    for neighbor_art in artists :
                        if neighbor_art['id'] == art['id'] and neighbor_art['id'] not in col_set:
                            
                                col_set.add(neighbor_art['id'])
                                if not G.has_edge(alb['id'],neighbor[0]) :
                                        G.add_edge(alb['id'],neighbor[0],weight = 1,byear=alb[date_keyword],eyear=2024)   
                                else :
                                        G[alb['id']][neighbor[0]]['weight'] = G[alb['id']][neighbor[0]]['weight'] + 1 
                                      
        
        #remove artists attribut/ allow to save 
        for (n,d) in G.nodes(data=True):
            del d["col"]
        
        return G   
    """

    #deprecated
    def build_collaborators_projection_network(self,results,idx_keyword,date_keyword) :
        G = nx.Graph()
        for alb in results:
            artists = alb[idx_keyword]
           
            if len(artists) == 1 :
                treated.add(artists[0]['id'])
                if not G.has_node(int(artists[0]['id'])) :
                        G.add_node(int(artists[0]['id']), name = artists[0]['name'],byear=alb[date_keyword],eyear=2024)     
                       

            for i in range(0,len(artists)-1):  #Check for mutual collaboration   
                treated = set()
                for j in range(i+1,len(artists)): 
                    art_in = artists[i]
                    art_out = artists[j] 
                  
                    if art_out['id'] in treated or art_in['id'] in treated  or art_in['id'] == art_out['id'] :
                        continue    

                    treated.add(art_in['id'])
                   
                    if not G.has_node(art_in['id']) :
                        G.add_node(art_in['id'], name = art_in['name'],byear=alb[date_keyword],eyear=2024)    
                        
                    if not G.has_node(art_out['id']):
                        G.add_node(art_out['id'], name = art_out['name'],byear=alb[date_keyword],eyear=2024)     
                        

                    if not G.has_edge(art_in['id'],art_out['id']) :
                        G.add_edge(art_in['id'],art_out['id'],weight = 1,byear=alb[date_keyword],eyear=2024)    
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


   #The	diameter of	the	graph is the maximum distance between any pair of its nodes.
    def get_diameter(self,g):
        print("Diameter : ", nx.diameter(g))

    def get_density(self,g) :
        print("Density : ", nx.density(g))

    def get_avg_weighted_degree(self,g) :
        print("Avg weighted degree : ", np.mean(nx.degree(g,weight='weight')))

    def get_avg_clustering_coefficent(self,g) :
        print("Average clustering coefficient : ", nx.average_clustering(g))

    def get_avg_path_length(self,g) :
          print("get_avg_path_length: ", nx.average_shortest_path_length(g))

    def get_nb_of_connected_comp(self,g) :
            print("Nb connected components : ", nx.number_connected_components(g))

    #Plot the clusting coefficient by degree(histogramme representation) and safe the plot   
    def plot_hist_clustering_coeff_by_amount(self,g) :
        clustering_coefficients= nx.clustering(g).values()
        clustering_coefficients_occ = Counter(clustering_coefficients)

        fig, ax = plt.subplots()
        nbins = math.ceil(math.sqrt(len(clustering_coefficients))) 
        print(nbins)
        plt.hist(clustering_coefficients,bins = 10,color=plot_color)

        plt.ylabel("Amount")
        plt.xlabel("Local Clustering coefficient")
        plt.savefig("../data/repartition/local-clust-coeff_hist.png", format="png")
        plt.show()


    #Plot the clusting coefficient by degree(points representation) and safe the plot   
    def plot_clustering_coeff_by_degree(self,g) :
        
        d = defaultdict(list)

        for u in g.nodes():
            d[g.degree(u)].append(u)

        clustering_coeffs=defaultdict(np.double)
        for degree in d:
            clustering_coeff = list(nx.clustering(g, d[degree]).values())
            clustering_coeffs[degree] = np.mean(clustering_coeff)

        fig, ax = plt.subplots()

        plt.plot(clustering_coeffs.keys(), clustering_coeffs.values(), 'o',color=plot_color)
        #ax.set_yscale('log')
        #ax.set_xscale('log')
        plt.ylabel("Average Clustering coefficient")
        plt.xlabel("Degree k")
        plt.savefig("../data/repartition/local-clust-coeff_degree.png", format="png")
        plt.show()


    def get_transitivity(self,g):
        print("Transitivity : ", nx.transitivity(g))


    #---------------------Centrality ----------------------------------

    #Compute the bipartite degree centrality
    #return musician_id,centrality in DESC order
    def get_bipartite_degree_centrality(self,g):
        degree_centralities = self.get_weighted_deg_centrality(g)
     
        top_degree_centrality =degree_centralities[0]
        top_degree_centrality_values =degree_centralities[1]
        ids = list()
        for id in top_degree_centrality :  
            if g.nodes[id]['type'] == "Artist" : 
                    ids.append(id)
        return ids,top_degree_centrality_values

    #Compute the degree centrality
    #return musician_id,centrality in DESC order
    def get_degree_centrality(self,g):
        degree_centralities = nx.degree_centrality(g)
        sort_degree = dict(sorted(degree_centralities.items(), reverse=True,key=lambda item: item[1]))
        top_degree_centrality_id = list(sort_degree.keys())
        top_degree_centrality = list(sort_degree.values())
        return top_degree_centrality_id,top_degree_centrality
    

    def get_weighted_deg_centrality(self,g):
        weighted_degree_centrality = {}
        for node in g.nodes:        
            weighted_degree = sum(weight for _, _, weight in g.edges(node, data='weight'))
            weighted_degree_centrality[node] = weighted_degree / (len(g.nodes) - 1)  # Normalize by n-1

        sort_degree = dict(sorted(weighted_degree_centrality.items(), reverse=True,key=lambda item: item[1]))
        top_degree_centrality_id = list(sort_degree.keys())
        top_degree_centrality = list(sort_degree.values())

        return top_degree_centrality_id,top_degree_centrality


    #Compute the betweenness centrality
    #return musician_id,centrality in DESC order
    def get_betweenness_centrality(self,g):
        between_centralities = nx.betweenness_centrality(g)
        sort_degree = dict(sorted(between_centralities.items(), reverse=True,key=lambda item: item[1]))
        top_between_centrality_id = list(sort_degree.keys())
        top_between_centrality = list(sort_degree.values())
        return top_between_centrality_id,top_between_centrality

    #Compute the eigenvector centrality
    #return musician_id,centrality in DESC order
    def get_eigenvector_centrality(self,g):
        eigen_centralities = nx.eigenvector_centrality_numpy(g, weight="weight")
        sort_degree = dict(sorted(eigen_centralities.items(), reverse=True,key=lambda item: item[1]))
        top_eigen_centrality_id = list(sort_degree.keys())
        top_eigen_centrality = list(sort_degree.values())
        return top_eigen_centrality_id,top_eigen_centrality


    def get_name_from_id(self,top10_degre_centrality,g) :
        names = list()
        for node in top10_degre_centrality :  
            print(g.degree[node[0]])
            names.append(g.nodes[node[0]]['name'])
        return names       


    #Compute Spearman correlation between degree,betweenness,eigenvector centralities
    def get_spearman_corr(self,g) : 
          
          degree_cen_k = self.get_weighted_deg_centrality(g)[1]
          betweenness_cen = self.get_betweenness_centrality(g)[1]
          eigenvector_cen = self.get_eigenvector_centrality(g)[1]
       
          print("Spearman corr between projected degree k and betweenness centrality is",stats.spearmanr(degree_cen_k, betweenness_cen))
          print("Spearman corr between projected degree k and eigenvector centrality is",stats.spearmanr(degree_cen_k, eigenvector_cen))
          print("Spearman corr between betweenness centrality and eigenvector centrality is",stats.spearmanr(betweenness_cen, eigenvector_cen))
          

   
    def get_pearson_correlation(self,g):
        r = nx.degree_pearson_correlation_coefficient(g)
        print(f"{r:3.1f}")    

