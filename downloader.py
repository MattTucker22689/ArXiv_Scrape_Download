#   Author:
#                   Matt Tucker
#
#   Date:
#                   19Aug2024
#
#   Description:
#                   Download papers from ArXiv based on their ID numbers
#######################################################################################################################
import arxiv
import pandas as pd
import requests
import os

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
    files_in_root = os.listdir()

    csv_files = [file for file in files_in_root if file.endswith('.csv')]
    for file in csv_files:
        df = pd.read_csv(file, dtype={'id': str})  # Ensure 'id' is read as string
        arxiv_ids = df.iloc[:, 0]

        for arxiv_id in arxiv_ids:
            download_arxiv_paper(arxiv_id)

if __name__ == '__main__':
    main()



