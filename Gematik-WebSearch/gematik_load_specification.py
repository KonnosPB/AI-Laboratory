import os
from dotenv import load_dotenv
from langchain_community.document_loaders import SitemapLoader

load_dotenv()

def loadSiteMapInto():
    url = os.getenv("GEMATIK_SPEC_URL")
    filter = os.getenv("GEMATIK_SPEC_SITE_FILTER")
    loader = SitemapLoader(
        web_path=url,
        filter_urls=filter,
        restrict_to_same_domain=True,
        #continue_on_failure = True,
    )
    loader.fetch_all(urls=[url])
    documents = loader.lazy_load()
    if (not documents):
        return
    for document in documents:
        print("".format(document.name))


loadSiteMapInto();