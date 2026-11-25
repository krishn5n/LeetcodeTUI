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
POTD_QUESTION = "POTD_QUESTION"

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
        totalJson.update({})
    cur_date = current_date()
    formattedJson = {
        DATA_KEY: fetchedJson,
        DATE: cur_date
    }
    totalJson[key] = formattedJson

def find(s, ch):
    return [i for i, ltr in enumerate(s) if ltr == ch]

def replacing_placeholders(text: str,values: list):
    indices = find(text,"?")
    listOfText = list(text)
    for i,n in enumerate(indices):
        listOfText[n] = values[i]
    return ''.join(listOfText)

def current_date():
    return datetime.now().strftime(DATE_TIME_FORMAT)

def string_to_date(date_str):
    return datetime.strptime(date_str,DATE_TIME_FORMAT)

def fetch_value_cached(key):
    data = reading_json_from_cache()
    if data == None or data.get(key) == None:
        return None
    date =  data.get(key).get(DATE)
    if date == None:
        return None

    parsed_date: datetime = string_to_date(date)
    parsed_curr_date: datetime= string_to_date(current_date())
    return data.get(key).get(DATA_KEY) if parsed_date.date() == parsed_curr_date.date() else None

def call_api(url, body):
    headers = construct_headers()
    return requests.post(url=url, headers=headers, json=body).json()

def potd_stats():
    jsonFile = reading_json_from_cache()
    response_json = fetch_value_cached(POTD_STATS)
    if response_json == None:
        response_json = call_api(LEETCODE_URL, {"query": POTD_BODY})
        writing_json_to_cache(jsonFile, response_json,POTD_STATS)
    return response_json

def potd_detail():
    jsonFile = reading_json_from_cache()
    response_json = fetch_value_cached(POTD_DETAIL)
    if response_json == None:
        response_json = call_api(LEETCODE_URL, {"query": POTD_DETAIL_BODY})
        writing_json_to_cache(jsonFile, response_json, POTD_DETAIL)
    return response_json

def method_signature(title=None):
    if title == None:
        return potd_method_signature()
    return any_method_signature(title)

def any_method_signature(title):
    formattedBody = replacing_placeholders(POTD_QUESTION_BODY,title)
    response_json = call_api(LEETCODE_URL, {"query": formattedBody})
    return response_json

def potd_method_signature():
    response_json = fetch_value_cached(POTD_QUESTION)
    if response_json == None:
        response_json_stats = potd_stats()
        jsonFile = reading_json_from_cache()
        questionTitlePOTD = [response_json_stats['data']['activeDailyCodingChallengeQuestion']['question']['titleSlug']]
        formattedBody = replacing_placeholders(POTD_QUESTION_BODY,questionTitlePOTD)
        
        response_json = call_api(LEETCODE_URL, {"query": formattedBody})
        writing_json_to_cache(jsonFile, response_json, POTD_QUESTION)
        
    return response_json