#!/usr/bin/env python3
 
import os
import csv
from urllib.request import urlopen
from urllib.request import Request
from colorama import Fore, Style
import sys
import web

def GetXQEMUCompatibilityList():

  if False:
    #tables = GetTables("http://xboxdevwiki.net/XQEMU/Compatibility_List")
    #games = GetWikitable(tables[0])
    pass
  else:

    # Load data from John Godgames google sheet

    games = []
    sheet = "1sVtQ9SNPathKAMCqfYtvJQP0bs0UeLzP9otPHvZDMwE"

    url = "https://docs.google.com/spreadsheets/d/%s/export?format=csv" % sheet

    page_req = Request(url, headers={'User-Agent' : "Xbox-Database Tools"}) 
    page_res = urlopen(url)
    page_data = page_res.read()

    page_data = page_data.decode("utf-8")
    #print(page_data)

    values = [x for x in csv.reader(page_data.split('\n'))]


    heads = []
    for i, row in enumerate(values):            
        
      # Some rows might be to short, so we extend them
      row += [''] * max(0, len(heads) - len(row))

      # Parse the header
      if i == 0:
        for h in row:
          name = h.strip()
          if name == "": break
          if name == "Repo.": name = "Repository"
          if name == "commit": name = "Commit"
          heads += [name]
        continue

      # Parse each row
      test = {}
      for j in range(len(heads)):
        test[heads[j]] = row[j].strip()

      # Game probably wasn't tested if this condition is true
      if (test['Status'] == "" and test['Broken'] == ""):
        continue

      games += [test]

  return games

def GetGithubLines(user, repo, revision, path, from_line = 1, to_line = 999999, highlight = None):
  url = "https://raw.githubusercontent.com/" + user + "/" + repo + "/" + revision + "/" + path
  try:
    page_data = web.request(url, cache=True)
  except Exception as e:
    print("Unable to get '%s' (%s)" % (url, str(e)))
    return None
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
      print(Fore.YELLOW + line + Style.RESET_ALL)
    else:
      print(line)
  return lines



xqemu_compat = GetXQEMUCompatibilityList()

# Dump a version of the XQEMU compatibility list wiki page
if False:
  for g in xqemu_compat:
    if g['Status'] == "" and g['Broken'] == "" and g['Notes'] == "":
      continue
    print("| [[" + g['Title'] + "]] || " + g['Status'] + " || " + g['Broken'] + " || " + g['Author'] + " || " + g['Repository'] + " || " + g['Branch'] + " || " + g['Commit'] + " ||")
    print(g['Notes'])
    print("|-")

# Move variable
# (This used to be from a different script, which handled other DBs too)
all_games = xqemu_compat

status_count = {}
broken_count = {}
brokens = {}
for game in all_games:

  #print(game)
  
  try:
    title = game['Title']
    status = game['Status']
    broken = game['Broken']
  except KeyError:
    # Woops.. possibly no report yet :(
    continue

  # Attempt to track how often each "Status" appears
  try:
    oldCount = status_count[status]
  except KeyError:
    oldCount = 0    
  status_count[status] = oldCount + 1

  # Create a identifier for an error in a git version
  if broken.strip() != "":
    broken = { "Broken": game['Broken'], "Author": game['Author'], "Repository": game['Repository'], "Commit": game['Commit'] }
    broken_hash = hash(frozenset(broken.items()))
    brokens[broken_hash] = broken

    # Add this error to the list of unique ways XQEMU can be broken
    try:
      oldCount = broken_count[broken_hash]
    except KeyError:
      oldCount = []
    broken_count[broken_hash] = oldCount + [game['Title']]

# Display how often each status appears
print(status_count)

# Loop over the ways XQEMU broke
bad_brokens = {}
for broken_hash, titles in broken_count.items():
  broken = brokens[broken_hash]

  print()

  notes = ""

  if True:
    #FIXME: Loop over all affected games and display the notes
    for game_title in titles:
      
      #FIXME: Get game notes differently..
      game = [x for x in all_games if x['Title'] == game_title]
      assert(len(game) == 1)
      game = game[0]

      try:
        game_notes = game['Notes'].strip() 
      except:
        continue
      if game_notes == "":
        continue
      if notes != "":
        notes += "---\n"
      notes += Fore.WHITE + str(game['Title']) + Style.RESET_ALL + ": " + game_notes + "\n"

  if notes == "":
    notes = "<No notes>\n"

  notes = "\n" + notes
  notes = notes[:-1]
  notes = notes.replace("\n", "\n    ")

  #try:
  #  notes = 
  #except:
  #  pass

  print(Fore.GREEN + str(titles) + Style.RESET_ALL)
  print(broken)

  if broken['Broken'].lower() == "test":
    print("Needs retest: " + str(titles))
  elif broken['Broken'].lower() == "shader":
    print("Broken shader: " + notes)
  elif broken['Broken'].lower() == "texture":
    print("Broken texture(s): " + notes)
  elif broken['Broken'].lower() == "audio":
    print("Broken audio: " + notes)
  elif broken['Broken'].lower() == "input":
    print("Broken input: " + notes)
  elif broken['Broken'].lower() == "performance":
    print("Performance issues: " + notes)
  elif broken['Broken'].lower() == "memleak":
    print("Leaks memory: " + notes)
  elif broken['Broken'].lower() == "crash":
    print("Crashes: " + notes)
  elif broken['Broken'].lower() == "noboot":
    print("Does not boot: " + notes)
  elif broken['Broken'].lower() == "lighting":
    print("Lighting issues: " + notes)
  elif broken['Broken'] != "":
    try:
      path, line = broken['Broken'].rsplit(':', 1)

      # Convert line to integer and handle additional offset
      sep = line.find("-")
      if sep == -1:
        sep = line.find("+")
      if sep != -1:
        line_base = int(line[0:sep])
        line_offset = int(line[sep:])
        line = line_base + line_offset
      else:
        line = int(line)

      s = 3
      lines = GetGithubLines(broken['Author'],broken['Repository'],broken['Commit'], path, line-s, line+s, line)
      if lines == None:
        print(Fore.MAGENTA + "Bad report: " + str(broken) + " (GitHub error)" + Style.RESET_ALL)
        bad_brokens[broken_hash] = ["github", broken]
      else:
        if lines[line - 1].find("assert(") == -1:
          print(Fore.MAGENTA + "Bad report: " + str(broken) + " (Assert not found)" + Style.RESET_ALL)
          bad_brokens[broken_hash] = ["assert", broken]
        for i in range(max(1,line - 2), line + 1):
          if lines[i - 1].find("default:") != -1:
            print("Catchall (" + broken['Broken'] + "): " + notes)
        for i in range(max(1,line - 1), line + 1):
          if lines[i - 1].lower().find("untested") != -1:
            print("Untested feature (" + broken['Broken'] + "): " + notes)
    except:
      print("Error in database: '%s' caused problems" % str(broken['Broken']))
      bad_brokens[broken_hash] = ["parser", broken]

print()
print()

if len(bad_brokens) == 0:
  print("No errors found!")
else:
  print("Encountered the following %d error(s) in database:" % len(bad_brokens))
  print(" - github: GitHub did not have this file / revision")
  print(" - parser: An unknown value was used in 'Broken' field")
  print(" - assert: There was no assert found at the specified line")
  print()

  for broken_hash in bad_brokens:
    bad_broken = bad_brokens[broken_hash]
    print()
    print(Fore.MAGENTA + ("Error: %s" % str(bad_broken)) + Style.RESET_ALL )
    print("Games: %s" % str(broken_count[broken_hash]))

