
class Concert(object):
  
  def __init__(self,id,name,artists,date,location):
    
    self.id = id
    self.name = name
    self.artists = artists
    self.date = date
    self.location= location
 

  def to_dict(self):
        
        return {
            'id': self.id,
            'name': self.name,
            'musicians': self.artists,
            'date' : self.date,
            'location' : self.location,        
        }   
  
