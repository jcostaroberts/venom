#!/usr/bin/env python

from datetime import datetime
from lxml import html
import argparse
import csv
import pdb
import unicodedata

def read_file(infile):
   f = open(infile, "r")
   t = f.read()
   f.close()
   return t

def their_name(expected_name, n1, n2):
   assert expected_name in [n1, n2]
   return n1 if n1 != expected_name else n2

def parsed_html(infile):
   tree = html.fromstring(read_file(infile))
   table = tree.xpath('//div[@class="profile_feed_story gray_bottom_divider p_twenty_l p_twenty_r"]')
   return [t.text_content() for t in table]

def item_to_list(item):
   return filter(lambda x: x, [x.strip() for x in item.split("\n")])

def string_from_unicode(s):
   return unicodedata.normalize("NFKD", s).encode("ascii", "ignore")

def date_from_string(date, year):
   try:
      d = str(datetime.strptime("%s %s" % (date, year),
	      "%B %d %Y").date())
      return d
   except ValueError:
      return date

def processed_item(expected_name, year, item):
   itl = [string_from_unicode(x) for x in item_to_list(item)]
   from_name = itl[0]
   to_name = itl[2]
   note = itl[3].replace(",", "") # No commas in note
   date = date_from_string(itl[6], year)
   amount = itl[-1].replace("+", "") # Positive by default
   name = their_name(expected_name, from_name, to_name)
   return [name, note, date, amount]

def write_csv(outfile, item_list):
   f = open(outfile, "w")
   writer = csv.writer(f)
   writer.writerow(["Name", "Note", "Date", "Amount"])
   map(writer.writerow, item_list)
   f.close()

parser = argparse.ArgumentParser()
parser.add_argument("-i", "--infile", required=True,
                    help="HTML file containing Venmo transactions")
parser.add_argument("-o", "--outfile", required=True,
                    help="CSV output file location")
parser.add_argument("-u", "--username", required=True,
                    help="Name of user")
parser.add_argument("-y", "--year", default=datetime.now().year,
                    help="Transaction year")
args = parser.parse_args()

write_csv(args.outfile,
          map(lambda x: processed_item(args.username, args.year, x),
              parsed_html(args.infile)))
