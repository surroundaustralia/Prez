from typing import Dict, List, Tuple, Union

from httpx import AsyncClient
from httpx import Response as httpxResponse
from rdflib import Graph
import asyncio
from connegp import RDF_MEDIATYPES

from config import *


async def sparql_query(query: str, prez: str) -> Tuple[bool, Union[List, Dict]]:
    """Executes a SPARQL SELECT query for a single SPARQL endpoint"""
    creds = {
        "endpoint": "",
        "username": "",
        "password": ""
    }
    if prez == "VocPrez":
        creds["endpoint"] = VOCPREZ_SPARQL_ENDPOINT
        creds["username"] = VOCPREZ_SPARQL_USERNAME
        creds["password"] = VOCPREZ_SPARQL_PASSWORD
    elif prez == "SpacePrez":
        creds["endpoint"] = SPACEPREZ_SPARQL_ENDPOINT
        creds["username"] = SPACEPREZ_SPARQL_USERNAME
        creds["password"] = SPACEPREZ_SPARQL_PASSWORD
    else:
        raise Exception("Invalid prez specified in sparql_query call. Available options are: 'VocPrez', 'SpacePrez'.")
    async with AsyncClient() as client:
        response: httpxResponse = await client.post(
            creds["endpoint"],
            data=query,
            headers={
                "Accept": "application/json",
                "Content-Type": "application/sparql-query",
            },
            auth=(creds["username"], creds["password"]),
            timeout=15.0,
        )
    if 200 <= response.status_code < 300:
        return True, response.json()["results"]["bindings"]
    else:
        return False, {
            "code": response.status_code,
            "message": response.text,
            "prez": prez,
        }


async def sparql_query_multiple(
    query: str, prezs: List[str] = ENABLED_PREZS
) -> Tuple[List, List]:
    """Executes a SPARQL SELECT query for (potentially) multiple SPARQL endpoints

    If prezs arg is omitted, queries all available SPARQL endpoints.
    """
    results = await asyncio.gather(*[sparql_query(query, prez) for prez in prezs])
    succeeded_results = []
    failed_results = []
    for result in results:
        if result[0]:
            succeeded_results += result[1]
        else:
            failed_results += result[1]
    return succeeded_results, failed_results


async def sparql_construct(query: str, prez: str):
    """Returns an rdflib Graph from a CONSTRUCT query for a single SPARQL endpoint"""
    creds = {
        "endpoint": "",
        "username": "",
        "password": ""
    }
    if prez == "VocPrez":
        creds["endpoint"] = VOCPREZ_SPARQL_ENDPOINT
        creds["username"] = VOCPREZ_SPARQL_USERNAME
        creds["password"] = VOCPREZ_SPARQL_PASSWORD
    elif prez == "SpacePrez":
        creds["endpoint"] = SPACEPREZ_SPARQL_ENDPOINT
        creds["username"] = SPACEPREZ_SPARQL_USERNAME
        creds["password"] = SPACEPREZ_SPARQL_PASSWORD
    else:
        raise Exception("Invalid prez specified in sparql_query call. Available options are: 'VocPrez', 'SpacePrez'.")
    async with AsyncClient() as client:
        response: httpxResponse = await client.post(
            creds["endpoint"],
            data=query,
            headers={
                "Accept": "text/turtle",
                "Content-Type": "application/sparql-query",
            },
            auth=(creds["username"], creds["password"]),
            timeout=15.0,
        )
    if 200 <= response.status_code < 300:
        return True, Graph().parse(data=response.text)
    else:
        return False, {
            "code": response.status_code,
            "message": response.text,
            "prez": prez,
        }


async def sparql_endpoint_query(
    query: str, prez: str, accept: str
) -> Tuple[bool, Union[Dict, str]]:
    """Queries a SPARQL query on a single endpoint for some Accept mediatype"""
    creds = {
        "endpoint": "",
        "username": "",
        "password": ""
    }
    if prez == "VocPrez":
        creds["endpoint"] = VOCPREZ_SPARQL_ENDPOINT
        creds["username"] = VOCPREZ_SPARQL_USERNAME
        creds["password"] = VOCPREZ_SPARQL_PASSWORD
    elif prez == "SpacePrez":
        creds["endpoint"] = SPACEPREZ_SPARQL_ENDPOINT
        creds["username"] = SPACEPREZ_SPARQL_USERNAME
        creds["password"] = SPACEPREZ_SPARQL_PASSWORD
    else:
        raise Exception("Invalid prez specified in sparql_query call. Available options are: 'VocPrez', 'SpacePrez'.")
    async with AsyncClient() as client:
        response: httpxResponse = await client.post(
            creds["endpoint"],
            data=query,
            headers={
                "Accept": f"{accept}",
                "Content-Type": "application/sparql-query",
            },
            auth=(creds["username"], creds["password"]),
            timeout=15.0,
        )
    if 200 <= response.status_code < 300:
        if accept in ["application/sparql-results+json", "application/json"]:
            return True, response.json()
        else:
            return True, response.text
    else:
        return False, {
            "code": response.status_code,
            "message": response.text,
            "prez": prez,
        }


async def sparql_endpoint_query_multiple(
    query: str, accept: str = "application/sparql-results+json"
) -> Tuple[Union[str, Dict], List]:
    """Queries a SPARQL query on multiple endpoints for some Accept mediatype"""
    results = await asyncio.gather(
        *[sparql_endpoint_query(query, prez, accept) for prez in ENABLED_PREZS]
    )
    succeeded_results = Graph() if accept in RDF_MEDIATYPES else {}
    failed_results = []
    for result in results:
        if result[0]:
            if accept in RDF_MEDIATYPES:
                succeeded_results += Graph().parse(result[1], format=accept)
            else:  # JSON for now (need to cater for CSV & TSV)
                if len(succeeded_results.keys()) == 0:
                    succeeded_results = result[1]
                else:
                    succeeded_results["results"]["bindings"] += result[1]["results"][
                        "bindings"
                    ]
        else:
            failed_results += result[1]
    if accept in RDF_MEDIATYPES:
        return succeeded_results.serialize(format=accept), failed_results
    else:
        return succeeded_results, failed_results
