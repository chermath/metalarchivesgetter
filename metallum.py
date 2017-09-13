#!/usr/bin/env python
import json
import sys
import argparse
import re

import urllib2
import os

import album
import artist
from bs4 import BeautifulSoup
from urllib import urlopen, urlencode
from jsonpipe import jsonpipe
import ajax_ma
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


        # # band_genre_re
        # def get_songs_data(band, song):
        #     """Search on metal-archives for song coincidences"""
        #     params = dict(
        #         bandName=band,
        #         # songTitle = song
        #         releaseTitle=song
        #     )
        #     url = "".join([site_url, ajax_album, urlencode(params)])
        #     print "url=" + url
        #     return json.load(urlopen(url))['aaData']
        #
        #
    def fill_album(self, album_data):
        album_tmp = album.Album()
        if 'Full-length' in album_data['Type']:
            album_type = 'LP'
        else:
            album_type = album_data['Type']
        album_tmp.year = album_data['Year']
        album_tmp.title = album_data['Name']
        album_tmp.type = album_type
        return album_tmp

    def get_discography(self, band_id):
        params = dict(
            bandId=self.ma_band.id,
            releaseTitle=album
        )
        response = urllib2.urlopen('http://www.metal-archives.com/band/discography/id/' + self.ma_band.id + '/tab/all')
        html = response.read()
        #     # tmp = json.load("http://www.metal-archives.com/band/discography/id/3070/tab/misc")
        #     # url = "".join([site_url, ajax_album, urlencode(params)])
        soup = BeautifulSoup(html, "lxml")
        table = soup.find("table")
        # table = html.find('table')
        return table


    def get_ma_album(self, album):

        disco = self.get_discography(self.ma_band.id)

        headings = [th.get_text() for th in disco.find("tr").find_all("th")]

        for row in disco.find_all("tr")[1:]:
            dataset = zip(headings, (td.get_text() for td in row.find_all("td")))
            albums = dict(dataset)
            # print(str(albums['Name']))
            new_album = self.fill_album(albums)
            self.band_discography.albums.append(new_album)
            if album.lower() in new_album.title.lower():
                self.ma_album = new_album
                # albums_data[albums['Name']] = album_data
                # print album_data
                # print albums.keys()
                print "searched album: " + self.ma_album.year + " - " + self.ma_album.title
                print "*******************************"


        #print album_data
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
        doc = csv.reader(open('/home/matth/programowanie/python/ma/metallum/country_code.csv', "rb"), delimiter=",")
        country_nr = "0"
        for line in doc:
            if str(country_name) in str(line[0]):
                return line[1]
                break
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
                print self.ma_band.name + "[" + self.ma_band.country + ", " + self.ma_band.genre + "]" + " id=" + self.ma_band.id
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

    def iterate_songs_and_print(self, songs):
        '''Iterate over returned song matches. If the lyrics are different than\
        "(lyrics not available)" then break the loop and print them out.\
        Otherwise the last song of the list will be printed.'''
        i = 0
        for song in songs:
            i = i + 1
            # print "song:" + song
            # band_name = band_name_re.search(song[0]).group("name")
            band_name = re.sub('<.*?>', '', song[0])
            # print "band_name:" + band_name
            band_albums_song_number_re = i
            # albums
            band_albums_re = re.sub('<.*?>', '', song[1])
            band_albums_song_name_re = song[3]
            print band_name + " - " + band_albums_song_name_re + " [" + band_albums_re + "]"
            # band_albums_re = re.compile(r'\*">
            # band_albums_re = re.search('?=song[1])
            # print "\n" + albums_title
            # print "*****song_title"
            # song_title = song[3]
            # print song_title
            # print search(song[1]).group("id")
            # song_id = lyric_id_re.search(song[4]).group("id")
            # print "*****song[2]"
            # print song[2]+ "|" + song[3] +":" + song[4]
            # print song_id
            # lyrics = get_lyrics_by_song_id(song_id)
            # if lyrics != lyrics_not_available:
            #    break
        band_albums_songs_total_numbers_re = i
        # title = "".join([band_name, " - ", song_title, "\n"])
        # sys.exit("".join(["\033[4m", title, "\n\033[0m", lyrics, "\n"]))

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
        print "********************"

if __name__ == '__main__':
    ma_searcher = ma_search()
    ma_searcher.main()
