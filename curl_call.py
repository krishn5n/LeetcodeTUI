import requests
from datetime import datetime
import json

CACHE_PATH = r"/Users/krishnannarayanan/.cache/leetcode/leetcode.json"
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
POTD_DETAIL = "POTD DETAIL"
POTD_QUESTION_BODY = "POTD_QUESTION_BODY"

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

POTD_DETAIL_BODY = """
    query questionOfToday {
        activeDailyCodingChallengeQuestion {
            date
            link
            question {
                questionFrontendId
                title
                titleSlug
                difficulty
                content
                exampleTestcases
                topicTags {
                    name
                }
            }
        }
    }
"""

POTD_QUESTION_BODY = """
    query questionData {
        question(
            titleSlug: "?"
        ) {
            questionId
            questionFrontendId
            title
            titleSlug
            difficulty
            content
            exampleTestcases
            metaData
            codeSnippets {
                lang
                langSlug
                code
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

def writing_json_to_cache(totalJson, fetchedJson, key):
    construct_value(totalJson, fetchedJson,key)

    with open(CACHE_PATH, "w") as file:
        totalJson = json.dump(totalJson,file,indent=4)

def construct_value(totalJson, fetchedJson, key):
    if totalJson == None:
        totalJson = {}
    cur_date = current_date()
    formattedJson = {
        DATA_KEY: fetchedJson,
        DATE: cur_date
    }
    totalJson[key] = formattedJson

def current_date():
    return datetime.now().strftime(DATE_TIME_FORMAT)

def date_to_string(date_str):
    return datetime.strptime(date_str,DATE_TIME_FORMAT)

def fetch_value_cached(data, key):
    data = reading_json_from_cache()
    if data == None or data.get(key) == None:
        data = {}
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
    jsonFile = {}
    response_json = fetch_value_cached(jsonFile, POTD_STATS)
    if response_json == None:
        response_json = call_api(LEETCODE_URL, {"query": POTD_BODY})
        writing_json_to_cache(jsonFile, response_json,POTD_STATS)

def potd_detail():
    jsonFile = {}
    response_json = fetch_value_cached(jsonFile, POTD_DETAIL)
    if response_json == None:
        response_json = call_api(LEETCODE_URL, {"query": POTD_DETAIL_BODY})
        writing_json_to_cache(jsonFile, response_json, POTD_DETAIL)