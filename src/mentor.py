import requests
import pandas as pd
from io import StringIO

MENTOR_DF = None
MENTOR_DOMAIN_ACRONYMS = {
    "machine learning": ["ml", "machinelearning", "machine-learning"],
    "deep learning": ["dl", "deeplearning", "deep-learning"],
    "computer vision": ["cv", "computervision", "computer-vision"],
    "natural language processing": ["nlp", "naturallanguageprocessing", "natural-language-processing"],
    "app development": ["app dev", "appdev", "app-dev", "appdevelopment", "app-development"],
    "web development": ["web dev", "webdev", "web-dev", "webdevelopment", "web-development"],
    "linux": ["linux"],
    "android kernel development": ["android-kernel-dev", "android-kernel-development", "android-kernel", "android kernel"],
    "automation and webscraping": ["automation", "webscraping", "web-scraping", "automation-webscraping", ],
    "robotics": ["robotics", "robots"],
    "distributed systems":["distributed-systems", "distributedsystems"],
}
MENTOR_CAMPUS = set()
MENTOR_NAMES = set()


def readDataFrame():
    global MENTOR_DF
    # mentor_df_link = "https://raw.githubusercontent.com/ArvindAROO/Choco-private/master/data/mentors.csv?token=AH5RA36D6H6YS6WTPLU3FTDA6ZSWM"
    # response = requests.get(mentor_df_link)
    # mentor_df_content = StringIO(response.content.decode())
    MENTOR_DF = pd.read_csv("data/mentors.csv")


def initialiseMentorFilters():
    global MENTOR_DOMAIN_ACRONYMS
    global MENTOR_CAMPUS
    global MENTOR_NAMES

    for row in MENTOR_DF.iterrows():
        row = dict(row[1])
        domain = row["DOMAIN"].lower()
        name = row["NAME"]
        campus = row["CAMPUS"].lower()
        domains = set([c.lower().strip() for c in domain.split(',')])
        for domain_name in domains:
            found = False
            for existing_domain in MENTOR_DOMAIN_ACRONYMS:
                if domain_name == existing_domain or domain_name in MENTOR_DOMAIN_ACRONYMS[existing_domain]:
                    found = True
            if not found:
                MENTOR_DOMAIN_ACRONYMS[domain_name] = list()

        MENTOR_NAMES.add(name)
        MENTOR_CAMPUS.add(campus)


def getMentorFilterType(queries):
    query_data = list()
    for query in queries:
        query = query.lower()
        query_type = None
        if query in MENTOR_CAMPUS:
            query_type = "CAMPUS"
        elif query in MENTOR_DOMAIN_ACRONYMS:
            query_type = "DOMAIN"
        else:
            for domain_name in MENTOR_DOMAIN_ACRONYMS:
                if query in MENTOR_DOMAIN_ACRONYMS[domain_name]:
                    query_type = "DOMAIN"
                    break
        if query_type == None:
            query_type = "NAME"
        query_data.append({query: query_type})
    return query_data


def replaceAcronymWithKeyword(acronym):
    acronym = acronym.lower()
    for domain_name in MENTOR_DOMAIN_ACRONYMS:
        if acronym in MENTOR_DOMAIN_ACRONYMS[domain_name] or acronym == domain_name:
            return domain_name
    return acronym


def getMentorResultsByNameOrCampus(search_query, query_type):
    result = list()
    if query_type in ["NAME", "CAMPUS"]:
        search_query = search_query.lower()
        for row in MENTOR_DF.iterrows():
            row = dict(row[1])
            search_query_field_value = row[query_type].lower()
            if search_query in search_query_field_value:
                result.append(row)
    return result


def getMentorResultsByDomain(search_domain):
    result = list()
    search_domain = replaceAcronymWithKeyword(search_domain)
    for row in MENTOR_DF.iterrows():
        row = dict(row[1])
        domains = [c.lower().strip() for c in row["DOMAIN"].split(',')]
        if search_domain in domains:
            result.append(row)
    return result


def getMentorResultsByFilters(query_data):
    result = list()
    for row in MENTOR_DF.iterrows():
        flag = True
        row = dict(row[1])
        for filter in query_data:
            query, query_type = list(filter.items())[0]
            query_search_field_value = row[query_type].lower()
            if query_type == 'NAME' and query in query_search_field_value:
                result.append(row)
                return result
            if query_type == "DOMAIN":
                query = replaceAcronymWithKeyword(query)
                domains = [c.lower().strip() for c in row["DOMAIN"].split(',')]
                query_search_field_value = domains
            if query not in query_search_field_value:
                flag = False
        if flag:
            result.append(row)
    return result


def getMentorResults(queries):
    query_data = getMentorFilterType(queries)
    num_queries = len(query_data)
    if num_queries == 1:
        query, query_type = list(query_data[0].items())[0]
        if query_type == "DOMAIN":
            result = getMentorResultsByDomain(query)
        else:
            result = getMentorResultsByNameOrCampus(query, query_type)
    else:
        result = getMentorResultsByFilters(query_data)
    return result
