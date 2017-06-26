from bs4 import BeautifulSoup
import requests
import shutil


class ScrapePGN(object):
    BASE = 'http://www.pgnmentor.com'
    SOURCE = 'http://www.pgnmentor.com/files.html'

    @classmethod
    def scrape(cls):
        page = requests.get(cls.SOURCE).content
        soup = BeautifulSoup(page, 'html.parser')
        links = []
        for anchor in soup.find_all('a'):
            href = anchor.attrs.get('href', '')
            if '.zip' in href and 'players' in href:
                links.append('{}/{}'.format(cls.BASE,
                                            href))
        # links = [link for link in soup.find_all('a')
        #          if '.zip' in link.attrs.get('href', '')]
        # print(links)
        return links

    @classmethod
    def download_file(cls, url):
        local_filename = url.split('/')[-1]
        r = requests.get(url, stream=True)
        with open(local_filename, 'wb') as f:
            shutil.copyfileobj(r.raw, f)

        return local_filename