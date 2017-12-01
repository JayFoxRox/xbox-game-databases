import os
from urllib.request import urlopen
from urllib.request import Request
import hashlib

def request(url, cache=False):

  m = hashlib.sha256()
  m.update(url.encode())
  url_hash = m.hexdigest()

  url_cache = os.path.join("cache", url_hash)

  if cache == True:
    try:
      with open(url_cache, 'rb') as f:
        return f.read()
    except:
      pass

  page_req = Request(url, headers={'User-Agent' : "Xbox-Database Tools"}) 
  page_res = urlopen(url)
  page_data = page_res.read()

  if cache == True:
    # Dump website to a file
    try:
      with open(url_cache, 'wb') as f:
        f.write(page_data)
    except:
      print("Failed to cache '" + url + "' (" + url_hash + ")")

  return page_data
