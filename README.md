## Classify Expenses from a DKB-Banking account .csv-file

The idea of this project is using LLMs to classify the expenses from my banking account into pre-defined classes using in-context learning capabilities of LLMs.

The project uses ollama (with a llama2-variant) to preprocess the unstructured csv-file into a classified document

## Predefined Categories:
```python
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
```

## retrieval.py

The idea behind this script is to essentially google the name of the company of the payment to make a more educated guess about the class of the payment.
