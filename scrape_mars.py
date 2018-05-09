from splinter import Browser
import selenium
from selenium import webdriver
from bs4 import BeautifulSoup as bs
import pandas as pd
import requests
import time

def scrape():
    scrape_dict = {}
    # NASA Mars News

    news_url = "https://mars.nasa.gov/news/"
    news_response=requests.get(news_url)

    news_soup = bs(news_response.text,'lxml')
    #print(news_soup.prettify())

    news_title = news_soup.find("div",class_="content_title").text.strip()
    news_text = news_soup.find("div",class_="rollover_description").text.strip()

    scrape_dict["news_title"] = news_title
    scrape_dict["news_text"] = news_text

    # ### JPL Mars Space Images - Featured Image
    try:
        executable_path = {'executable_path': 'chromedriver.exe'}
        browser = Browser('chrome', **executable_path, headless=False)
    except selenium.common.exceptions.WebDriverException:
        executable_path = {'executable_path': '/usr/local/bin/chromedriver'}
        browser = Browser('chrome', **executable_path, headless=False)

    jpl_url = "https://www.jpl.nasa.gov/spaceimages/?search=featured&category=Mars"
    jpl_url_base = "https://www.jpl.nasa.gov"

    browser.visit(jpl_url)

    #Not always Mars-related, but okay.
    #more info returns ElementNotVisible exception
    #browser.click_link_by_partial_text('FULL IMAGE')
    
    jpl_soup = bs(browser.html, 'lxml')
    jpl_img_path = jpl_soup.find("a",class_="button fancybox")["data-fancybox-href"]
    
    #browser.click_link_by_partial_text('more info')

    # try:
    #     browser.click_link_by_partial_href('/spaceimages/images/large')
    # except:
    #     print("images/large link sucked.")
    #     return

    #jpl_img = browser.url
    jpl_img = jpl_url_base + jpl_img_path
    scrape_dict["jpl_img"] = jpl_img

    # ### Mars Weather Report

    weather_url = "https://twitter.com/marswxreport?lang=en"
    weather_response = requests.get(weather_url)

    weather_soup = bs(weather_response.text,'lxml')
    #print(weather_soup.prettify())

    mars_weather = weather_soup.find("p", class_="tweet-text").text
    scrape_dict["mars_weather"] = mars_weather

    # ### Mars Facts

    facts_url = "https://space-facts.com/mars/"

    facts_df=pd.read_html(facts_url)[0]

    facts_df.columns = ["description","value"]
    facts_df.set_index("description", inplace=True)

    facts_table = facts_df.to_html()

    scrape_dict["facts_table"] = facts_table

    # ### Mars Hemispheres

    hem_url = "https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars"
    hem_base_url = "https://astrogeology.usgs.gov"

    browser.visit(hem_url)

    hem_soup = bs(browser.html, 'lxml')
    #print(hem_soup.prettify())

    hem_items = hem_soup.find_all("div", class_="item")
    hem_links = [hem_base_url+x.a["href"] for x in hem_items]

    hem_images = []
    for link in hem_links:
        browser.visit(link)
        #print(browser.html)

        hem_soup = bs(browser.html,'lxml')
        #print(hem_soup.prettify())
        
        hem_entry = {}
        hem_entry["title"] = hem_soup.title.text.split(" Enhanced")[0]
        hem_entry["img_url"] = hem_soup.find("a", text="Sample")["href"]
        hem_images.append(hem_entry)


    scrape_dict["hem_images"] = hem_images

    return scrape_dict