







import re
import json
import requests
from bs4 import BeautifulSoup
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt










# HelloWorld left in place for testing purposes.
@csrf_exempt
def hello_world(request):
    return HttpResponse("Hello, World!")








# receives a url from client and scrapes CBC.ca for story data
# facilitating the quick creation of a new article in the database.
@csrf_exempt
def getArticle(request):


    try:

        data    = json.loads(request.body)
        url     = data.get('url')
        
        print(f"Scraping story data from \n{url}\n")

        response = requests.get(url)
        soup     = BeautifulSoup(response.content, 'html.parser')

        # extract headline, date, and image data
        headline = soup.find('h1').text.strip()
        time     = soup.find('time', class_='timeStamp')
        date     = time['datetime'][:10]

        # extract image data
        wrapper  = soup.find('figure', class_='leadmedia-story')
        image    = wrapper.find('img')
        alt      = image['alt'] if image else None
        src      = image['src'] if image else None


        # Serialize the dictionary to JSON with ensure_ascii=False
        # to prevent unicode characters from being escaped.
        response_json = json.dumps([headline, date, src, alt], ensure_ascii=False)

        return HttpResponse(response_json, content_type='application/json')


    except Exception as e:
        print(f"An error occurred in the getArticle view function: {str(e)}")
        return HttpResponse("An error occurred gathering your story data", status=400)
   







# scrapes Caitlyn Gowriluk's CBC author page for story data
@csrf_exempt
def getNewStories(request):


    try:

        print(f"Checking CBC.ca for that new Caitlyn Gowriluk content...\n")
       
        # get existing article ids from client to prevent duplicates
#        existing_ids  = json.loads(request.body)

        url           = "https://www.cbc.ca/news/canada/manitoba/author/caitlyn-gowriluk-1.4845371"
        response      = requests.get(url)
        soup          = BeautifulSoup(response.content, 'html.parser')

        recentStories = soup.find("div", class_="contentListCards")
        storyList     = recentStories.find_all("a", class_="card")

        
        # extract story data iteratively
        stories = []
        for story in storyList:

            data_content_id = story["data-contentid"]

#            if data_content_id in existing_ids: continue

            img         = story.find("img")
            src         = img["src"]
            headline    = story.find("h3",  class_="headline"    ).text
            description = story.find("div", class_="description" ).text
            date        = story.find("time"                      )["datetime"]
            link        = story["href"]
            link        = "https://www.cbc.ca"+link if link[:18] != "https://www.cbc.ca" else link

            stories.append({"article_id": data_content_id, "image": src, "headline": headline, "description": description, "link": link, "date": date })

        # Serialize the list of dictionaries to JSON with ensure_ascii=False
        # to prevent unicode characters from being escaped.
        response_json = json.dumps(stories, ensure_ascii=False)

        return HttpResponse(response_json, content_type='application/json')

    except Exception as e:
            print(f"An error occurred in the getNewStories view function: {str(e)}")
            return HttpResponse("An error occurred gathering your new story data", status=400)






