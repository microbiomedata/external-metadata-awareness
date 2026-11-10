import pprint
import time
from typing import List, Optional

import click
import requests
import xmltodict

# NCBI allows 3 E-utilities requests per second without an API key
# (https://www.ncbi.nlm.nih.gov/books/NBK25497/), and this script makes one per accession plus one.
REQUEST_INTERVAL_SECONDS = 0.34


@click.command()
@click.option(
    '--biosample-accession',
    multiple=True,
    help="NCBI BioSamples to fetch, by accession, like SAMN37862744 or SAMEA10021844.",
    default=[
        'SAMN37862742',
        'SAMN37862743',
        'SAMN37862744',
    ]
)
def main(biosample_accession: List[str]):
    """
    Fetch and display BioSample information from NCBI using accession IDs.

    This script looks up each accession's UID with NCBI's eSearch, uses eFetch to retrieve
    XML formatted BioSample data for those UIDs, converts it to a Python dictionary,
    and pretty-prints it.

    Example:
        python script.py -a SAMN37862744 -a SAMN37862743
    """
    uids = [resolve_biosample_uid(accession) for accession in biosample_accession]
    xml_data = fetch_biosample_xml(uids)
    if xml_data:
        biosample_dict = convert_xml_to_dict(xml_data)
        pprint.pprint(biosample_dict)
    else:
        print("Failed to fetch data")


def resolve_biosample_uid(accession: str) -> str:
    """
    Look up the NCBI internal UID for a BioSample accession with eSearch.

    eFetch treats the digits of an accession passed as `id` as a UID, so for SAMD and
    SAMEA accessions it returns a different BioSample without an error. SAMN accessions
    only work because their UID happens to equal their digits.

    Raises:
        click.ClickException: if the accession matches no BioSample or more than one.
    """
    time.sleep(REQUEST_INTERVAL_SECONDS)
    response = requests.get(
        "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi",
        params={'db': 'biosample', 'term': f"{accession}[accn]", 'retmode': 'json'},
    )
    response.raise_for_status()
    uids = response.json()["esearchresult"]["idlist"]
    if len(uids) != 1:
        raise click.ClickException(f"{accession} matched {len(uids)} BioSamples in NCBI, expected 1: {uids}")
    return uids[0]


def fetch_biosample_xml(uids: List[str]) -> Optional[str]:
    """
    Fetch BioSample XML data for given NCBI UIDs (see resolve_biosample_uid).

    Args:
        uids (List[str]): List of BioSample UIDs, not accessions.

    Returns:
        Optional[str]: XML string of BioSample data if request is successful, None otherwise.
    """
    url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
    params = {
        'db': 'biosample',
        'id': ','.join(uids),
        'rettype': 'xml',  # Optional: 'api_key': 'YOUR_API_KEY'
    }
    time.sleep(REQUEST_INTERVAL_SECONDS)
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
