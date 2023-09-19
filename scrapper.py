from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
from rich import print
import pandas as pd
from pandas import ExcelWriter
import csv

reviews_list = []

def get_html(page,url):
  page.goto(url)
  html = BeautifulSoup(page.content(), 'html.parser')
  return html

   
def get_reviews(html):
    reviews = html.find_all('div', {'data-hook': 'review'})
    date_split_word = "on "
    title_split_word = "stars\n"
    # TO DO: Clean the field for country. country_split_word = "Reviewed in the", "Reviewed in" 
  
    try:
        for item in reviews:
            review = {
              'product': html.title.text.replace('Amazon.com:Customer reviews:', '').strip(),
              "country": item.find('span', {'data-hook': 'review-date'}).text.strip().split(date_split_word,1)[0].strip(),
              'date':  item.find('span', {'data-hook': 'review-date'}).text.strip().split(date_split_word,1)[1],
              'rating': float(item.find('i', {'data-hook': 'review-star-rating'}).text.replace('out of 5 stars', '').strip()),
              'title': item.find('a', {'data-hook': 'review-title'}).text.strip().split(title_split_word,1)[1],
              'body': item.find('span', {'data-hook': 'review-body'}).text.strip(),
            }
            reviews_list.append(review)
    except:
        pass

def get_global_ratings(page, asin):
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
  
def save(results, name, asin):
  df = pd.DataFrame(results)
  df.to_excel(f'{asin}-{name}.xlsx', index = False)
  # TO DO: create a excel writer object (necessary to write to different sheets in the same excel file)
  # with pd.ExcelWriter(f'{asin}-amazon.xlsx') as writer:
  #   df = pd.DataFrame(results)
  #   df.to_excel(writer, sheet_name=name, index=False)

# def save_to_csv(results, asin, name):
#    f = open(f'{asin}-{name}.csv', 'w')
#    writer = csv.writer(f)
#    writer.writerow(results)
#    f.close()

   

def read_products_csv():
  with open('amazon-asins.csv', 'r') as f:
   reader = csv.reader(f)
   return [item[0] for item in reader]


def run(asin):
  pw = sync_playwright().start()
  browser = pw.chromium.launch()
  page = browser.new_page()
  print(f'Scrapping info for product {asin} ⏳')
  # save_to_csv(reviews_list,asin, "global-rating")
  # save(get_global_ratings(page, asin),"global-rating", asin)
  for x in range(2000):
    soup = get_html(page,f'https://www.amazon.com/product-reviews/{asin}/ref=cm_cr_arp_d_paging_btm_next_2?ie=UTF8&reviewerType=all_reviews&sortBy=recent&pageNumber={x+1}')
    get_reviews(soup)
    if not soup.find('li', {'class': 'a-disabled a-last'}):
        pass
    else:
        break 
  browser.close()
  pw.stop()
  # save_to_csv(reviews_list,asin, "reviews-list")
  # save(reviews_list,"reviews-list", asin)
  df = pd.DataFrame(reviews_list)
  print(df.head())
  print(f'Info for product {asin} retrieved correctly 🥳')

def main():
  asins = read_products_csv()
  for asin in asins:
    run(asin)

if __name__ == "__main__":
  main()