#!/usr/bin/env python

import sys
import argparse
import re
import os

import album
import artist
import ajax_ma
import discography


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

    def get_ma_album(self, number_of_results, search_album):
        if (number_of_results == 1):
            for album in self.band_discography.albums:
                if album.name.lower() in search_album.lower():
                    return album
        elif (number_of_results > 1):
            albums_founded = []
            albums_strings = []
            for album in self.band_discography.albums:
                # weird, how bellow work and lower don't
                if album.name.lower().count(search_album.lower()) >= 1:
                #if (album.name.lower() in search_album.lower()):
                    albums_founded.append(album)
                    albums_strings.append(album.album_to_string(albums_founded[-1]))
            choose = self.selector(albums_strings)
            # print("We choses %s" % albums_founded[choose].name)
            return albums_founded[choose]

    def create_ma_discography(self, album):
        disco = self.ajax_ma.discography_ma_query(self.ma_band.id)
        headings = [th.get_text() for th in disco.find("tr").find_all("th")]
        album_counter = 0
        for row in disco.find_all("tr")[1:]:
            dataset = zip(headings, (td.get_text() for td in row.find_all("td")))
            albums = dict(dataset)
            new_album = self.fill_album(albums)
            self.band_discography.albums.append(new_album)
            # check if searched string match with album string
            album_counter += 1 if album.lower() in new_album.name.lower() else False
        return album_counter

    # def listing_dirs():
    #     for dirname, dirnames, filenames in os.walk(''):
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
        new_band.name = self.get_band_name(data[0])
        # if band have aka title
        if 'a.k.a.' in new_band.name:
            new_band.aka = new_band.name[new_band.name.find("(") + 1:new_band.name.find(")")].replace(
                'a.k.a. ', '')
            new_band.name = new_band.name[:new_band.name.find("(") - 1]

        new_band.id = self.get_band_id(data[0])
        new_band.genre = self.get_genre(data[1])
        new_band.country = self.get_country_code(data[2])
        return new_band

    def get_band_name(self, raw_data):
        return re.sub('<.*?>', '', raw_data).replace("  ", " ")

    def get_band_id(self, raw_data):
        band_id = re.findall('//(.*?)">*', raw_data, re.DOTALL)
        band_id = band_id[0].replace("bands/", "")
        return re.sub('^.*?/.*?/', '', band_id)

    def get_genre(self, raw_data):
        return raw_data.replace(",", " - ").replace("/", " - ").replace("\\", " -  ").replace("  ", " ")

    def get_country_code(self, country_name):
        """Function to convert country name to country code"""
        import csv
        doc = csv.reader(open('extra/country_code.csv', "rt", encoding='utf8'), delimiter=",")
        for line in doc:
            if str(country_name) in str(line[0]):
                return line[1]
                break
        return "xxx"

    def get_ma_band(self, band):
        results = self.ajax_ma.band_ma_query(band)
        # if only one result (so we don't have to select anything) else run selector
        if results['iTotalDisplayRecords'] == 1:
            band = results['aaData'][0]
            new_band = artist.Band()
            new_band = self.create_band(band)
            print(artist.band_to_string(new_band))
            return new_band
        elif results['iTotalDisplayRecords'] > 1:
            bands_founded = []
            bands_strings = []
            for band in results['aaData']:
                bands_founded.append(self.create_band(band))
                bands_strings.append(artist.band_to_string(bands_founded[-1]))
            choose = self.selector(bands_strings)
            # debug if choose select proper object
            # print("We chose " + bands_strings[choose])
            return bands_founded[choose]

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
            stdscr.addstr("Have more results with this name.\nCan you select proper?\n", curses.A_UNDERLINE)
            # for debug pressed key's
            # stdscr.addstr("Pressed = %s\n" % str(c))
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
        # debug choosing
        #stdscr.addstr("You chose {0}".format(choose_list))
        #stdscr.getch()
        stdscr.erase()
        return option

    def main(self):
        """Runs the program and handles command line options"""
        parser = argparse.ArgumentParser(description='Get lyrics from http://metal-archives.com')
        parser.add_argument('band', type=str, help='The name of the band. Ex: "Vomigod"')
        parser.add_argument('album', type=str, help='The title of the song. Ex: "OralTrol"')
        args = parser.parse_args()
        self.ma_band = self.get_ma_band(args.band)
        if not self.ma_band:
            print("can't find " + args.band)
        else:
            album_results = self.create_ma_discography(args.album)
            self.ma_album = self.get_ma_album(album_results, args.album)
        print("********************")


if __name__ == '__main__':
    ma_searcher = MASearch()
    ma_searcher.main()
