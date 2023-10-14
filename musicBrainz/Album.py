class Album(object):
  
  def __init__(self,title,artists,countries,year,labels):
    
    self.title = title
    self.artists = artists
    self.countries= countries
    self.year= year
    self.labels= labels
 
 

  def to_dict(self):
        
        return {
            'title': self.title,
            'artists': self.artists,
            'countries' : self.countries,
            'year' : self.year,
            'labels' : self.labels,
        }   
  
 