import json
from urllib.request import urlopen
from urllib.parse import urlencode
import codecs

class AjaxMa:
    def __init__(self):
        self.site_url = 'http://www.metal-archives.com/'
        self.site_url_without_html = 'www.metal-archives.com/bands/'
        self.ajax_song = 'search/ajax-advanced/searching/songs?'
        self.ajax_album = 'search/ajax-advanced/searching/albums?'
        self.ajax_band = 'search/ajax-advanced/searching/bands?'
        self.ajax_query_album = 'search/ajax-album-search/?query='
        self.ajax_query_band = 'search/ajax-band-search/?'

    def band_ma_query(self, query):
        # create parameters to query
        params = dict(
            query=query,
        )
        url = "".join([self.site_url, self.ajax_query_band, urlencode(params)])
        # debug url info
        # print ">>url=" + url
        normalizer = codecs.getreader("utf-8")
        norm_result = normalizer(urlopen(url))
        return json.load(norm_result)
