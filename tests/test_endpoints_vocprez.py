import pytest
import re
from pathlib import Path
import shutil
import os
import sys
PREZ_DIR = Path("/Users/nick/Work/Prez/prez/")
sys.path.insert(0, str(PREZ_DIR.parent.absolute()))
from fastapi.testclient import TestClient


@pytest.fixture(scope="session")
def vp_test_client(request):
    print('\nDoing config setup')
    # preserve original config file
    shutil.copyfile(PREZ_DIR / "config.py", PREZ_DIR / "config.py.original")

    # alter config file contents
    with open(PREZ_DIR / "config.py", "rt") as f:
        config = f.read()
        config = config.replace("Default Prez", "Test Prez")
        config = config.replace("Default VocPrez", "Test VocPrez")
        config = config.replace('["VocPrez", "SpacePrez"]', '["VocPrez"]')
        config = config.replace('"VOCPREZ_SPARQL_ENDPOINT", ""', '"VOCPREZ_SPARQL_ENDPOINT", "http://localhost:3030/vocprez"')

    # write altered config contents to config.py
    with open(PREZ_DIR / "config.py", "w") as f:
        f.truncate(0)
        f.write(config)

    def teardown():
        print("\nDoing teardown")
        # remove altered config file
        os.unlink(PREZ_DIR / "config.py")

        # restore original file
        shutil.copyfile(PREZ_DIR / "config.py.original", PREZ_DIR / "config.py")
        os.unlink(PREZ_DIR / "config.py.original")

    request.addfinalizer(teardown)

    # must only import app after config.py has been altered above so config is retained
    from prez.app import app
    return TestClient(app)


@pytest.fixture(scope="module")
def a_vocab_id(vp_test_client):
    r = vp_test_client.get("/vocab")
    return re.search(r'<a href="/vocab/(.*)">', r.text)[1]


@pytest.fixture(scope="module")
def a_vocab_id_and_a_concept_id(vp_test_client, a_vocab_id):
    # get the first concept endpoint
    r2 = vp_test_client.get(f"/vocab/{a_vocab_id}?_mediatype=text/html")
    patt = f'<a href="http://testserver/vocab/{a_vocab_id}/(.*)">'
    return (a_vocab_id, re.search(patt, r2.text)[1])


def test_home_default_default(vp_test_client):
    r = vp_test_client.get("/")
    assert "<h1>Test VocPrez</h1>" in r.text


def test_home_default_turtle(vp_test_client):
    r = vp_test_client.get("/?_profile=dcat&_mediatype=text/turtle")
    assert "a dcat:Dataset" in r.text


def test_home_alt_html(vp_test_client):
    r = vp_test_client.get("/?_profile=alt")
    assert "<h1>Alternate Profiles</h1>" in r.text


def test_home_alt_turtle(vp_test_client):
    r = vp_test_client.get("/?_profile=alt&_mediatype=text/turtle")
    assert "a rdfs:Resource" in r.text


def test_vocabs_default_default(vp_test_client):
    r = vp_test_client.get("/vocab")
    assert "Concept Scheme list" in r.text


# def test_vocabs_default_turtle(config_setup):
#     r = config_setup.get("/vocabs?_mediatype=text/turtle")
#     assert "a dcat:Dataset" in r.text


def test_vocabs_dd_json(vp_test_client):
    r = vp_test_client.get("/vocab?_profile=dd&_mediatype=application/json")
    assert '[{"uri":"' in r.text


def test_vocab_default_default(vp_test_client, a_vocab_id):
    r2 = vp_test_client.get(f"/vocab/{a_vocab_id}?_mediatype=text/html")  # TODO: work out why HTML has to be specified here?
    assert f'<li class="breadcrumb"><a href="http://testserver/vocab/{a_vocab_id}">' in r2.text


def test_vocab_default_turtle(vp_test_client, a_vocab_id):
    r2 = vp_test_client.get(f"/vocab/{a_vocab_id}?_mediatype=text/turtle")
    assert 'a skos:ConceptScheme' in r2.text


def test_vocab_alt_default(vp_test_client, a_vocab_id):
    r2 = vp_test_client.get(f"/vocab/{a_vocab_id}?_profile=alt")
    assert 'Alternate Profiles' in r2.text


def test_vocab_alt_turtle(vp_test_client, a_vocab_id):
    r2 = vp_test_client.get(f"/vocab/{a_vocab_id}?_profile=alt&_mediatype=text/turtle")
    assert 'a rdfs:Resource' in r2.text


def test_vocab_dd_json(vp_test_client, a_vocab_id):
    r2 = vp_test_client.get(f"/vocab/{a_vocab_id}?_profile=dd&_mediatype=application/json")
    assert '[{"uri":"http' in r2.text


def test_concept_default_default(vp_test_client, a_vocab_id_and_a_concept_id):
    a_vocab_id, a_concept_id = a_vocab_id_and_a_concept_id

    # TODO: should not have to specify vocpub for default
    r3 = vp_test_client.get(f"/vocab/{a_vocab_id}/{a_concept_id}?_profile=vocpub&_mediatype=text/html")
    assert '<a href="http://www.w3.org/2004/02/skos/core#Concept" target="_blank" >' in r3.text


def test_concept_default_turtle(vp_test_client, a_vocab_id_and_a_concept_id):
    a_vocab_id, a_concept_id = a_vocab_id_and_a_concept_id

    r3 = vp_test_client.get(f"/vocab/{a_vocab_id}/{a_concept_id}?_profile=vocpub&_mediatype=text/turtle")
    assert 'a skos:Concept' in r3.text


def test_concept_alt_default(vp_test_client, a_vocab_id_and_a_concept_id):
    a_vocab_id, a_concept_id = a_vocab_id_and_a_concept_id

    r3 = vp_test_client.get(f"/vocab/{a_vocab_id}/{a_concept_id}?_profile=alt")
    assert '<h1>Alternate Profiles</h1>' in r3.text


# def test_concept_alt_turtle(config_setup, a_vocab_id_and_a_concept_id):
#     a_vocab_id, a_concept_id = a_vocab_id_and_a_concept_id
#
#     r3 = config_setup.get(f"/vocab/{a_vocab_id}/{a_concept_id}?_profile=alt&_mediatype=text/turtle")
#     assert '<h1>Alternate Profiles</h1>' in r3.text