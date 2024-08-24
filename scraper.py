#   Author:
#                   Matt Tucker
#
#   Date:
#                   16Aug2024
#
#   Description:
#                   Build CSV files containing information about papers on ArXiv
#######################################################################################################################
from math_config import dstart, dend, allcats, cat, math_branches, math_connections, math_science_connections
import arxivscraper
import pandas as pd

def dataList(type, lookup, start=dstart, end=dend):
    # Look up wide range of maths within 'narrow' window of time
    if type == 'category':
        scraper = arxivscraper.Scraper(category=lookup, date_from=start, date_until=end)
    # Look up 'narrow' scope of math in wide window of time
    elif type == 'keyword':
        scraper = arxivscraper.Scraper(category=cat, date_from=start, date_until=end, filters={'abstract': [lookup]})

    output = scraper.scrape()

    # Ensure 'id' is treated as a string
    for entry in output:
        entry['id'] = str(entry['id'])

    cols = ('id', 'title', 'categories', 'abstract', 'doi', 'created', 'updated', 'authors')

    df = pd.DataFrame(output, columns=cols)

    return df

def main():
    df = dataList('category', cat)
    df.to_csv('arxivList.csv', index=False)

if __name__ == '__main__':
    main()


