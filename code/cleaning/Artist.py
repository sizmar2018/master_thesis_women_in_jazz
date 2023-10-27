

class Artist(object):
  
  def __init__(self,id,name,roles,main=False):
    self.id = id
    self.name = name
    self.roles = roles
    self.main = main

  def to_dict(self):
        
        return {
            'id': self.id,
            'name': self.name,
            'role' : self.roles,
            'main' :self.main
        }   
