#!/usr/bin/env python3

from urllib.request import urlopen
import bs4
from bs4 import BeautifulSoup

def GetKeyValues(table):
  keys = {}
  rows = table.find_all("tr")
  for tr in rows:
    key = None
    for th in tr.find_all('th'):
      key = th.getText().strip()
    value = None
    for th in tr.find_all('td'):
      text = [x['src'].strip() for x in th.findAll('img')]
      if text == []:
        text = [line.strip() for line in th.getText(separator='\n').splitlines()]
      if text == []:
        text = None
    if key != None and text != None:
      print(key + " = " + str(text))
      keys[key] = text
  return keys

#FIXME: Could be merged with the previous one if we just kept searching for th
#       and td in alternating sequence, regardless of tr
def GetKeyValuesWeird(table):
  keys = {}
  key = None
  value = None
  rows = table.find_all("tr")
  for tr in rows:
    if rows.index(tr) % 2 == 0:
      key = None
      for th in tr.find_all('th'):
        key = th.getText().strip()
      print(key)
    else:
      value = None
      for th in tr.find_all('td'):
        value = th.getText().strip()
      if key != None and value != None:
        #print(key + " = " + value)
        keys[key] = value
  return keys

def TableWithHeader(table):
  data = []
  rows = table.find_all("tr")
  for tr in rows:
    #print("Row")
    if rows.index(tr) >=  2:
      texts = []
      for th in tr.find_all('td'):
        text = [x['src'] for x in th.findAll('img')]
        if text == []:
          text = [th.getText().strip()]
        texts += [ text[0] ]
      data += [ texts ]
  return data

def GetGameList(path):
  page = 1
  game_tables = []
  while True:
    page_url = "http://redump.org" + path + "?page=" + str(page)
    print("Getting page " + str(page_url))
    page_data = urlopen(page_url)
    soup = BeautifulSoup((page_data), "html.parser")

    #FIXME: Make sure that the number of items did not change [so we don't miss any changes]
    if len(game_tables) > 0:
      pass

    # If there is no game table we've reached the end
    tables = soup.findAll("table")
    game_table = [table for table in tables if table['class'][0] == "games"]
    print("Found game tables: " + str(len(game_table)))
    if len(game_table) != 1:
      break

    game_tables += [ game_table[0] ]
    print("Adding page " + str(page))
    page += 1

  discs = []
  for game_table in game_tables:
    rows = game_table.findAll('tr')
    for tr in rows:
      if rows.index(tr) >=  1:
        disc_id = tr.findAll('td')[1].find('a')['href']
        disc_data = [x.getText().strip() for x in tr.findAll('td')]
        discs += [[ disc_id, disc_data]]

  return discs

def GetGameDisc(path):
  page_url = "http://redump.org" + path
  page_data = urlopen(page_url)
  soup = BeautifulSoup((page_data), "html.parser")

  mapStatus = {}
  mapStatus['/images/status/yellow.png'] = 'bad'
  mapStatus['/images/status/blue.png'] = 'unconfirmed'
  mapStatus['/images/status/green.png'] = 'confirmed'

  mapCountry = {}
  
  mapRegion = {}

  divs = soup.findAll("div")
  for div in divs:
    try:
      div_id = div["id"]
    except KeyError:
      continue
    if div_id == "main":
      name1 = div.find("h1").getText().strip()
      name2 = div.find("h2").getText().strip()
      print("Name 1: " + name1)
      print("Name 2: " + name2)

  tables = soup.findAll("table")
  for table in tables:

    table_class = table["class"][0]

    if table_class == "gameinfo":
      print(GetKeyValues(table))
    elif table_class == "dumpinfo":
      print(GetKeyValues(table))
    elif table_class == "gamecomments":
      print(GetKeyValuesWeird(table))
      #FIXME: Split Comments to get access to DMI, PFI, SS values
    elif table_class == "tracks":
      track_status = table.find("img")
      status = mapStatus[track_status['src'].strip()]
      print("track with status '" + status + "'")
      print(TableWithHeader(table))
    elif table_class == "rings":
      rings = TableWithHeader(table)
      for ring in rings:
        if len(ring) == 7:
          status = mapStatus[ring[6]]
          print("ring with status '" + status + "'")
        elif len(ring) == 5:
          print("normal ring")
        else:
          print("unknown ring " + str(len(ring)))
      print(rings)
    elif table_class == "ssranges":
      ssranges_status = table.find("img")
      status = mapStatus[ssranges_status['src'].strip()]
      print("ssranges with status '" + status + "'")
      print(TableWithHeader(table))
    else:
      print(table_class)
  return {}

#pages = GetGameList("/discs/system/xbox/")
#pages = GetGameList("/discs/dumper/Bubba2011/") # Random user for testing
#print(pages)
#print(str(len(pages)))

#FIXME: Process all pages

#GetGameDisc("/disc/9001/")

pages = GetGameList("/discs/system/xbox/")

publishers = []
for x in pages:
  data = x[1]
  mastering = data[6]
  if (mastering[2] == "-"):
    publisher = mastering[0:2]
    gameid = int(mastering[3:])
    fakemastering = publisher + "-" + ("000" + str(gameid))[-3:]
    if fakemastering != mastering:
      print("URGH!" + data)
    print(fakemastering + "  " + data[1])
    publishers += [publisher]
  else:
    print("BAD: " + mastering)
#print(pages)

publishers = list(set(publishers))
for p in sorted(publishers):
  print("| " + p + " || ")
  print("|-")
