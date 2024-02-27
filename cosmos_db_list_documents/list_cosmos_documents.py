import os
import requests
import json
import urllib.parse
import datetime

from azure.identity import DefaultAzureCredential

# cosmos
COSMOS_ACCOUNT_NAME = os.environ.get("COSMOS_ACCOUNT_NAME")
COSMOS_URI = f"https://{COSMOS_ACCOUNT_NAME}.documents.azure.com"
DATABASE_NAME = os.environ.get("DATABASE_NAME")
COLLECTION_ID = os.environ.get("COLLECTION_ID")
RECORDS_NUMBER = int(float(os.environ.get("RECORDS_NUMBER")))


def get_cosmos_aad_authorization(
    cosmos_account_name: str,
    token_version: str = "1.0",
):
    """Get a valid Authorization value used in the Header for Azure Cosmos DB REST API using EntraID credentials.
        DefaultAzureCredential uses the following environment variables automatically: AZURE_CLIENT_ID, AZURE_CLIENT_SECRET, AZURE_TENANT_ID
    Args:
        client_id (_type_): Client ID (app_id) for Entra ID Identity
        client_secret (_type_): App or Service Principal Key credential
        tenant_id (_type_): azure Tenant ID
        cosmos_account_name (_type_): _description_
        token_version (str, optional): _description_. Defaults to "1.0".

    Returns:
        string: Valid Authorization value used in Cosmos REST API Header
    """
    print(get_cosmos_aad_authorization.__name__)
    key_type = "aad"
    try:
        aad_credentials = DefaultAzureCredential()
        scope = f"https://{cosmos_account_name}.documents.azure.com/.default"
        signature = aad_credentials.get_token(scope)
    except Exception as e:
        print(f"Error: {e}")

    auth = f"type={key_type}&ver={token_version}&sig={signature.token}"
    encoded_authorization = urllib.parse.quote_plus(auth)
    return encoded_authorization


def get_cosmos_headers(
    authorization: str,
    partition_key: str = "",
    xms_version: str = "2018-12-31",
    create_document: bool = False,
):
    """Create a full valid Header for Cosmos REST API.
    Args:
        authorization (str): the value for the Authorization Header Key used in REST API.
        partition_key (str, optional):  The partition_key used in documents and in the x-ms-documentdb-partitionkey header key.
            Only used if create_document is True. Defaults to "".
        xms_version (str, optional): _x-ms-version Header Key. Defaults to "2018-12-31".
        create_document (bool, optional): If true x-ms-documentdb-partitionkey put this key and a partition_key in value in the header.
            Defaults to False.

    Returns:
        dict: A valid dictionary used in Cosmos REST API.
    """
    print(get_cosmos_headers.__name__)
    headers = {
        "Authorization": authorization,
        "x-ms-version": xms_version,
        "x-ms-date": datetime.datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT"),
        "x-ms-continuation": None,
    }
    if create_document is True:
        headers["x-ms-documentdb-partitionkey"] = f"[{partition_key}]"

    return headers


def invoke_web_request(
    url: str, method: str = "GET", headers: dict = None, body: dict = None
):
    """_summary_

    Args:
        url (str): Endpoint to call a REST API.
        method (str, optional): Method used in REST API. For now: GET or POST. Defaults to "GET".
        headers (dict, optional): A valid header used in Header REST API call. Defaults to None.
        body (dict, optional): A dictionary (json) used in the Body. Defaults to None.

    Raises:
        e: Method not suported
        e: HTTPError
        e: ConnectionError
        e: Timeout
        e: RequestException

    Returns:
        dict: Return the raw reponse for this web request.
    """
    print(invoke_web_request.__name__)
    if headers is None:
        headers = {}

    try:
        match method.upper():
            case "GET":
                print(f"Executing {method}")
                response = requests.get(url, headers=headers)
            case "POST":
                print(f"Executing {method}")
                body_json = json.dumps(body) if body is not None else None
                response = requests.post(url, headers=headers, data=body_json)
            case _:
                e = "This method is not supported:"
                print(f"{e} {method}")
                raise e

        response.raise_for_status()
        return response

    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error: {e}")
        raise e
    except requests.exceptions.ConnectionError as e:
        print(f"Connection Error: {e}")
        raise e
    except requests.exceptions.Timeout as e:
        print(f"Timeout Error: {e}")
        raise e
    except requests.exceptions.RequestException as e:
        print(f"Unknown Error: {e}")
        raise e


def get_cosmos_documents(
    headers: dict, cosmos_account_name: str, database_name: str, collection_id: str
):
    """Get all the documents from a Cosmos Collection

    Args:
        headers (dict): Valid header used in Cosmos REST API.
        cosmos_account_name (str): Cosmos account name to be queried
        database_name (str): Database name to be queried
        collection_id (str): Collection ID (name) to be queried

    Returns:
        list: All the Documents in a collection (with all the properties)
    """
    print(get_cosmos_documents.__name__)
    url = f"https://{cosmos_account_name}.documents.azure.com:443/dbs/{database_name}/colls/{collection_id}/docs"
    all_documents = []
    exe = True
    while exe is True:
        print(
            f"Getting the documents for the Cosmos:'{cosmos_account_name}' | Database: '{database_name}' | CollectionId: '{collection_id}'"
        )
        response = invoke_web_request(url=url, method="GET", headers=headers)
        all_documents.extend(response.json()["Documents"])
        continuation_token = response.headers.get("x-ms-continuation")
        # Add the continuation token if it exists
        headers["x-ms-continuation"] = continuation_token
        if continuation_token is None:
            exe = False
    return all_documents


def main():
    authorization = get_cosmos_aad_authorization(
        cosmos_account_name=COSMOS_ACCOUNT_NAME
    )
    headers = get_cosmos_headers(authorization=authorization)
    all_documents = get_cosmos_documents(
        headers=headers,
        cosmos_account_name=COSMOS_ACCOUNT_NAME,
        database_name=DATABASE_NAME,
        collection_id=COLLECTION_ID,
    )

    print(json.dumps(all_documents[-RECORDS_NUMBER:-1], indent=4))
    print("OK: Script finished.")


## MAIN
if __name__ == "__main__":
    main()
