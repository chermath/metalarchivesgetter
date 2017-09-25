import artist

def album_to_string(album):
    return album.year + " - " + album.name + "[" + album.type + "]"

class Album():
    def __init__(self):
        self.name = ''
        self.type = ''
        self.year = ''
        self.tracks = ''
        self.artist = artist.Band()

#    def __getattr__(self, item):
#        self[item]