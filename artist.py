import re


def get_name(data):
    band_name = re.sub('<.*?>', '', data[0]).replace("  ", " ")
    return is_aka_name(band_name)


def is_aka_name(band_name):
    if 'a.k.a.' in band_name:
        aka = band_name[band_name.find("(") + 1:band_name.find(")")].replace(
            'a.k.a. ', '')
        band_name = band_name[:band_name.find("(") - 1]
        return band_name, aka
    else:
        return band_name, None


def get_genre(data):
    return data[1].replace(",", " - ").replace("/", " - ").replace("\\", " -  ").replace("  ", " ")


def get_id(data):
    band_id = re.findall('//(.*?)">*', data[0], re.DOTALL)
    band_id = band_id[0].replace("bands/", "")
    return re.sub('^.*?/.*?/', '', band_id)


def get_country_code(country_name):
    """Function to convert country name to country code"""
    import csv
    doc = csv.reader(open('country_code.csv', "rt", encoding="UTF-8"), delimiter=",")
    for line in doc:
        if str(country_name) in str(line[0]):
            return line[1]
            break
    # if don't find country in file
    return "xxx"


class Band:
    def __init__(self):
        self.id = ''
        self.name = ''
        self.aka = ''
        self.genre = ''
        self.country = ''
        self.discography = []

    def set_band_data(self, data):
        band = Band()
        # if band don't have aka title ma_band.aka = None
        band.name, band.aka = get_name(data)
        band.id = get_id(data)
        band.genre = get_genre(data)
        band.country = get_country_code(data[2])
        return band
