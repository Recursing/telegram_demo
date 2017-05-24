from urllib.request import urlopen
import xml.etree.ElementTree as ET


def get_articles():
    html_source = urlopen("https://www.gulp.linux.it/feed/").read().decode()
    root = ET.fromstring(html_source)
    items = root.find('channel').findall('item')
    for e in items:
        yield {'title': e.find('title').text,
               'link': e.find('link').text}
