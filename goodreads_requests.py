import requests
import resource

api_key = resource.api_key


def get_review_counts(isbns) -> list:
    """From Goodreads API doc:
    Get review statistics for books given a list of ISBNs. ISBNs can be specified as an array
    (e.g. isbns[]=0441172717&isbns[]=0141439602) or a single, comma-separated string (e.g. isbns=0441172717,0141439602).

    :param isbns: (list or str) isbn or list of isbns. In this case ','.join is used to create a string.
    :return (list) list of dictionaries where each dictionary represents the review counts answer per isbn
    """
    if isinstance(isbns, list):
        isbns = ','.join(isbns)
    res = requests.get("https://www.goodreads.com/book/review_counts.json",
                       params={"key": api_key, "isbns": isbns})
    return res.json()['books']


if __name__ == '__main__':
    print(get_review_counts("1"))
