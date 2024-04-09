import argparse

from ai import *
from onenote import *
from maps import *
from utils import *

parser = argparse.ArgumentParser(description = 'Plan a trip for selected place in given country.')
parser.add_argument('city', help = 'a city for which to plan the trip')

parser.add_argument('--min', default = 15,  help = 'Minimum number of returned attractions, e.g. 10. Default 15')
parser.add_argument('--max', default = 20,  help = 'Maximum number of returned attractions, e.g. 10. Default 20')
parser.add_argument('--country', default = "Spain",  help = 'Optional country. Default Spain')
parser.add_argument('--home', default = "Barcelona",  help = 'Optional home city, it is used to find direction  to selected city. Default Barcelona')

args = parser.parse_args()

#get reference pages
pages = getReferencePages(args.city, args.country)
pages = ','.join([str(page) for page in pages])

# OpenAI
data = planner(city = args.city, country = args.country, pages = pages, min = args.min, max = args.max)

# print(data)
# No API for MyMaps (but there is a hope) -> https://issuetracker.google.com/issues/35820262
# Workaround :
# - create KML file with values returned from geocode API
# - open create new map in MyMaps and import KML file
# - get link to map (paste in some dialog box)
# - update link in OneNote
# - attach file to page in  OneNote

KMLData = prepareKMLFile(args.city.title(), args.country.title(), data)

# OneNote
print("Let's insert page in OneNote")
insertPage(args.city, args.country, prepareOneNoteContent(args.city, args.country, data, KMLData, args.home, pages))