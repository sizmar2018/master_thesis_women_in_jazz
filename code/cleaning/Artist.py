

class Artist(object):
  
  def __init__(self,id,name,roles):
    self.id = id
    self.name = name
    self.roles = roles
   

  def to_dict(self):
        
        return {
            'id': self.id,
            'name': self.name,
            'role' : self.roles,
           
        }   
