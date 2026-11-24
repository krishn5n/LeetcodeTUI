import requests
import json

CACHE_PATH = r"/home/krishnannarayanan/.cache/leetcode/leetcode.json"
LEETCODE_URL = "https://leetcode.com/graphql"
CONTENT_TYPE = "Content-Type"
APPLICATION_JSON = "application/json"
REFERER_HEADER = "Referer"
REFERER_RESPONSE = "https://leetcode.com"

CURRENT_POTD = "CURRENT_POTD"

POTD_BODY = """ 
    query dailyChallenge { 
        activeDailyCodingChallengeQuestion { 
            date 
            userStatus 
            link 
            question { 
                questionFrontendId 
                title 
                titleSlug 
                difficulty 
                acRate 
            } 
        } 
    } 
"""

def construct_headers():
    return {
        CONTENT_TYPE: APPLICATION_JSON,
        REFERER_HEADER: REFERER_RESPONSE
    }

def reading_json_from_cache():
    with open(CACHE_PATH, "r") as file:
        data = json.load(file)
    return data


def current_potd():
    headers = construct_headers()    
    response_json = requests.post(url=LEETCODE_URL, headers=headers, json={"query": POTD_BODY}).json()
    data = reading_json_from_cache()
    data[CURRENT_POTD] = response_json 