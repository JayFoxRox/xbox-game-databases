#!/usr/bin/env python3
 
import copy
import web
import extra
import bs4
from bs4 import BeautifulSoup
from colorama import init
init()
from colorama import Fore, Style
import difflib
#from github import Github

#gh = Github(client_id="",client_secret="")


def GetWikitable(table):
  games = []
  rows = table.findAll('tr')

  headers = [th.getText().strip() for th in rows[0].findAll('th')]

  for tr in rows:
    if rows.index(tr) >= 1:
      tds = tr.findAll('td')
      game = {}
      for i in range(len(headers)):
        key = headers[i]
        try: #FIXME: This should consider rowspan / colspan!
          td = tds[i]
          for e in td.find_all():
            try:
              if e.attrs['style'].find('display:none;') != -1:
                e.extract()
            except KeyError:
              pass
          for e in td.find_all('sup'):
            try:
              if "reference" in e.attrs['class']:
                e.extract()
            except KeyError:
              pass
          for e in td.find_all('small'):
            e.extract()
          value = td.getText().strip()
          game[key] = value
        except IndexError:
          game[key] = ''
      games += [game]

  return games

def GetTables(url):
  page_data = web.request(url)
  soup = BeautifulSoup((page_data), "html.parser")
  return soup.findAll("table")

def GetXQEMUCompatibilityList():
  tables = GetTables("http://xboxdevwiki.net/XQEMU/Compatibility_List")
  games = GetWikitable(tables[0])
  for g in games:
    try:
      aliased = extra.alias[g['Title']]  
      if len(aliased) != 1:
        print("Oops?! Name ambigious: " + str(g['Title']))
      g['Title'] = aliased[0] #FIXME: Clone entry for ambigious names?!
    except:
      pass
  return games

#FIXME: Add support for https://en.wikipedia.org/wiki/List_of_Xbox_games_compatible_with_Xbox_360

def GetEngineList():
  tables = GetTables("http://xboxdevwiki.net/Engine_List")
  header = "FooEngine"
  engines = []
  for i in range(7):
    engine = GetWikitable(tables[i])
    engine = Merge(engine, [{"Engine": header}], []) # Always matches!
    for g in engine:
      titles = g['Title'].split('\n')
      g['Title'] = titles[0] #FIXME: Trim?
      g['Alternate Titles'] = titles[1:] #FIXME: Trim each?
    engines += engine
  #print(engines)
  return engines

def GetAllGames():
  tables = GetTables("https://en.wikipedia.org/wiki/List_of_Xbox_games")
  games = GetWikitable(tables[1])
  for g in games:
    titles = g['Title'].split('\n')
    g['Title'] = titles[0] #FIXME: Trim?
    g['Alternate Titles'] = titles[1:] #FIXME: Trim each?
  return games

def GetHDGames():
  tables = GetTables("https://en.wikipedia.org/wiki/List_of_Xbox_games_with_alternate_display_modes")
  games = GetWikitable(tables[0])
  for g in games:
    titles = g['Title'].split('\n')
    g['Title'] = titles[0] #FIXME: Trim?
    g['Alternate Titles'] = titles[1:] #FIXME: Trim each?
  return games

def GetGithubLines(user, repo, revision, path, from_line = 1, to_line = 999999, highlight = None):
  page_data = web.request("https://raw.githubusercontent.com/" + user + "/" + repo + "/" + revision + "/" + path, cache=True)
  the_page = page_data.decode()
  lines = the_page.splitlines()  
  for i in range(from_line - 1, to_line):
    if i < 0:
      continue
    if i >= len(lines):
      break
    line = lines[i]
    line_index = i + 1 #FIXME: Does not work if from_line is negative
    #print(str(line_index))
    if highlight != None and highlight == line_index:
      print(Fore.RED + line + Style.RESET_ALL)
    else:
      print(line)
  return lines

def Rename(src, new, old):
  mixed = copy.deepcopy(src)
  for m in mixed:
    m[new] = m.pop(old)
  return mixed

# FIXME: Move to some common file
# FIXME: Report those which could not be matched
def Merge(dest, src, by):
  mixed = copy.deepcopy(dest)
  for s in src:
    match_count = 0
    #print("Trying to match " + s[by[0]])
    for d in mixed:
      #print("     agaist " + d[by[0]])
      # Check if all fields match
      matched = True
      for b in by:
        try:
          if d[b] != s[b]:
            matched = False
        except KeyError:
          # matched = True # = Key doesn't exist = merge anyway
          matched = False # = Key doesn't exist = don't merge
      if matched == False:
        continue
      match_count += 1
      # Move data
      for key,value in s.items():
        d[key] = value
      #print("Matched " + d[by[0]])
    if match_count != 1:
      if len(by) >= 1:
        print("Unexpected match count (" + str(match_count) + "): '" + s[by[0]] + "'")
        d_all = [d[by[0]] for d in dest]
        print("Did you mean: " + str(difflib.get_close_matches(s[by[0]], d_all)))
        print("")

  return mixed

hd_games = GetHDGames()
#hd_games = Rename(hd_games, "Title", "Game")
#print(hd_games)
all_games = GetAllGames()

# Add unreleased games!
for k,v in extra.unreleased.items():
  g = {}
  g['Title'] = k
  g['Unreleased'] = True
  all_games += [g]

# Add XBLA games!
for k,v in extra.xbla.items():
  g = {}
  g['Title'] = k
  g['XBLA'] = True
  all_games += [g]


#print(all_games)
engines = GetEngineList()
xqemu_compat = GetXQEMUCompatibilityList()


# Dump a version of the XQEMU compatibility list wiki page
if False:
  for g in xqemu_compat:
    if g['Status'] == "" and g['Broken'] == "" and g['Notes'] == "":
      continue
    print("| [[" + g['Title'] + "]] || " + g['Status'] + " || " + g['Broken'] + " || " + g['Author'] + " || " + g['Repository'] + " || " + g['Branch'] + " || " + g['Commit'] + " ||")
    print(g['Notes'])
    print("|-")

print("Merging HD mode")
all_games = Merge(all_games, hd_games, ['Title'])

print("Merging engines")
all_games = Merge(all_games, engines, ['Title'])

print("Merging all games")
all_games = Merge(all_games, xqemu_compat, ['Title'])

status_count = {}
broken_count = {}
brokens = {}
for game in all_games:

#  print(game)
  
  try:
    title = game['Title']
    status = game['Status']
    broken = game['Broken']
  except KeyError:
    # Woops.. possibly no report yet :(
    continue

#  owner = game[3]
#  repo = game[4]
#  branch = game[5]
#  revision = game[6]
#  notes = game[7]

#  try:
#    print(game['Publisher/Developer'])
#  except KeyError:
#    pass

  try:
    oldCount = status_count[status]
  except KeyError:
    oldCount = 0    
  status_count[status] = oldCount + 1

  broken = { "Broken": game['Broken'], "Author": game['Author'], "Repository": game['Repository'], "Commit": game['Commit'] }

  #FIXME: Don't need the hash.. just add by index
  broken_hash = hash(frozenset(broken.items()))
  brokens[broken_hash] = broken
  try:
    oldCount = broken_count[broken_hash]
  except KeyError:
    oldCount = []
  broken_count[broken_hash] = oldCount + [game['Title']]



print(status_count)
#print(broken_count)

for broken_hash, titles in broken_count.items():
  broken = brokens[broken_hash]

  notes = ""
  try:
    notes = game['Notes']
  except:
    pass
    
  if broken['Broken'].lower() == "test":
    print("Needs retest: " + str(titles))
  elif broken['Broken'].lower() == "shader":
    print("Broken shader: " + notes)
  elif broken['Broken'].lower() == "texture":
    print("Broken texture: " + notes)
  elif broken['Broken'] != "":
    print(titles)
    #print(broken)
    path, line = broken['Broken'].rsplit(':', 1)
    line = int(line)
    s = 3
    lines = GetGithubLines(broken['Author'],broken['Repository'],broken['Commit'], path, line-s, line+s, line)
    if lines[line - 1].find("assert(") == -1:
      print("Bad report: " + str(titles))
    for i in range(max(1,line - 2), line + 1):
      if lines[i - 1].find("default:") != -1:
        print("Catchall (" + broken['Broken'] + "): " + str(titles))
    for i in range(max(1,line - 1), line + 1):
      if lines[i - 1].lower().find("untested") != -1:
        print("Untested feature (" + broken['Broken'] + "): " + str(titles))


