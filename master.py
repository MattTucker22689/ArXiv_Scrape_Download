#   Author:
#                   Matt Tucker
#
#   Date:
#                   23Aug2024
#
#   Description:
#                   1)  Build CSV files containing information about papers on ArXiv
#                   2)  Download papers from ArXiv based on their ID numbers
#######################################################################################################################

from math_config import dstart, dend, allcats, cat, math_branches, math_connections, math_science_connections
import arxivscraper
import arxiv
import pandas as pd
import requests
import os

def dataList(type, lookup, start):
    end = str(start + 1) + '-01-01'
    start = str(start) + '-01-01'
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

def download_arxiv_paper(arxiv_id, output_dir='papers'):
    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Ensure arxiv_id is a string
    if pd.isna(arxiv_id):
        print(f"Invalid arXiv ID: {arxiv_id}")
        return

    arxiv_id = str(arxiv_id).strip()

    # Validate the arXiv ID format (e.g., 0704.0014)
    if not arxiv_id or not arxiv_id.replace('.', '').isdigit() or len(arxiv_id.split('.')[0]) < 4:
        print(f"Invalid arXiv ID format: {arxiv_id}")
        return

    # Search for the paper using Client
    client = arxiv.Client()
    search = arxiv.Search(id_list=[arxiv_id])
    try:
        paper = next(client.results(search))
    except StopIteration:
        print(f"No results found for arXiv ID: {arxiv_id}")
        return
    except arxiv.HTTPError as e:
        print(f"Failed to fetch paper for {arxiv_id}. HTTPError: {e}")
        return

    # Get the PDF URL
    pdf_url = paper.pdf_url

    # Download the PDF
    response = requests.get(pdf_url)
    if response.status_code == 200:
        # Generate a filename
        filename = f"{arxiv_id.replace(':', '_')}.pdf"
        filepath = os.path.join(output_dir, filename)

        # Save the PDF
        with open(filepath, 'wb') as f:
            f.write(response.content)
        print(f"Downloaded: {filename}")
    else:
        print(f"Failed to download {arxiv_id}")

def main():
    start = int(dstart)
    while start < int(dend):
        end = start + 1
        df = dataList('category', cat, start)
        df.to_csv('arxivList_' + str(start) + '-' + str(end) + '_.csv', index=False)
        start = end

    files_in_root = os.listdir()

    csv_files = [file for file in files_in_root if file.endswith('.csv')]
    for file in csv_files:
        df = pd.read_csv(file, dtype={'id': str})  # Ensure 'id' is read as string
        arxiv_ids = df.iloc[:, 0]

        for arxiv_id in arxiv_ids:
            download_arxiv_paper(arxiv_id)

if __name__ == '__main__':
    main()
