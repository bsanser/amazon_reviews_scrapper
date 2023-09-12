from playwright.sync_api import sync_playwright
from selectolax.parser import HTMLParser
from dataclasses import dataclass
from rich import print

@dataclass
class ReviewItem:
  asin: str
  product_title: str
  size: str
  date: str
  country: str
  rating: float
  title: str
  body: str
  verified_purchase: str 
  people_who_found_helpful: int
  author: str


def get_html(page, asin):
  url= f"https://www.amazon.com/dp/{asin}"
  page.goto(url)
  page.wait_for_selector("#cm-cr-dp-review-list")
  html = HTMLParser(page.content())
  return html

def parse_html(html, asin):
  date_country_string = html.css_first("#customer_review-R3UWUBUOZUDI2B > span").text(strip=True)
  country_split_word = "the"
  date_split_word = "on"
  country = date_country_string.split(country_split_word,1)[1].split(date_split_word, )[0]
  date = date_country_string.split(date_split_word,1)[1]
  review_item = ReviewItem(
    asin = asin,
    product_title = html.css_first("span#productTitle").text(strip=True),
    size = html.css_first("#customer_review-R3UWUBUOZUDI2B > div.a-row.a-spacing-mini.review-data.review-format-strip > span").text(strip=True)[6:],
    date = date.strip(),
    country = country.strip(),
    rating = float(html.css_first("#customer_review-R3UWUBUOZUDI2B > div:nth-child(2) > a > i").text(strip=True)[:3]),
    title = html.css_first("#customer_review-R3UWUBUOZUDI2B > div:nth-child(2) > a > span:nth-child(3)").text(strip=True),
    body = html.css_first("#customer_review-R3UWUBUOZUDI2B > div.a-row.a-spacing-small.review-data > span > div > div.a-expander-content.reviewText.review-text-content.a-expander-partial-collapse-content > span").text(strip=True),
    verified_purchase = html.css_first("#customer_review-R3UWUBUOZUDI2B > div.a-row.a-spacing-mini.review-data.review-format-strip > a > span").text(strip=True),
    people_who_found_helpful = int(html.css_first("#customer_review-R3UWUBUOZUDI2B > div.a-row.review-comments.cr-vote-action-bar > span.cr-vote > div.a-row.a-spacing-small > span").text(strip=True).split(" ", 1)[0]),
    author = html.css_first("#customer_review-R3UWUBUOZUDI2B > div:nth-child(1) > a > div.a-profile-content > span").text(strip=True)
  )
  return review_item

def run():
  asin = "B0C4FT6Q1F"
  pw = sync_playwright().start()
  browser = pw.chromium.launch()
  page = browser.new_page()
  html = get_html(page,asin)
  review_item = parse_html(html, asin)
  print(review_item)


def main():
  run()

if __name__ == "__main__":
  main()