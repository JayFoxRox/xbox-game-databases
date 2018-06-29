#!/usr/bin/env python3
 
from googleapiclient import discovery
from colorama import Fore, Style

import sys

import web

args = sys.argv[1:]

api_key = None
api_key_file = "xqemu-compatibility-inspector.api_key"

def failKey(message):
  print(Fore.RED + message + Style.RESET_ALL)
  print("")
  print("If you think this is an error, try again.")
  print("")
  print("Otherwise follow the instructions at: https://goo.gl/3UN7Ut")
  print("Then run this script with `--key <Google API key>` as argument to initialize your key-file.")
  sys.exit(1)

if len(args) >= 1:

  # Update key
  if args[0] == '--key':
    args = args[1:] # Consume "--key"
    if len(args) == 0:
      print("Missing <Google API key> after `--key` option.")
      sys.exit(1)
    else:
      api_key = args[0].strip()
      with open(api_key_file, 'w') as f:
        f.write(api_key)
        f.close()
        print("Stored key-file! Next time, you don't have to use the `--key` option.")
        print("")
      args = args[1:] # Consume <api_key>
  else:
    print("Unknown option '%s'." % args[0])
    sys.exit(1)

# Load API token from file if necessary
if api_key == None:
  try:
    with open(api_key_file, 'r') as f:
      api_key = f.read().strip()
      f.close()
  except:
    failKey("Failed to load key-file and no valid Google API key provided.")

# API key is empty
if len(api_key) == 0:
  failKey("Google API key is empty.")

def GetXQEMUCompatibilityList():

  if False:
    #tables = GetTables("http://xboxdevwiki.net/XQEMU/Compatibility_List")
    #games = GetWikitable(tables[0])
    pass
  else:

    # Load data from John Godgames google sheet

    games = []


    spreadsheetId = '1sVtQ9SNPathKAMCqfYtvJQP0bs0UeLzP9otPHvZDMwE'
    rangeName = 'Data!A1:Z'
    discoveryUrl = ('https://sheets.googleapis.com/$discovery/rest?'
                    'version=v4&')
      

    try:
      service = discovery.build('sheets', 'v4',
                                developerKey=api_key,
                                discoveryServiceUrl=discoveryUrl)
      result = service.spreadsheets().values().get(spreadsheetId=spreadsheetId, range=rangeName).execute()

    except:
      failKey("Failed to load spreadsheet. Something might be wrong with your Google API key.")

    values = result.get('values', [])

    if not values:
      print('No data found.')
    else:
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

  #FIXME: Loop over all affected games and display the notes
  notes = "<Notes>"
  #try:
  #  notes = game['Notes']
  #except:
  #  pass

  print(Fore.GREEN + str(titles) + Style.RESET_ALL)
  print(broken)

  if broken['Broken'].lower() == "test":
    print("Needs retest: " + str(titles))
  elif broken['Broken'].lower() == "shader":
    print("Broken shader: " + notes)
  elif broken['Broken'].lower() == "texture":
    print("Broken texture: " + notes)
  elif broken['Broken'].lower() == "audio":
    print("Broken audio: " + notes)
  elif broken['Broken'].lower() == "input":
    print("Broken input: " + notes)
  elif broken['Broken'].lower() == "memoryleak":
    print("Broken memory leak: " + notes)
  elif broken['Broken'].lower() == "crash":
    print("Broken crash: " + notes)
  elif broken['Broken'].lower() == "noboot":
    print("Broken boot: " + notes)
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
            print("Catchall (" + broken['Broken'] + "): " + str(titles))
        for i in range(max(1,line - 1), line + 1):
          if lines[i - 1].lower().find("untested") != -1:
            print("Untested feature (" + broken['Broken'] + "): " + str(titles))
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

