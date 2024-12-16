import os
import re
import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
import json

class SitemapSpider(CrawlSpider):
    name = 'sitemap_spider'
    allowed_domains = ['gemspec.gematik.de']
    start_urls = ['https://gemspec.gematik.de/']

    rules = (
        Rule(LinkExtractor(allow=('/docs/', '/downloads/'), deny=('/Aend/',)), callback='parse_item', follow=True),
    )

    latest_urls = {}

    def parse_item(self, response):
        self.logger.info('Visited %s', response.url)

        # Extrahiere spezifische Download-Links
        download_links = response.css('a::attr(href)').extract()
        for link in download_links:
            if re.search(r'/downloads/.*\.html$', link) and 'Aend' not in link:
                full_url = response.urljoin(link)
                self.logger.info('Found HTML download link: %s', full_url)
                self.process_link(full_url)

        # Prüfe auf "latest" URLs und extrahiere die spezifische Version, falls vorhanden
        if '/latest/' in response.url:
            self.handle_latest_url(response)

    def process_link(self, url):
        # Extrahiere die Basis-URL und die Versionsnummer
        match = re.search(r'(.*?)(V\d+\.\d+\.\d+)(.*)', url)
        if match:
            base_url = match.group(1) + match.group(3)  # Basis-URL ohne Versionsnummer
            version = match.group(2)  # Versionsnummer

            # Überprüfen, ob die Basis-URL bereits im Dictionary vorhanden ist
            if base_url in self.latest_urls:
                # Vergleiche die Versionsnummern
                existing_version = re.search(r'V\d+\.\d+\.\d+', self.latest_urls[base_url]['url']).group(0)
                if version > existing_version:
                    self.latest_urls[base_url] = {'url': url, 'version': version}
            else:
                self.latest_urls[base_url] = {'url': url, 'version': version}

    def handle_latest_url(self, response):
        # Suche nach Links auf der Seite, die spezifische Versionen enthalten
        download_links = response.css('a::attr(href)').extract()
        for link in download_links:
            if re.search(r'/downloads/.*V\d+\.\d+\.\d+.*\.html$', link) and 'Aend' not in link:
                specific_version_url = response.urljoin(link)
                self.logger.info('Found specific version link: %s', specific_version_url)
                self.process_link(specific_version_url)
                return

    def close(self, reason):
        # Datei löschen, falls vorhanden
        if os.path.exists("sitemap.json"):
            os.remove("sitemap.json")

        # Ausgabe der neuesten URLs am Ende des Crawls
        with open('sitemap.json', 'w') as f:
            json.dump([{'url': entry['url']} for entry in self.latest_urls.values()], f, indent=2)

# Datei löschen, falls vorhanden
# if os.path.exists("sitemap.json"):
#     os.remove("sitemap.json")

# Scrapy-Spider ausführen und Ausgabe in sitemap.json speichern
#subprocess.run(["scrapy", "crawl", "sitemap_spider"])
