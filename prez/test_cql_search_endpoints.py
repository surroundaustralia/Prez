from fastapi.testclient import TestClient
from prez.app import app
import pytest


client = TestClient(app)


def test_search_page():
    r = client.get("/search")
    assert r.status_code == 200
    assert "<h2>Feature Search</h2>" in r.text


def test_home_items_default_default():
    r = client.get("/items")
    assert r.status_code == 200
    assert '<div class="member">' in r.text


# unsure if /items is required to have a geoJSON format for OAI
# see http://docs.opengeospatial.org/is/17-069r3/17-069r3.html#_requirements_class_geojson
def test_home_items_default_geojson():
    r = client.get("/items?_mediatype=application/geo+json")
    assert r.status_code == 200
    assert '"rel":"self"' in r.text


def test_home_cqlsearch_default_default():
    r = client.get('/items?filter=title LIKE "catch"')
    assert r.status_code == 200
    assert '<div class="member">' in r.text


@pytest.fixture(scope="module")
def a_dataset_link():
    # get link for first dataset
    r = client.get("/datasets?_profile=mem&_mediatype=application/json")
    return r.json()["members"][0]["link"]


def test_dataset_items_default_default(a_dataset_link):
    r = client.get(f"{a_dataset_link}/items")
    assert r.status_code == 200
    assert '<div class="member">' in r.text


# unsure if /items is required to have a geoJSON format for OAI
# see http://docs.opengeospatial.org/is/17-069r3/17-069r3.html#_requirements_class_geojson
def test_dataset_items_default_geojson(a_dataset_link):
    r = client.get(f"{a_dataset_link}/items?_mediatype=application/geo+json")
    assert r.status_code == 200
    assert '"rel":"self"' in r.text

def test_dataset_cqlsearch_default_default(a_dataset_link):
    r = client.get(f'{a_dataset_link}/items?filter=title LIKE "catch"')
    assert r.status_code == 200
    assert '<div class="member">' in r.text


@pytest.fixture(scope="module")
def an_fc_link(a_dataset_link):
    # get link for first collection
    r2 = client.get(
        f"{a_dataset_link}/collections?_profile=mem&_mediatype=application/json"
    )
    return r2.json()["members"][0]["link"]

def test_fc_cqlsearch_default_default(an_fc_link):
    r = client.get(f'{an_fc_link}/items?filter=title LIKE "catch"')
    assert r.status_code == 200
    assert '<div class="member">' in r.text
