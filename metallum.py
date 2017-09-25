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


class MASearch():
    def __init__(self):
        self.ajax_ma = ajax_ma.AjaxMa()
        self.ma_band = ''
        self.ma_album = album.Album()
        self.band_discography = discography.Discography()

    def fill_album(self, album_data):
        album_tmp = album.Album()
        if 'Full-length' in album_data['Type']:
            album_type = 'LP'
        else:
            album_type = album_data['Type']
        album_tmp.year = album_data['Year']
        album_tmp.name = album_data['Name']
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

    def get_ma_album(self, number_of_results, search_album):
        print ("czego szukam: " + search_album.lower())
        if(number_of_results == 1):
            for album in self.band_discography.albums:
                if album.name.lower() in search_album.lower():
                    return album
        elif(number_of_results>1):
            for album in self.band_discography.albums:
                albums_founded = []
                albums_strings = []
                print ("jestem" + str(album.name.lower()) == str(search_album.lower()))
                if album.name.lower() in search_album.lower():
                    print("kurwa!!")
                    albums_founded.append(album)
                    albums_strings.append(album.album_to_string(albums_founded[-1]))

            choose = self.selector(albums_strings)
            print("We chose " + albums_strings[choose])
            if album.name.lower() in search_album.lower():
                self.ma_album = album
                exit(0)

    def create_ma_discography(self, album):

        disco = self.get_discography(self.ma_band.id)

        headings = [th.get_text() for th in disco.find("tr").find_all("th")]
        album_counter = 0
        for row in disco.find_all("tr")[1:]:
            dataset = zip(headings, (td.get_text() for td in row.find_all("td")))
            albums = dict(dataset)
            # print(str(albums['Name']))
            new_album = self.fill_album(albums)
            self.band_discography.albums.append(new_album)
            if album.lower() in new_album.name.lower():
                album_counter += 1
                # albums_data[albums['Name']] = album_data
                # print album_data
                # print albums.keys()
                print("searched album: " + new_album.year + " - " + new_album.name)
                print("*******************************")
        return album_counter

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
        new_band = artist.Band()
        new_band.name = re.sub('<.*?>', '', data[0]).replace("  ", " ")
        # if band have aka title
        if 'a.k.a.' in self.ma_band.name:
            new_band.aka = new_band.name[new_band.name.find("(") + 1:new_band.name.find(")")].replace(
                'a.k.a. ', '')
            new_band.name = new_band.name[:new_band.name.find("(") - 1]
        # band_id = data[0].replace("<a href=\"" + site_url + "bands/", "")
        band_id = re.findall('//(.*?)">*', data[0], re.DOTALL)
        band_id = band_id[0].replace("bands/", "")
        new_band.id = re.sub('^.*?/.*?/', '', band_id)
        new_band.genre = data[1].replace(",", " - ").replace("/", " - ").replace("\\", " -  ").replace("  ", " ")
        new_band.country = self.get_country_code(data[2])
        return new_band

    def get_country_code(self, country_name):
        """Function to convert country name to country code"""
        import csv
        doc = csv.reader(open('country_code.csv', "rb"), delimiter=",")
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
            band = results['aaData'][0]
            self.ma_band = artist.Band()
            self.ma_band = self.create_band(band)
            print(artist.band_to_string(self.ma_band))
        elif results['iTotalDisplayRecords'] > 1:
            bands_founded = []
            bands_strings = []
            for band in results['aaData']:
                #bands_founded = artist.Band()
                bands_founded.append(self.create_band(band))
                bands_strings.append(artist.band_to_string(bands_founded[-1]))

            choose = self.selector(bands_strings)
            print("We chose " + bands_strings[choose])
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
            print(band_name + " - " + band_albums_song_name_re + " [" + band_albums_re + "]")
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

    def selector(self, choose_list):
        import curses
        stdscr = curses.initscr()
        curses.start_color()
        attributes = {}
        curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)
        attributes['normal'] = curses.color_pair(1)

        curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_WHITE)
        attributes['highlighted'] = curses.color_pair(2)

        c = 0  # last character read
        option = 0  # the current option that is marked
        while c != 10:  # Enter in ascii
            stdscr.erase()
            stdscr.addstr("What is your class?\n", curses.A_UNDERLINE)
            stdscr.addstr("Pressed = " + str(c))
            for i in range(len(choose_list)):
                if i == option:
                    attr = attributes['highlighted']
                else:
                    attr = attributes['normal']
                stdscr.addstr("{0}. ".format(i + 1))
                stdscr.addstr(choose_list[i] + '\n', attr)
            c = stdscr.getch()
            # curses.KEY_UP 65 or KEY_LEFT 68
            if (c == 65 or c == 68) and option > 0:
                option -= 1
            # curses.KEY_DOWN 66 or KEY_RIGHT 67
            elif (c == 66 or c == 67) and option < len(choose_list) - 1:
                option += 1

        stdscr.addstr("You chose {0}".format(choose_list))
        stdscr.getch()
        return option


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
            album_results = self.create_ma_discography(args.album)
            self.ma_album = self.get_ma_album(album_results, args.album)
            #    # TODO do smthing with more results
            #    print("Founded albums: %s" % album_results)
            #    self.selector()
                #curses.wrapper(self.character)
        print("********************")


if __name__ == '__main__':
    ma_searcher = MASearch()
    ma_searcher.main()
