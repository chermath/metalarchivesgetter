#!/usr/bin/env python3
import argparse
import json
import os
import re
from urllib.request import urlopen
from urllib.parse import urlencode

import sys
# import urllib2
from bs4 import BeautifulSoup
# from jsonpipe import jsonpipe

import ajax_ma
import album
import artist
import discography

site_url = 'http://www.metal-archives.com/'
site_url_without_html = 'www.metal-archives.com/bands/'
ajax_song = 'search/ajax-advanced/searching/songs?'
ajax_album = 'search/ajax-advanced/searching/albums?'
ajax_band = 'search/ajax-advanced/searching/bands?'
ajax_query_album = 'search/ajax-album-search/?query='
ajax_query_band = 'search/ajax-band-search/?'
lyrics_not_available = '(lyrics not available)'
lyric_id_re = re.compile(r'id=.+[a-z]+.(?P<id>\d+)')
band_name_re = ""
tags_re = re.compile(r'<[^>]+>')
# band_albums_re = re.compile(r'albums=.*\">(?P<albums>*</a>')
band_albums_song_number_re = 0
band_albums_song_name_re = ''
band_albums_songs_total_numbers_re = 0
# band_name = ''
albums_data = dict()


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
        return True if name1.lower() == name2.lower() else False

    def get_ma_album(self, sought_album):
        disco = self.get_discography(self.ma_band.id)
        self.set_headings(disco)
        # extract to albums data from ma site to readable labels eg. year, album name
        for row in disco.find_all("tr")[1:]:
            # TODO get the album ID
            new_album = self.prepare_dataset(disco, row)
            self.band_discography.albums.append(new_album)
            if self.compare_names(sought_album, new_album):
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
        self.ma_band.name = re.sub('<.*?>', '', data[0]).replace("  ", " ")
        # if band have aka title
        if 'a.k.a.' in self.ma_band.name:
            self.ma_band.aka = self.ma_band.name[self.ma_band.name.find("(") + 1:self.ma_band.name.find(")")].replace(
                'a.k.a. ', '')
            self.ma_band.name = self.ma_band.name[:self.ma_band.name.find("(") - 1]
        # band_id = data[0].replace("<a href=\"" + site_url + "bands/", "")
        band_id = re.findall('//(.*?)">*', data[0], re.DOTALL)
        band_id = band_id[0].replace("bands/", "")
        self.ma_band.id = re.sub('^.*?/.*?/', '', band_id)
        self.ma_band.genre = data[1].replace(",", " - ").replace("/", " - ").replace("\\", " -  ").replace("  ", " ")
        self.ma_band.country = self.get_country_code(data[2])

    def get_country_code(self, country_name):
        """Function to convert country name to country code"""
        import csv
        doc = csv.reader(open('country_code.csv', "rt", encoding="UTF-8"), delimiter=",")
        country_nr = "0"
        for line in doc:
            if str(country_name) in str(line[0]):
                return line[1]
                break
        # if don't find country in file
        return "xxx"

    def get_ma_band(self, band):
        results = self.ajax_ma.band_ma_query(band)
        # any results ? so create empty band
        # if results['iTotalDisplayRecords'] >=1:
        #    self.ma_band = band.Band()
        # if only one result (so we don't have to select anything
        if results['iTotalDisplayRecords'] == 1:
            for bands in results['aaData']:
                self.ma_band = artist.Band()
                self.create_band(bands)
                print(
                    self.ma_band.name + "[" + self.ma_band.country + ", " + self.ma_band.genre + "]" + " id=" + self.ma_band.id)
                if self.ma_band.aka:
                    print("(" + self.ma_band.aka + ")")

                    # choosen_band = dict(
                    #     id=band_id,
                    #     name=band_name,
                    #     country=band_country,
                    #     genre=band_genre_re
                    # )

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
              self.ma_band.name + " [" + self.ma_band.country + ", " + self.ma_band.genre + "]/" +
              self.ma_band.name + " - " + self.ma_album.year + " - " + self.ma_album.title)


if __name__ == '__main__':
    ma_searcher = ma_search()
    ma_searcher.main()
