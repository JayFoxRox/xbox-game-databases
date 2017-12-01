#!/usr/bin/env python3

from urllib.request import urlopen
from urllib.request import Request
import bs4
from bs4 import BeautifulSoup

def GetImage(path):
  page_url = "http://www.covergalaxy.com" + path
  print(page_url)
  page_req = Request(page_url, headers={'User-Agent' : "Xbox Preservation"}) 
  page_data = urlopen(page_req)
  soup = BeautifulSoup((page_data), "html.parser")

  tables = soup.findAll("table")
  print(str(len(tables)))
  if len(tables) != 3:
    return None

  table = tables[-1]

  return table.find('img')['src']

def GetGameCoverImage(path):
  return GetImage(path + "Cover")

def GetGameDiscImage(path):
  return GetImage(path + "CD")

def GetGameList(path):
  page_url = "http://www.covergalaxy.com" + path
  print(page_url)
  page_req = Request(page_url, headers={'User-Agent' : "Xbox Preservation"}) 
  page_data = urlopen(page_req)
  soup = BeautifulSoup((page_data), "html.parser")

  tables = soup.findAll("table")
  print(str(len(tables)))
  if len(tables) != 3:
    return []

  games = []
  table = tables[-1]

  rows = table.findAll('tr')
  for tr in rows:
    if rows.index(tr) >= 1:
      tds = tr.findAll('td')
      games += [tds[0].getText()]
      #FIXME: Find URL from the 2 links

  return games


print(GetGameDiscImage("/XBox/007+Agent+Under+Fire/"))
print(GetGameCoverImage("/XBox/007+Agent+Under+Fire/"))

#games = GetGameList("/list/XBox/all/")
#print(games)

