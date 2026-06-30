import requests, sqlite3, time
from bs4 import BeautifulSoup

BASE_URL = "https://a.111477.xyz/"
TARGET_DIRS = ["movies/", "tvs/"]
EXTENSIONS = ('.mkv', '.mp4', '.avi')
HEADERS = {'User-Agent': 'PersonalKodiSearchIndex/1.0 (Compliant Crawler)'}

def crawl():
    conn = sqlite3.connect('media.db')
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS media (title TEXT, url TEXT)')
    
    def process_dir(url, depth=0):
        if depth > 3: return
        try:
            r = requests.get(url, headers=HEADERS, timeout=10)
            time.sleep(1.0) # Polite rate limiting
            soup = BeautifulSoup(r.text, 'html.parser')
            for a in soup.find_all('a', href=True):
                href = a['href']
                if href == '../': continue
                if href.lower().endswith(EXTENSIONS):
                    c.execute('INSERT INTO media VALUES (?, ?)', (href, url + href))
                elif href.endswith('/'):
                    process_dir(url + href, depth + 1)
        except Exception: pass

    for d in TARGET_DIRS: process_dir(BASE_URL + d, 0)
    conn.commit()
    conn.close()
    
    # Save a timestamp for Kodi to check against
    with open('timestamp.txt', 'w') as f:
        f.write(str(time.time()))

if __name__ == "__main__":
    crawl()
