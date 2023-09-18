from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
from rich import print
import json
import pandas as pd

reviews_list = []
asin = "B0C4FT6Q1F"

def get_html(page,url):
  page.goto(url)
  html = BeautifulSoup(page.content(), 'html.parser')
  return html

def get_reviews(html):
    reviews = html.find_all('div', {'data-hook': 'review'})
    date_split_word = "on "
    title_split_word = "stars\n"
  
    try:
        for item in reviews:
            review = {
              'product': html.title.text.replace('Amazon.com:Customer reviews:', '').strip(),
              'date':  item.find('span', {'data-hook': 'review-date'}).text.strip().split(date_split_word,1)[1],
              'rating': float(item.find('i', {'data-hook': 'review-star-rating'}).text.replace('out of 5 stars', '').strip()),
              'title': item.find('a', {'data-hook': 'review-title'}).text.strip().split(title_split_word,1)[1],
              'body': item.find('span', {'data-hook': 'review-body'}).text.strip(),
            }
            reviews_list.append(review)
    except:
        pass

def save(results):
   with open (asin + '-reviews.json','w') as f:
      json.dump(results, f)

def run():
  pw = sync_playwright().start()
  browser = pw.chromium.launch()
  page = browser.new_page()
  global_html = get_html(page,f'https://www.amazon.com/product-reviews/{asin}?th=1')
  average_star_rating = float(global_html.find("i", attrs={'data-hook': 'average-star-rating'}).string.replace(' out of 5 stars', '').strip())
  total_review_count =  int(global_html.find_all(class_='averageStarRatingNumerical')[0].string.replace(' global ratings', '').replace(',', '').strip())
  global_ratings = {}
  rows = global_html.find_all('tr', class_="a-histogram-row")
  for row in rows:
    cells = row.find_all("td")
    rating = cells[0].find('a', class_="a-link-normal").text.strip()
    percentage = cells[2].find('a', class_="a-link-normal").text.strip()
    global_ratings[rating]=percentage
  
  print(f'Average rating: {average_star_rating}')
  print(f'Total number of reviews: {total_review_count}')
  print(f'Rating distribution: {global_ratings}')

  for x in range(10):
    soup = get_html(page,f'https://www.amazon.com/product-reviews/{asin}/ref=cm_cr_arp_d_paging_btm_next_2?ie=UTF8&reviewerType=all_reviews&sortBy=recent&pageNumber={x+1}')
    print(f'Getting page: {x}')
    get_reviews(soup)
    save(reviews_list)
    if not soup.find('li', {'class': 'a-disabled a-last'}):
        pass
    else:
        break
    


def main():
  run()

if __name__ == "__main__":
  main()