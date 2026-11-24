import requests
from datetime import datetime
import json

CACHE_PATH = rCACHE_PATH = r"/Users/krishnannarayanan/.cache/leetcode/leetcode.json"
LEETCODE_URL = "https://leetcode.com/graphql"
CONTENT_TYPE = "Content-Type"
APPLICATION_JSON = "application/json"
REFERER_HEADER = "Referer"
REFERER_RESPONSE = "https://leetcode.com"
DATE = "DATE"
DATA_KEY = "data"
DATE_TIME_FORMAT = "%Y-%m-%d %H:%M:%S"

#POTD
POTD_STATS = "POTD_STATS"

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
    try:
        with open(CACHE_PATH, "r") as file:
            data = json.load(file)
        return data
    except Exception as e:
        return {}

def writing_json_to_cache(jsonValue, key):
    jsonValue = construct_value(jsonValue,key)

    with open(CACHE_PATH, "w") as file:
        data = json.dump(jsonValue,file,indent=4)

def construct_value(jsonValue, key):
    cur_date = current_date()
    return {
        key: {
            DATA_KEY: jsonValue,
            DATE: cur_date
        }
    }

def current_date():
    return datetime.now().strftime(DATE_TIME_FORMAT)

def date_to_string(date_str):
    return datetime.strptime(date_str,DATE_TIME_FORMAT)

def fetch_value_cached(key):
    data = reading_json_from_cache()
    if data == None or data.get(key) == None:
        return None
    date =  data.get(key).get(DATE)
    if date == None:
        return None
    cur_date = current_date()
    return data.get(key).get(DATA_KEY) if cur_date == date else None

def call_api(url, body):
    headers = construct_headers()
    return requests.post(url=url, headers=headers, json=body).json()

def potd_stats():
    response_json = fetch_value_cached(POTD_STATS)
    if response_json == None:
        response_json = call_api(LEETCODE_URL, {"query": POTD_BODY})
        writing_json_to_cache(response_json,POTD_STATS)
