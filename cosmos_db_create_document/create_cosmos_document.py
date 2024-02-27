import os
import requests
import json
import urllib.parse
import datetime
import base64

from azure.identity import DefaultAzureCredential

# cosmos
COSMOS_ACCOUNT_NAME = os.environ.get("COSMOS_ACCOUNT_NAME")
DATABASE_NAME = os.environ.get("DATABASE_NAME")
COLLECTION_ID = os.environ.get("COLLECTION_ID")
COSMOS_URI = f"https://{COSMOS_ACCOUNT_NAME}.documents.azure.com"
CREATE_BODY = os.environ.get("CREATE_BODY")  # json in base64


def get_cosmos_aad_authorization(
    cosmos_account_name: str,
    token_version: str = "1.0",
):
    """Get a valid Authorization value used in the Header for Azure Cosmos DB REST API using EntraID credentials.
        DefaultAzureCredential uses the following environment variables automatically: AZURE_CLIENT_ID, AZURE_CLIENT_SECRET, AZURE_TENANT_ID
    Args:
        cosmos_account_name (_type_): Azure Cosmos Account Name.
        token_version (str, optional): The token version used in the key 'ver' for the authorization string. Defaults to "1.0".

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
        headers["x-ms-documentdb-partitionkey"] = f'["{partition_key}"]'

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


def create_cosmos_document(
    headers: dict,
    cosmos_account_name: str,
    database_name: str,
    collection_id: str,
    body: dict,
):
    """Create a document in a Cosmos Collection

    Args:
        headers (dict): Valid header used in Cosmos REST API.
        cosmos_account_name (str): Cosmos account name in which the document is to be created.
        database_name (str): Database name in which the document is to be created.
        collection_id (str): Collection ID (name) in which the document is to be created.
        body: The body used in the REST API to create the document.

    Returns:
        list: All the Documents in a collection (with all the properties)
    """
    print(create_cosmos_document.__name__)

    url = f"https://{cosmos_account_name}.documents.azure.com:443/dbs/{database_name}/colls/{collection_id}/docs"
    print(f"Creating document in {url}")

    response = invoke_web_request(url=url, method="POST", headers=headers, body=body)
    return response.json()


def main():
    decoded_json = base64.b64decode(CREATE_BODY).decode("utf-8")
    create_body = json.loads(decoded_json)
    partition_key = create_body["partitionKey"]
    authorization = get_cosmos_aad_authorization(
        cosmos_account_name=COSMOS_ACCOUNT_NAME
    )
    headers = get_cosmos_headers(
        authorization=authorization, partition_key=partition_key, create_document=True
    )
    response = create_cosmos_document(
        headers=headers,
        cosmos_account_name=COSMOS_ACCOUNT_NAME,
        database_name=DATABASE_NAME,
        collection_id=COLLECTION_ID,
        body=create_body,
    )

    print(json.dumps(response, indent=4))
    print("OK: Script finished.")


## MAIN
if __name__ == "__main__":
    main()
