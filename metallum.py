#!/usr/bin/env python3
import argparse
import json
import os
import re
from urllib.request import urlopen
# local imports
import ajax_ma
import album
import artist
import discography

site_url = 'http://www.metal-archives.com/'
tags_re = re.compile(r'<[^>]+>')


class ma_search():
    def __init__(self):
        self.ajax_ma = ajax_ma.AjaxMa()
        self.ma_band = ''
        self.ma_album = album.Album()
        self.band_discography = discography.Discography()
        self.headlines = []

    def fill_album(self, album_data):
        # create an object
        album_info = album.Album()
        # fill an album with data
        if 'Full-length' in album_data['Type']:
            album_type = 'LP'
        else:
            album_type = album_data['Type']
        album_info.year = album_data['Year']
        album_info.title = album_data['Name']
        album_info.type = album_type
        return album_info

    def get_discography(self, band_id):
        return self.ajax_ma.discography_ma_query(band_id)

    def set_headings(self, disco):
        self.headlines = [th.get_text() for th in disco.find("tr").find_all("th")]

    def prepare_dataset(self, disco, data_raw):
        dataset = zip(self.headlines, (td.get_text() for td in data_raw.find_all("td")))
        return self.fill_album(dict(dataset))

    def compare_names(self, name1, name2):
        return True if str(name1).lower() == str(name2).lower() else False

    def get_ma_album(self, sought_album):
        disco = self.get_discography(self.ma_band.id)
        self.set_headings(disco)
        # extract to albums data from ma site to readable labels eg. year, album name
        for row in disco.find_all("tr")[1:]:
            # TODO get the album ID
            new_album = self.prepare_dataset(disco, row)
            self.band_discography.albums.append(new_album)
            if self.compare_names(sought_album, new_album.title):
                self.ma_album = new_album
                print("searched album: " + self.ma_album.year + " - " + self.ma_album.title)
                print("############################")
                # print(new_album.)


                # print album_data
                # for album in albums_data:
                # print album['Name']
                # for row in rows:
                # print "url=" + row
                # listing_dirs()
                # url = site_url + ajax_query_album
                # if 1 == json.load(urlopen(url))['iTotalRecords']:
                #     url = "".join([site_url, ajax_query_album, urlencode(params)])
                #     return json.load(urlopen(url))['aaData']
                # else:
                #     print "zonk"

    # def listing_dirs():
    #     for dirname, dirnames, filenames in os.walk('/home/matth/storage/MP3/torrent'):
    #         # print path to all subdirectories first.
    #         for subdirname in dirnames:
    #             if "[" in subdirname:
    #                 print(subdirname.partition("[")[0])
    #             elif "-" in subdirname:
    #                 substring = subdirname.partition("-")[0]
    #                 if len(substring) == 5:
    #                     print("len this is year: " + substring)
    #                 elif len(substring) > 5:
    #                     print(str(len(substring)) + "is len allmost sure band: " + substring)
    #                 else:
    #                     print("band? " + substring)
    #             #print(os.path.join(dirname, subdirname))
    def create_band(self, data):
        # self.ma_band = artist.Band()
        self.ma_band = artist.Band().set_band_data(data)

    def one_band_result(self, raw_data):
        return True if raw_data['iTotalDisplayRecords'] == 1 else False

    def get_ma_band(self, band):
        # create an object
        self.ma_band = artist.Band()
        results = self.ajax_ma.band_ma_query(band)
        if self.one_band_result(results):
            for band in results['aaData']:
                self.create_band(band)
                print(self.ma_band.name + "[" + self.ma_band.country + ", " + self.ma_band.genre + "]" + (" (a.k.a. " + self.ma_band.aka +")" if self.ma_band.aka else "") + " id=" + self.ma_band.id)
        # TODO for more than one band with the same name, selector should by by id ;)
        # user should choose
        # if 1 == json.load(urlopen(url))['iTotalRecords']:
        #    return json.load(urlopen(url))['aaData']
        # if
        # global band_data
        # band_data = choosen_band
        # print(os.path.isdir("/home/matth/inspiracja/Zrobione/" + band_data.band_name[0][0]) + "/" +)

    def get_lyrics_by_song_id(self, song_id):
        """Search on metal-archives for lyrics based on song_id"""
        url = "".join([site_url, "release/ajax-view-lyrics/id/", song_id])
        return tags_re.sub('', urlopen(url).read().strip()).decode('utf-8')

    def find_band(self, band):
        band_names = self.get_ma_band(band)
        # if (band_names >= 1):
        #    print "znaleziono wincyj zespolow"
        # TODO wyswietlic i dac do wybrania ;)
        # else:
        #    print "git"
        #    get_albums_artist
        # return band_names

    def main(self):
        """Runs the program and handles command line options"""
        parser = argparse.ArgumentParser(description='Get lyrics from http://metal-archives.com')
        parser.add_argument('band', type=str, help='The name of the band. Ex: "Vomigod"')
        parser.add_argument('album', type=str, help='The title of the song. Ex: "OralTrol"')
        args = parser.parse_args()
        self.get_ma_band(args.band)
        if not self.ma_band:
            print("cann't find " + args.band)
        else:
            self.get_ma_album(args.album)
        print("********************")
        print("output format=\n" +
              self.ma_band.name + " [" + self.ma_band.country + ", " + self.ma_band.genre + "]" + (" (a.k.a. " + self.ma_band.aka +")" if self.ma_band.aka else "") +
              "/" + self.ma_band.name + " - " + self.ma_album.year + " - " + self.ma_album.title)


if __name__ == '__main__':
    ma_searcher = ma_search()
    ma_searcher.main()
