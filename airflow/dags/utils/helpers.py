import requests
from bs4 import BeautifulSoup


def generate_npr_feed_urls():
    """
    Generate a list of NPR RSS feed URLs by scraping the NPR Aggregation Table.
    """

    # set url consts that well use later on
    AGG_TABLE_URL = "https://npr.github.io/content-distribution-service/faq/table-of-aggregations.html"
    RSS_BASE_URL = "https://www.npr.org/rss/rss.php"

    # grab the agg table's webpage so we can extract its content
    res = requests.get(
        url=AGG_TABLE_URL,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            + "AppleWebKit/537.36 (KHTML, like Gecko) "
            + "Chrome/120.0.0.0 Safari/537.36"
        },
    )
    soup = BeautifulSoup(res.text, "html.parser")
    topics, programs, blogs = soup.find_all("table")

    # iterate over available tables to get IDs and construct RSS feed URLs
    feed_urls = []
    for i, table in enumerate([topics, programs, blogs]):
        for row in table.find_all("tr"):
            try:
                collection_name, collection_id = row.find_all("td")
                url = f"{RSS_BASE_URL}?id={collection_id.text.strip()}"
                feed_urls.append(url)
            except:
                pass  # case of table header

    return feed_urls


def request_rss_feed(rss_feed_url: str) -> dict[str, str] | None:
    res = requests.get(rss_feed_url, timeout=10)
    if res.status_code != 200:
        print(f"Error retrieving XML document for {rss_feed_url}: {res.status_code}")
        return None

    return {
        "rss_url": rss_feed_url,
        "xml_doc": res.text,
    }
