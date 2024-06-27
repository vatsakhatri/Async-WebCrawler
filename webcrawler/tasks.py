import time
from celer import capp
import os
from celer import capp as cel
from summarizer import Summarizer
from bs4 import BeautifulSoup
import requests
from urllib.parse import urljoin, urlparse
from celery.result import AsyncResult
url_list = []

unique_links = set()

    # Start URL
start_url = ""
url_list.append(start_url)
parsed_url = urlparse(start_url)
base_domain = f"{parsed_url.scheme}://{parsed_url.netloc}"
print("Base domain:", base_domain)


def all_text_from_page(url):
    
    ress = requests.get(url)
   
    html_doc = ress.text
    clean_text = " ".join(BeautifulSoup(html_doc, "html.parser").stripped_strings)
    return clean_text
def find_all_links(url, count):
    
    
    ress = requests.get(url)
    html_doc = ress.text

    soup = BeautifulSoup(html_doc, "html.parser")
   
    links = soup.find_all('a')
    for link in links:
        href = link.get('href')
        
        if href:
            full_url = urljoin(url, href)
            if full_url.startswith(base_domain) and full_url not in unique_links:
                if count > 1:
                    break
                # print("Found URL:", full_url)
                url_list.append(full_url)
                count += 1
                unique_links.add(full_url)
                print("Count:", count)
    return count




@capp.task(queue='queue1')
def crawl():
    
    print("=======started")
    count = 1  # Start with 1 since the start_url is already in the list
    current_index = 0
    while current_index < len(url_list) and count <= 1:
        current_url = url_list[current_index]
        print("Current URL:", current_url)
        count = find_all_links(current_url, count)
        current_index += 1
 
    txt=""

    for current in url_list :
        
        
        #print("Current URL:", current)
        content = all_text_from_page(current)
        
        txt+=content# Or process the content as needed

    summarizer=Summarizer()
    summary=summarizer(txt,min_length=0,max_length=500)
    print(summary)
    print("Crawling finished. Total unique links found:", len(unique_links))
    time.sleep(15)
    print("=======end")
    
    
    
@capp.task(queue='queue2')
def ping_for_result(task_id):
    print("=======started checking status")
    # Ensure task_id is the actual ID of the task
    task=AsyncResult(task_id,backend=cel.backend)
    while task.status!="SUCCESS":
        time.sleep(5)
        print(task.status)
        task=AsyncResult(task_id,backend=cel.backend)
    
    complete_url = 'http://127.0.0.1:8000/complete'  # Replace with your actual endpoint URL
    response = requests.post(complete_url)
    
    return     

