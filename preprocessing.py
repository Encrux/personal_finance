import csv
import datetime

import ollama
import pandas as pd
from matplotlib import pyplot as plt
import tqdm

columns = [
    "date",
    "value_date",
    "status",
    "payer",
    "payee",
    "purpose",
    "type",
    "IBAN",
    "amount",
    "creditor_id",
    "mandate_reference",
    "customer_reference"
]

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

prompt_template = ("I'm trying to categorize my payments. Can you help me with this one? \n"
                   "For a lot of payments, I just have a company name and a purpose. "
                   "It would be great if you could also infer the category just from the company name.\n"
                   "Please just type the category you think fits best. \n"
                   "Please do not repeat the full list categories in your response. \n"
                   "the possible categories are [categories]. \n"
                   "Alright, here's the payment info: \n"
                   "Payee: [payee], Purpose: [purpose] \nCategory: ")


def plot_top_n(n: int):
    data = _open_csv('account.csv')
    unique = data['payee'].unique()  # all unique payment recipients of this account
    # summarizes the above for loop in one dictionary
    recipient_dict = {recipient: abs(data[data['payee'] == recipient]['amount']).sum() for recipient
                      in unique}
    # sort the dictionary by the amount of money received
    recipient_dict = dict(sorted(recipient_dict.items(), key=lambda item: item[1], reverse=True))
    # create bar chart with the first 15 recipients, put the rest into 'Sonstige'
    top_n = dict(list(recipient_dict.items())[:n])
    top_n['Sonstige'] = sum(list(recipient_dict.values())[n:])
    print(top_n)
    # create plot
    plt.bar(top_n.keys(), top_n.values())
    plt.xticks(rotation=75)
    plt.tick_params(axis='x', labelsize=5)
    plt.show()


def _open_csv(file: str):
    """
    :param file: string
    :return: pandas dataframe
    """
    print("Opening file")
    with open(file) as f:
        #use utf-8
        dialect = csv.Sniffer().sniff(f.read(1024))
        f.seek(0)
        reader = csv.DictReader(f, dialect=dialect)
        data = pd.DataFrame(reader)

    data.columns = columns
    data['amount'] = data['amount'].str.replace('.', '')
    data['amount'] = data['amount'].str.replace(',', '.').astype(float)

    data['date'] = pd.to_datetime(data['date'], format='%d.%m.%y')
    data['value_date'] = pd.to_datetime(data['value_date'], format='%d.%m.%y')
    return data


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
    prompt = (prompt_template
              .replace("[payee]", payee)
              .replace("[purpose]", purpose)
              .replace("[categories]", str(categories).replace('[', '').replace(']', '')).replace("'", ''))
    response = ollama.generate(model="llama2", prompt=prompt)

    cat = extract_category(response['response'], categories)

    #print input and response
    # print(f"Input: {payee}, {purpose}")
    # print(f"Response: {response['response']}")
    # print(f"Category: {cat}")
    # print("====================================")

    return cat


def categorize_all_payments(start_date: datetime, end_date: datetime):
    data = _open_csv('account.csv')
    data = data[data['date'] > start_date]
    data = data[data['date'] <= end_date]

    progress_bar = tqdm.tqdm(total=len(data))

    categories_dict = {c: [] for c in categories}
    for i, row in data.iterrows():
        progress_bar.update(1)
        cat = categorize_payment(row['payee'], row['purpose'])
        categories_dict[cat].append(row)

    print("Done categorizing payments")
    return categories_dict


if __name__ == '__main__':
    spending = categorize_all_payments(
        start_date=datetime.datetime(2024, 1, 1),
        end_date=datetime.datetime.now(),
    )
    for category, payments in spending.items():
        print(f"{category}: {len(payments)}")
        print(f"Total amount: {sum([p['amount'] for p in payments])}")
