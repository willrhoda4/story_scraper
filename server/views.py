







import re
import json
import requests

from   django.views.decorators.csrf import csrf_exempt
from   django.http                  import HttpResponse
from   bs4                          import BeautifulSoup as bs




# HelloWorld left in place for testing purposes
@csrf_exempt
def hello_world(request):
    return HttpResponse("Hello, World!")




# recieves a list of IMDB ids from client and scrapes
# imdb.com for all the stunt credits associated with each id,
# counts the  number of credits, deduplicates the list using set()
# then returns the total amount and the list.
@csrf_exempt
def getFlicks(request):

    try:

        data = json.loads(request.body)
        team = data.get('team', []) 
        print(f"Retrieving flicklist for the following team members:\n{team}\n")

        all_films = []

        for member in team:

            # scrape html from member's fullcredits page
            url        = f"https://www.imdb.com/name/{member}/fullcredits"
            response   = requests.get(url)
            soup       = bs(response.content, "html.parser")

            # extract IMDB ids for films from CSS ids.
            stunt_divs = soup.find_all("div", id=re.compile(r"stunts-tt\w+"))
            film_ids   = [film["id"][7:] for film in stunt_divs]
            all_films += film_ids
            

        # note total then deduplicate
        total_credits  = len(all_films)
        all_films      = list(set(all_films))


        return HttpResponse(json.dumps([total_credits, all_films]))


    except Exception as e:

        print(f"An error occurred in the getFlicks view function: {str(e)}")
        return HttpResponse("An error occurred gathering the flick list", status=400)

    
    


    
# receives the IMDB id for a film and checks
# imdb.com for an associated title and poster url,
# then ships back client. 
@csrf_exempt
def getPoster(request):

    try:

        data      = json.loads(request.body)
        imdbId    = data.get('imdbId', [])
        print(f"Trying to find data for this IMDB id: {imdbId}\n")


        # headers and session stop IMDB from smelling a scraper. 
        url        = f"https://www.imdb.com/title/{imdbId}/"
        headers    = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        session    = requests.Session()

        # go grab the json
        response   = session.get(url, headers=headers)
        film_soup  = bs(response.content, features="lxml")
        film_json  = film_soup.find("script", type="application/ld+json")

        if film_json:

            # if there's no poster, send back 'no poster' in lieu of url,
            # so the database knows not to look for it again during further searches.
            json_dict = json.loads(film_json.string)
            name      = json_dict.get( "name",  ""          )
            image     = json_dict.get( "image", "no poster" )
            
            return HttpResponse(json.dumps([name, imdbId, image]))

        # if there's no json, we got a problem.
        else: return HttpResponse("An error occurred with your poster JSON", status=400)

    except Exception as e:

        print(f"An error occurred in the getPoster view function: {str(e)}")
        return HttpResponse("An error occurred getting a poster", status=400)
