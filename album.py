import artist
class Album():
    def __init__(self):
        self.title = ''
        self.type = ''
        self.year = ''
        self.tracks = ''
        self.artist = artist.Band()

#    def __getattr__(self, item):
#        self[item]