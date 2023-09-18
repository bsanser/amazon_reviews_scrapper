from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
from rich import print
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

def get_global_ratings(page):
  try:
    global_html = get_html(page,f'https://www.amazon.com/product-reviews/{asin}?th=1')
    global_rating = {
      "average_star_rating" : [float(global_html.find("i", attrs={'data-hook': 'average-star-rating'}).string.replace(' out of 5 stars', '').strip())],
      "total_review_count" : [int(global_html.find_all(class_='averageStarRatingNumerical')[0].string.replace(' global ratings', '').replace(',', '').strip())],
    }
    
    rows = global_html.find_all('tr', class_="a-histogram-row")
    for row in rows:
      cells = row.find_all("td")
      rating = cells[0].find('a', class_="a-link-normal").text.strip()
      percentage = cells[2].find('a', class_="a-link-normal").text.strip()
      global_rating[rating]=[percentage]
    
    return global_rating
  except:
        pass
  
def save(results, name):
  df = pd.DataFrame(results)
  df.to_excel(f'{asin}-{name}.xlsx', index = False)

def run():
  pw = sync_playwright().start()
  browser = pw.chromium.launch()
  page = browser.new_page()
  save(get_global_ratings(page),"global-rating")
  for x in range(2000):
    soup = get_html(page,f'https://www.amazon.com/product-reviews/{asin}/ref=cm_cr_arp_d_paging_btm_next_2?ie=UTF8&reviewerType=all_reviews&sortBy=recent&pageNumber={x+1}')
    get_reviews(soup)
    if not soup.find('li', {'class': 'a-disabled a-last'}):
        pass
    else:
        break 
  browser.close()
  pw.stop()
  
  save(reviews_list,"reviews-list")
  print('Fin')

def main():
  run()

if __name__ == "__main__":
  main()