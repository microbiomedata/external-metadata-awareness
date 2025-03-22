import pprint
from typing import List, Optional

import click
import requests
import xmltodict


@click.command()
@click.option(
    '--biosample-accession',
    multiple=True,
    help="NCBI BioSamples to fetch, by alphanumeric accession, like SAMN37862744.",
    default=[
        'SAMN37862742',
        'SAMN37862743',
        'SAMN37862744',
    ]
)
def main(biosample_accession: List[str]):
    """
    Fetch and display BioSample information from NCBI using accession IDs.

    This script uses NCBI's eFetch service to retrieve XML formatted BioSample data
    for given accession IDs, converts it to a Python dictionary, and pretty-prints it.

    Example:
        python script.py -a SAMN37862744 -a SAMN37862743
    """
    xml_data = fetch_biosample_xml(biosample_accession)
    if xml_data:
        biosample_dict = convert_xml_to_dict(xml_data)
        pprint.pprint(biosample_dict)
    else:
        print("Failed to fetch data")


def fetch_biosample_xml(accessions: List[str]) -> Optional[str]:
    """
    Fetch BioSample XML data for given accession IDs from NCBI.

    Args:
        accessions (List[str]): List of BioSample accession IDs.

    Returns:
        Optional[str]: XML string of BioSample data if request is successful, None otherwise.
    """
    url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
    params = {
        'db': 'biosample',
        'id': ','.join(accessions),
        'rettype': 'xml',  # Optional: 'api_key': 'YOUR_API_KEY'
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.text
    else:
        return None


def convert_xml_to_dict(xml_data: str) -> Optional[dict]:
    """
    Convert XML data to a Python dictionary.

    Args:
        xml_data (str): XML string to be converted.

    Returns:
        Optional[dict]: Python dictionary representation of the XML data, None if conversion fails.
    """
    try:
        data_dict = xmltodict.parse(xml_data)
        return data_dict
    except Exception as e:
        print(f"Error parsing XML: {e}")
        return None


if __name__ == '__main__':
    main()
