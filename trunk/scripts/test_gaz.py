#!/usr/bin/python
#
# This script is used to create a report that compares the results obtained from the gazetteer bulk load with what is sent back via the REST service
# Author: Gavin Jackson
# Date: March 2011
# Tags: XPATH, csv read

import httplib
import csv
import io
from lxml import etree
from StringIO import StringIO

#read in points from csv file
pointReader = csv.reader(open('../data/gazetteer/gaz_sample.csv', 'rb'), delimiter=',', quotechar='|')
for row in pointReader:
	lon = row[0]
	lat = row[1]
	state = row[2]
	lga = row[3]
	ibra = row[4]
	imcra = row[5]

	#perform http request using gazetteer service
	conn = httplib.HTTPConnection("spatial.ala.org.au")
	conn.request("GET","/gazetteer/search?lat=" + lat + "&lon=" + lon);
	r1 = conn.getresponse()
	xmlres = r1.read()
	input = StringIO(xmlres)
	tree = etree.parse ( input );
	results = tree.xpath('/search/results/result')
	my_state = ""
	my_lga = ""
	my_ibra = ""
	my_imcra = ""
	for result in results:
		name = result.xpath('name')[0].text
		layer = result.xpath('layerName')[0].text
		if (layer == 'state'):
			my_state = name
		elif (layer == 'lga'):
			my_lga = name
		elif (layer == 'ibra'):
			my_ibra = name
		elif (layer == 'imcra'):
			my_imcra = name	
	print "lat: " + lat + " lon: " + lon + "\n\tSTATE: \n\t\tgaz:" + my_state + "\n\t\tbgaz:" + state + "\n\tLGA:  \n\t\tgaz:" + my_lga + "\n\t\tbgaz:" + lga + "\n\tIBRA:  \n\t\tgaz:" + my_ibra + "\n\t\tbgaz:" + ibra + "\n\tIMCRA: \n\t\tgaz:" + my_imcra + "\n\t\tbgaz:" + imcra + "\n"
