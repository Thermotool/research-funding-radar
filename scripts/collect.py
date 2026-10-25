"""Best-effort public-listing discovery. Not a guarantee of exhaustive or verified calls."""
import datetime as dt
import hashlib
import json
import os
import re
from pathlib import Path
from urllib.parse import urljoin, urlparse
import requests
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
HEADERS = {'User-Agent': 'ResearchFundingRadar/0.1 (+research discovery; contact via repository)'}
KEYWORDS = ('utlysning','finansiering','forskningsmedel','sök stöd','call for','funding','bidrag','ansökan','ansök','horizon')
STOPWORDS = ('cookie','integritet','kontakt','logga in','nyhetsbrev','tillgänglighet')
PROFILE = {
 'thermal plasma': (22, 'Termisk plasma'), 'plasma': (18, 'Plasma'),
 'electrification': (19, 'Elektrifiering'), 'elektrifier': (19, 'Elektrifiering'),
 'cement': (18, 'Cement'), 'high temperature': (16, 'Högtemperatur'),
 'högtemperatur': (16, 'Högtemperatur'), 'industri': (9, 'Industri'),
 'industrial': (9, 'Industri'), 'energy efficiency': (11, 'Energieffektivisering'),
 'energieffektiv': (11, 'Energieffektivisering'), 'combustion': (12, 'Förbränning'),
 'förbränning': (12, 'Förbränning'), 'hydrogen': (10, 'Vätgas'), 'vätgas': (10, 'Vätgas'),
 'climate': (7, 'Klimat'), 'klimat': (7, 'Klimat'), 'process': (5, 'Processer'),
 'värme': (9, 'Värmeöverföring'), 'heat transfer': (12, 'Värmeöverföring')
}

def score(text):
 t=text.lower(); found={}; points=0
 for term,(weight,tag) in PROFILE.items():
  if term in t and tag not in found:
   found[tag]=weight; points+=weight
 return min(100,points), list(found), [f'Ämnesmatchning: {tag}' for tag in list(found)[:4]]

def get_candidates(source):
 resp=requests.get(source['url'],headers=HEADERS,timeout=25)
 resp.raise_for_status()
 soup=BeautifulSoup(resp.text,'html.parser')
 for e in soup(['script','style','nav','footer','header']): e.decompose()
 output=[]; seen=set()
 for a in soup.select('a[href]'):
  title=' '.join(a.get_text(' ',strip=True).split())
  url=urljoin(resp.url,a['href']).split('#')[0]
  if len(title)<16 or len(title)>190 or not url.startswith('http') or url in seen:continue
  if any(s in title.lower() for s in STOPWORDS):continue
  context=' '.join(a.parent.get_text(' ',strip=True).split())[:550] if a.parent else title
  if not any(w in (title+' '+context).lower() for w in KEYWORDS):continue
  seen.add(url)
  output.append((title,url,context))
 return output[:120]

def main():
 sources=json.loads((ROOT/'data/sources.json').read_text())
 old_path=ROOT/'public/calls.json'
 old=json.loads(old_path.read_text()) if old_path.exists() else {'calls':[]}
 prior={c['id']:c for c in old.get('calls',[])}
 calls={}; results=[]; now=dt.datetime.now(dt.timezone.utc).isoformat()
 for source in sources:
  if not source.get('enabled',True):continue
  count=0
  try:
   for title,url,context in get_candidates(source):
    key=hashlib.sha256(url.encode()).hexdigest()[:16]
    relevance,tags,reasons=score(title+' '+context)
    if relevance==0:continue
    previous=prior.get(key,{})
    calls[key]={'id':key,'title':title,'funder':source['name'],'url':url,'deadline':previous.get('deadline'),
     'description':context[:420],'topics':tags,'score':relevance,'reasons':reasons,
     'eligibility':'Ej verifierad – kontrollera originalutlysningen.',
     'source':source['url'],'updated_at':now,'status':'unverified'}
    count+=1
   results.append({'name':source['name'],'status':'ok','count':count})
  except Exception as exc:
   results.append({'name':source['name'],'status':'error','count':0,'error':str(exc)[:250]})
   # Preserve old records if a source is temporarily unavailable.
   for key,entry in prior.items():
    if entry['funder']==source['name']:calls[key]=entry
 # Preserve manually curated records separately from automated discovery.
 for key,entry in prior.items():
  if entry.get('source')=='manual':calls[key]=entry
 output={'generated_at':now,'calls':sorted(calls.values(),key=lambda x:-x['score']), 'sources':results}
 old_path.write_text(json.dumps(output,ensure_ascii=False,indent=2)+'\n')
 print(f"Collected {len(calls)} candidates; {sum(s['status']=='error' for s in results)} source errors")
 if os.getenv('FAIL_ON_SOURCE_ERROR')=='1' and any(s['status']=='error' for s in results):raise SystemExit(1)

if __name__=='__main__':main()
