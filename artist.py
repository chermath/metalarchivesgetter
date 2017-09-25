def band_to_string(band):
    band_string = band.name + "[" + band.country + ", " + band.genre + "]" + " id=" + band.id
    if band.aka:
        band_string += " (" + band.aka + ")"
    return band_string


class Band():
    def __init__(self):
        self.id = ''
        self.name = ''
        self.aka = ''
        self.genre = ''
        self.country = ''
        self.discography = []


    #def __getattr__(self, item):
    #    return self[item]