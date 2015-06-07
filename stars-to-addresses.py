# -*- coding: utf-8 -*-
"""
Go to Google Bookmarks: https://www.google.com/bookmarks/

On the bottom left, click "Export bookmarks": https://www.google.com/bookmarks/bookmarks.html?hl=en

After downloading the html file, run this script on it to get the addresses

This script is based on https://gist.github.com/endolith/3896948
"""

import sys

try:
	from lxml.html import document_fromstring
except ImportError:
	print "You need to install lxml"
	sys.exit()

try:
	from geopy.geocoders import Nominatim
except ImportError:
	print "You need to install geopy"
	sys.exit()

from urllib2 import urlopen
import re
import time

filename = r'GoogleBookmarks.html'

with open(filename) as bookmarks_file:
    data = bookmarks_file.read()

geolocator = Nominatim()

# Hacky and doesn't work for all of the stars:
lat_re = re.compile('markers:[^\]]*latlng[^}]*lat:([^,]*)')
lon_re = re.compile('markers:[^\]]*latlng[^}]*lng:([^}]*)')
coords_in_url = re.compile('\?q=(-?\d{,3}\.\d*),\s*(-?\d{,3}\.\d*)')

doc = document_fromstring(data)
for element, attribute, url, pos in doc.body.iterlinks():
    if 'maps.google' in url:
        description = element.text or ''
        print description.encode('UTF8')
        
        if coords_in_url.search(url):
            # Coordinates are in URL itself
            latitude = coords_in_url.search(url).groups()[0]
            longitude = coords_in_url.search(url).groups()[1]
        else:
            # Load map and find coordinates in source of page
            try:
                sock = urlopen(url.replace(' ','+').encode('UTF8'))
            except Exception, e:
                print 'Connection problem:'
                print repr(e)
                print 'Waiting 2 minutes and trying again'
                time.sleep(120)
                sock = urlopen(url.replace(' ','+').encode('UTF8'))
            content = sock.read()
            sock.close()
            time.sleep(3) # Don't annoy server
            try:
                latitude = lat_re.findall(content)[0]
                longitude = lon_re.findall(content)[0]
            except IndexError:
                try:
                    lines = content.split('\n')  # --> ['Line 1', 'Line 2', 'Line 3']
                    for line in lines:
                        if re.search('cacheResponse\(', line):
                            splitline = line.split('(')[1].split(')')[0] + '"]'
                            # in the future we can extract the coordinates from here
                            null = None
                            values = eval(splitline)
                            print values[8][0][1]
                            continue
                    continue
                except IndexError:
                    print '[Coordinates not found]'
                    continue
                print
                continue
        
        print latitude, longitude
        try:
			location = geolocator.reverse(latitude+", "+longitude)
			print(location.address)
        except ValueError:
            print '[Invalid coordinates]'
        print
