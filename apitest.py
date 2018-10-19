import argparse
from craigslist import CraigslistForSale

parser = argparse.ArgumentParser()
parser.add_argument("-c", "--category", help="category to search. electronics, computers, music", default="ela")    #default is electronics
parser.add_argument("-p", "--price", help="max price to show", default="100")
parser.add_argument("-q", "--query", help="specific item query", default="")
args = parser.parse_args()


def map_cat(cat):
    if cat == "computers":
        return "sya"
    elif cat == "electronics":
        return "ela"
    elif cat == "music":
        return "msa"


location = "worcester"
category = map_cat(args.category)
price = args.price
query = args.query

cl_fs = CraigslistForSale(site=location, area=None, category=category, filters={
    'query': query, 'has_image': True, 'max_price': price, 'posted_today': True})

for result in cl_fs.get_results(sort_by='newest', geotagged=True):
    print(result)
