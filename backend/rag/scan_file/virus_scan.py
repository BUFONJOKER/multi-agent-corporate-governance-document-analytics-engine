import cloudmersive_virus_api_client
from cloudmersive_virus_api_client.rest import ApiException
from config import CLOUDMERSIVE_VIRUS_API


def scan_file(file_path: str) -> dict:
    '''
    Scans a file for viruses using the Cloudmersive Virus Scan API and returns the scan result.
    '''
    api_instance = cloudmersive_virus_api_client.ScanApi()


    api_instance.api_client.configuration.api_key = {}
    api_instance.api_client.configuration.api_key['Apikey'] = CLOUDMERSIVE_VIRUS_API

    try:
        # Scan a file for viruses
        api_response = api_instance.scan_file(file_path)
        return api_response
    except ApiException as e:
        return {"error":"Exception when calling ScanApi->scan_file: %s\n" % e}