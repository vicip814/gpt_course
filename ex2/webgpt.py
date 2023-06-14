from serpapi import GoogleSearch
import requests
import openai
import logging
import sys, os

openai.api_key = os.getenv("OPENAI_API_KEY")
serp_key = os.getenv('SERP_API_KEY')
headers = {'Cache-Control': 'no-cache', 'Content-Type': 'application/json'}
params = {'token': 'a01321e3-f570-4302-a16e-42a3e7f353a1'}

def scarpe_webpage(link):
    json_data = {
        'url': link,
        'elements': [{'selector': 'body'}],
    }
    response = requests.post('https://chrome.browserless.io/scrape', params=params, headers=headers, json=json_data)
    webpage_text = response.json()['data'][0]['results'][0]['text']
    #print(webpage_text)
    return webpage_text

def summarize_webpage(question, webpage_text):
  messages=[
        {"role": "system", "content": "You are an intelligent summarization engine. Extract and summarize the most relevant information from following text"},
        {"role": "user", "content":  webpage_text[0:2500]}]

  prompt = """You are an intelligent summarization engine. Extract and summarize the
  most relevant information from a body of text related to a question.

  Question: {}

  Body of text to extract and summarize information from:
  {}

  Relevant information:""".format(question, webpage_text[0:2500])
  completion = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages, temperature=0.8, max_tokens=800)
 # print(completion.choices[0].text)
  return completion.choices[0].message.content


def summarize_final_answer(question, summaries):
    messages=[
        {"role": "system", "content": "You are an intelligent summarization engine. Extract and summarize the most relevant information from following text"},
        {"role": "user", "content":  """    1. {}
            2. {}
            3. {}
            4. {}""".format(question, summaries[0], summaries[1], summaries[2], summaries[3]) }]
    prompt = """You are an intelligent summarization engine. Extract and summarize relevant information
    from the four points below to construct an answer to a question.

    Question: {}

    Relevant Information:
    1. {}
    2. {}
    3. {}
    4. {}""".format(question, summaries[0], summaries[1], summaries[2], summaries[3])
    completion = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages,  temperature=0.8, max_tokens=800)

    return completion.choices[0].message.content


def get_link(r):
    return r['link']

def get_search_results(question):
    search = GoogleSearch({
        "q": question,
        "api_key": serp_key,
        "logging": False
    })

    result = search.get_dict()
    return list(map(get_link, result['organic_results']))

def print_citations(links, summaries):
    print("Citations:")
    i = 0
    while i < 4:
        print("\n","[{}]".format(i+1), links[i],"\n", summaries[i], "\n")
        i += 1

def main():
    print("\nTell me about:\n")
    question = input()
    print("\n")
    sys.stdout = open(os.devnull, 'w') #disable print
    links = get_search_results(question)
    sys.stdout = sys.__stdout__ #enable print
    webpages = list(map(scarpe_webpage, links[:4]))
    summaries = []
    for x in webpages:
        summaries.append(summarize_webpage(question, x))
    final_summary =  summarize_final_answer(question, summaries)
    print("Here is the answer:", final_summary, "\n")
    print_citations(links, summaries)

if __name__ == "__main__":
    main()
