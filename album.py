import artist

class Album():
    def __init__(self):
        self.name = ''
        self.type = ''
        self.year = ''
        self.tracks = ''
        self.artist = artist.Band()
    def album_to_string(self, album):
        return album.year + " - " + album.name + "[" + album.type + "]"
#    def __getattr__(self, item):
#        self[item]