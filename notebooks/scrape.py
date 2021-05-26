# Diff. between Pool and ThreadPool
# https://stackoverflow.com/questions/46045956/whats-the-difference-between-threadpool-vs-pool-in-the-multiprocessing-module
from multiprocessing import pool
import requests
import re
import os
from PIL import Image
import io
from tqdm import trange
from urllib3.exceptions import MaxRetryError

from daily import *


get_image = lambda x: Image.open(io.BytesIO(requests.get(x).content))

def download_url(url):
  try:
    r = requests.get(url)
  except MaxRetryError:
    # most likely the file does not exist
    r = None
    print("URL failed:" + url)
  if r is not None and r.status_code == requests.codes.ok:
    out = r.content.decode("utf-8")
    sidx = out.index('''<img class="_2UpQX" sizes="(max-width:''')
    sec = out[sidx:sidx+1000]
    try:
      link = re.findall(r"https:\/+images.unsplash.com\/photo-[0-9a-zA-Z-_]+", sec)[0]
    except Exception as e:
      link = re.findall(r"https:\/+images.unsplash.com\/\d+\/[0-9a-zA-Z-_]+.jpg", sec)[0]
      print(e)
    try:
      img = get_image(link)
      _hash = Hashlib.md5(link) + Hashlib.sha256(img.tobytes())
      fp = os.path.join(folder(__file__), ".img_cache", _hash + ".png")
      img.save(fp)
    except Exception as e:
      print(e)
      return
    return _hash

if __name__ == "__main__":
  os.makedirs(os.path.join(folder(__file__), ".img_cache"), exist_ok = True)

  with open(os.path.join(folder(__file__), "links_raw.txt"), "r") as f:
    text = [x.strip() for x in f.readlines() if x.strip()]
  
  ls = []
  for t in text:
    m = re.findall(r"^https:\/+unsplash\.com\/photos\/[a-zA-Z0-9-]+$", t)
    if m:
      ls.extend(m)

  # Run 50 multiple threads, is this a good idea? Downloads are *really* fast though!
  ids = []
  with trange(len(ls)) as pbar:
    results = pool.ThreadPool(10).imap_unordered(download_url, ls)
    for r in results:
      pbar.update(1)
      pbar.set_description(f"--> {len(ids)}")
      if r:
        ids.append(r)

  with open(os.path.join(folder(__file__), "keys.txt"), "w") as f:
    f.write("\n".join(ids))
