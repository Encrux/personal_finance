import ollama
from bs4 import BeautifulSoup
import requests
import urllib.parse

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

categories = [
    "insurance",
    "groceries",
    "salary",
    "eating out/snacks",
    "rent/miete",
    "clothes",
    "amazon",
    "studierendenwerk karlsruhe",
    "phone",
    "transport",
    "sports",
    "other",
]


def google_search(query):
    query = urllib.parse.quote_plus(query)
    url = f"https://google.com/search?q={query}"
    result = requests.get(url, headers=headers, cookies=cookies)
    soup = BeautifulSoup(result.text, 'html.parser')
    return soup


def extract_category(response: str, categories: list):
    """
    algorithm to extract the category from the response. Case insenstiive
    :param categories: list of categories
    :param response: llm response
    :return: exact category
    """
    for cat in categories:
        if cat.lower() in response.lower():
            return cat

    return "other"


def categorize_payment(payee: str, purpose: str):
    """
    :param payee: string
    :param purpose: string
    :return: string
    """

    additional_info = get_additional_info(payee)

    prompt = ((prompt_template
               .replace("[payee]", payee)
               .replace("[purpose]", purpose)
               .replace("[categories]", str(categories).replace('[', '').replace(']', '')).replace("'", ''))
              .replace("[additional_info]", additional_info)
              )

    response = ollama.generate(model="llama2", prompt=prompt)

    cat = extract_category(response['response'], categories)

    return cat


def get_additional_info(param):
    response = google_search(param)
    summary = ollama.generate(model="llama2", prompt=response.text + f"\n in one simple sentence, {param} is")[
        "response"]
    return summary


if __name__ == '__main__':
    payee = "Drillisch Online GmbH                                                 Wilhelm-Rontgen-Strase 1-5, 63477 Maintal"
    purpose = "VISA KARTENZAHLUNG"

    print("googling...")
    response = google_search(payee)
    print("summarizing...")
    summary = ollama.generate(model="llama2", prompt=response.text + f"\n in one simple sentence, {payee} is")[
        "response"]
    print(summary)
    print("categorizing...")
    category = categorize_payment(payee, purpose)
    print(f"Category: {category}")
