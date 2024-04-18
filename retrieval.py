import ollama
from bs4 import BeautifulSoup
import requests
import urllib.parse

from preprocessing import categories, extract_category

prompt_template = ("I'm trying to categorize my payments. Can you help me with this one? \n"
                   "For a lot of payments, I just have a company name and a purpose. "
                   "It would be great if you could also infer the category just from the company name.\n"
                   "Please just type the category you think fits best. \n"
                   "Please do not repeat the full list categories in your response. \n"
                   "the possible categories are [categories]. \n"
                   "Alright, here's the payment info: \n"
                   "Payee: [payee], Purpose: [purpose] \n "
                   "Here's some additional info about the payee: [additional_info] \n")

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; rv:125.0) Gecko/20100101 Firefox/125.0"
}

cookies = {"CONSENT": "YES+cb.20220419-08-p0.cs+FX+111"}


def google_search(query):
    query = urllib.parse.quote_plus(query)
    url = f"https://google.com/search?q={query}"
    result = requests.get(url, headers=headers, cookies=cookies)
    soup = BeautifulSoup(result.text, 'html.parser')
    return soup


def categorize_payment(payee: str, purpose: str, additional_info: str):
    """
    :param payee: string
    :param purpose: string
    :return: string
    """
    prompt = ((prompt_template
               .replace("[payee]", payee)
               .replace("[purpose]", purpose)
               .replace("[categories]", str(categories).replace('[', '').replace(']', '')).replace("'", ''))
              .replace("[additional_info]", additional_info))

    response = ollama.generate(model="llama2", prompt=prompt)

    cat = extract_category(response['response'], categories)

    #print input and response
    # print(f"Input: {payee}, {purpose}")
    # print(f"Response: {response['response']}")
    # print(f"Category: {cat}")
    # print("====================================")

    return cat


if __name__ == '__main__':
    payee = "SPARKASSE KARLSRUHE"
    purpose = "VISA Debitkartenumsatz"

    print("googling...")
    response = google_search(payee)
    print("summarizing...")
    summary = ollama.generate(model="llama2", prompt=response.text + f"\n in one simple sentence, {payee} is")["response"]
    print(summary)
    print("categorizing...")
    category = categorize_payment(payee, purpose, summary)
    print(f"Category: {category}")
