
class Album(object):
  
  def __init__(self,id,title,artists,year,labels,rank,rating,genres):
    
    self.id = id
    self.title = title
    self.artists = artists
    self.genres= genres
    self.year= year
    self.labels= labels
    #self.styles = styles
    self.rank = rank
    self.rating = rating
 

  def to_dict(self):
        
        return {
            'id': self.id,
            'title': self.title,
            'artists': self.artists,
            'year' : self.year,
            'labels' : self.labels,
           # 'styles' : self.styles,
            'rank': self.rank,
            'rating': self.rating,
            'genres' : self.genres
        }   
  
