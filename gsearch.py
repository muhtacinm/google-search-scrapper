import requests
import re
import time
import json
import os

## HEADERS FOR GOOGLE SEARCH REQUESTS ##
google_headers = {
    'Host': 'www.google.com',
    'cache-control': 'max-age=0',
    'sec-ch-ua': '" Not;A Brand";v="99", "Google Chrome";v="97", "Chromium";v="97"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-full-version': '"97.0.4692.99"',
    'sec-ch-ua-arch': '"x86"',
    'sec-ch-ua-platform': '"Windows"',
    'sec-ch-ua-platform-version': '"10.0.0"',
    'sec-ch-ua-model': '""',
    'sec-ch-ua-bitness': '"64"',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-user': '?1',
    'sec-fetch-dest': 'document',
    'accept-language': 'en,en-CA;q=0.9,en-US;q=0.8,bn;q=0.7',
}

## HEADERS FOR ESPN API REQUESTS ##
espn_headers = {
    'authority': 'site.api.espn.com',
    'pragma': 'no-cache',
    'cache-control': 'no-cache',
    'sec-ch-ua': '" Not;A Brand";v="99", "Google Chrome";v="97", "Chromium";v="97"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'sec-fetch-site': 'cross-site',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-user': '?1',
    'sec-fetch-dest': 'document',
    'accept-language': 'en,en-CA;q=0.9,en-US;q=0.8,bn;q=0.7',
}

## STANDALONE INSTAGRAM SEARCH ##
def get_instagram(name):
    player=name.replace(" ", "+")
    html = requests.get('https://www.google.com/search?q='+ player +'+nba+instagram&hl=en', headers=google_headers)
    response = str(html.text)
    instagram = re.search('href="https:\/\/www.instagram.com\/([^"]+)"', response)
    if instagram:
        instagram= instagram.group(1)
        instagram = "https://www.instagram.com/"+instagram
    else:
        instagram=""
    return instagram
   
   
## STANDALONE TWITTER SEARCH ##    
def get_twitter(name):
    player=name.replace(" ", "+")
    html = requests.get('https://www.google.com/search?q='+ player +'+nba+twitter&hl=en', headers=google_headers)
    response = str(html.text)
    twitter = re.search('href="https:\/\/twitter.com\/([^"]+)"', response)
    if twitter:
        twitter= twitter.group(1)
        twitter="https://twitter.com/"+ twitter
    else:
        twitter=""
    return twitter


## GOOGLE ALL SEARCH ##
def get_all_social(name):
    player=name.replace(" ", "+")
    html = requests.get('https://www.google.com/search?q='+ player +'+nba&hl=en', headers=google_headers)
    response = str(html.text)

    ## REGEX MATCHES FOR SOCIAL MEDIA ##
    twitter = re.search('<g-link class="fl"><a.*\shref="https:\/\/.*twitter.com\/([^"]+)"', response)
    instagram = re.search('<g-link class="fl"><a.*\shref="https:\/\/www.instagram.com\/([^"]+)"', response)
    facebook = re.search('<g-link class="fl"><a.*\shref="https:\/\/www.facebook.com\/([^"]+)"', response)
    
    ## CHECK IF TWITTER MATCH EXISTS  (IF NOT USE TWITTER STANDALONE FUNCTION FOR ONE MORE CHECK) ##
    if twitter:
        twitter= twitter.group(1)
        twitter = re.sub(r'&amp;.*', '', twitter)
        twitter="https://twitter.com/"+ twitter
    else:
        twitter=get_twitter(name) 
    
    ## CHECK IF INSTAGRAM MATCH EXISTS  (IF NOT USE INSTAGRAM STANDALONE FUNCTION FOR ONE MORE CHECK) ##            
    if instagram:
        instagram= instagram.group(1)
        instagram="https://www.instagram.com/"+instagram
    else:
        instagram=get_instagram(name)
    
    ## CHECK IF FACEBOOK MATCH EXISTS ##    
    if facebook:
        facebook= facebook.group(1)
        facebook="https://www.facebook.com/"+facebook
    else:
        facebook=""
        
    return twitter, instagram, facebook

## ESPN GET TEAMS AND ID ##
def get_teams():
    the_data = []
    i = 1
    while i <= 30:
        response = requests.get('https://site.api.espn.com/apis/site/v2/sports/basketball/nba/teams/'+ str(i) + '/roster', headers=espn_headers)
        data = response.json()
        team=data['team']['displayName']
        logo=data['team']['logo']
        team_data = {"id": i , "team": team, "logo": logo}
        the_data.append(team_data)
        i+=1
     
    the_data=json.dumps(the_data, indent=4)
    save_to_json("teams", the_data)
    print (the_data)
     
## ESPN GET PLAYERS AND GOOGLE SEARCH SOCIAL MEDIA ##
def get_players():
    the_data = []
    i=1
    ## LOOP THROUGH 30 TEAMS ##
    while i <= 30: 
        response = requests.get('https://site.api.espn.com/apis/site/v2/sports/basketball/nba/teams/'+ str(i) + '/roster', headers=espn_headers)
        data = response.json()
        team=data['team']['displayName']
        print("Getting data for " + team)
        for value in data['athletes']:
            name=value['fullName']
            position=value['position']['abbreviation']
            jersey=value['jersey']
            try:
                headshot=value['headshot']['href']
            except:
                headshot=""
            twitter, instagram, facebook= get_all_social(name)
            player_data = {"name": name , "position": position ,"jersey": jersey, "headshot": headshot, "twitter": twitter, "instagram": instagram, "facebook": facebook}
            the_data.append(player_data)
            print(player_data)
            time.sleep(10) ## ADD SLEEP TO TIMEOUT GOOGLE SEARCH A LITTLE
        the_data=json.dumps(the_data, indent=4)
        save_to_json(team, the_data)
        the_data = []
        i+=1       
    
## SAVE ALL PLAYER DATA INCLUDING SOCIAL MEDIA ACCOUNTS TO JSON ##
def save_to_json(team, data):
    team=(team.replace(" " , "_")).lower()
    
    ## FILE PATH ##
    filename = team +".json"
    dirname = os.path.dirname(__file__)
    path = os.path.join(dirname, 'json_data')
    fullpath = os.path.join(path, filename)
    
    ## SAVE TO FILE ##
    file = open(fullpath, 'w')
    file.write(data)
    file.close()
    print("Saved " + filename )
    
get_players()