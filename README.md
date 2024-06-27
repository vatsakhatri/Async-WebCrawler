# Async WebCrawler 
- Start Date: 2024-05-16
- Created by : Vatsa Khatri


## Introduction


In this documentation, we will understand the how to asynchronously crawl web pages using redis and celery



## ***Backend Configuration***


### Install dependencies


#### Adding the packages into the requirements file:


```
📁 requirements.txt -----

fastapi
uvicorn
celery
redis
beautifulsoup4
requests
```


#### Executing the installation command again to install the modified libraries in the project


```pip3 install -r requirements.txt```




## Celery Configuration


- File path: ```webcrawler/celery.py```




```
📁 webcrawler/celery.py

capp=Celery('myapp',broker='redis://localhost:6379/0',backend=
'redis://localhost:6379/0')

```
- ```broker & backend``` :  Redis is used as the message broker and result backend 


### Queue configuration


* #### Import tasks
    ```capp.conf.imports=('tasks',) ```
    
    Import the module named tasks where your Celery tasks are defined.
* #### Define Queues
    ``` 
    capp.conf.task_queues={
        'queue1': {
            'exchange': '',         # Default exchange
            'binding_key': 'queue1' # Routing key
        },
        'queue2': {
            'exchange': '',         # Default exchange
            'binding_key': 'queue2' # Routing key
        },
        'default': {
            'exchange': '',         # Default exchange
            'binding_key': 'default' # Routing key
        }
    }
    capp.conf.task_default_queue = 'default'
    ```
    When a task with a `Routing Key` arrives at the exchange which queue it has to be redirected to . The default queue is `default`
    

### Adding Tasks


* #### Registering the crawling task

```
📁 webcrawler/tasks.py


@capp.task(queue='queue1')
def crawl():

@capp.task(queue='queue2')
def ping_for_result(task_id):

```


1. `@capp.task(queue='')` is used to register a task as a celery task which will be added to queue & `queue=' '`is the routing key

2. The `crawl()` task will do the web-crawling.
3. The `ping_for_result(task_id)` task will be the monitor the status of crawling using its task_id


## WebCrawler

### Given a base URL i will  crawl the website upto a limit of 50 pages.

** **
### 1)  Extract all text from a page

```
def all_text_from_page(url):
    ress = requests.get(url)
    html_doc = ress.text
    clean_text = " ".join(BeautifulSoup(html_doc, "html.parser").stripped_strings)
    return clean_text
```
- ```requests.get(url, headers=headers)``` : using the requests lib hit the website get the response and extract the hmtl content    
- `BeautifulSoup(html_doc, "html.parser")`: For the html doc create a beautifulsoup object of type html parse.

- `.stripped_strings` : traverses the DOM and extracts all text content and then we join it using `.join()`.

** **

 ### 2) Extract all links from a pages
 
 ```
 def find_all_links(url, count):
    ress = requests.get(url, headers=headers)
    html_doc = ress.text

    soup = BeautifulSoup(html_doc, "html.parser")
   
    links = soup.find_all('a')
    for link in links:
        href = link.get('href')
        
        if href:
            full_url = urljoin(url, href)
            if full_url.startswith(base_domain) and full_url not in unique_links:
                if count > 50:
                    break
                # print("Found URL:", full_url)
                url_list.append(full_url)
                count += 1
                unique_links.add(full_url)
                print("Count:", count)
    return count


 ```

- Similar as above using `requests.get()` fetch html and create a obj which parse the html content
- `soup.find_all('a')` will find all the `<a></a>` tags and return a list.
- Iterate over the list and find all the link and add it to our `urls_list`.


** **

 ### 3) Summarize the website
 
 ```
@capp.task(queue='queue1')
def crawl():
    
    count = 1 
    current_index = 0
    
    while current_index < len(url_list) and count <= 1:
        current_url = url_list[current_index]
        count = find_all_links(current_url, count)
        current_index += 1
        
    txt=""

    for current in url_list :
        content = all_text_from_page(current)
        txt+=content# Or process the content as needed

    summarizer=Summarizer()
    summary=summarizer(txt,min_length=0,max_length=500)
    print(summary)

 ```
 
 - Given a base url first go the site extract all link add to url_list
 - Iterate over the newly added urls and visit that page and append links in that pages to the url_list
 - Do this till a maximum of 50 sites are hit or there is no more pages to visit.
 - Finally extract all content url_list and summarize  it.
 
 
** **

 ### 4) Ping for result 
 ```
 def ping_for_result task will call the (task_id):
    
    task=AsyncResult(task_id,backend=cel.backend)
    while task.status!="SUCCESS":
        time.sleep(5)
        print(task.status)
        task=AsyncResult(task_id,backend=cel.backend)
    
    complete_url = 'http://127.0.0.1:8000/complete' 
 ```
- `AsyncResult(task_id,backend=cel.backend)` will fetch the task details from redis and will keeping pinging till 'SUCCESS'.

 ## Endpoints
 
 - ### Create endpoints for two tasks

    ```
    @app.post('/crawl')
    def add_from_fast():
        task = crawl.delay()
        return {"task_id": task.id}

    @app.get("/ping/{id}")
    def get_status(id:str):

        ping_for_result.delay(id)
        return{"pinging started":"for status"}

    @app.post('/complete')
    def com():
        print("thee summary is finished")
        return {"ok":"ok"}

    ```
    - `crawl.delay()` will add the crawling task to the queue 
    - once the pinging is done the `ping_for_result` task will call the `/complete` to mark the finish of crawling.
