import pytest

import config
from cql_search import CQLSearch

# CQL_PROPS.clear()
CQL_PROPS = {
    "title": {
        "title": "Title",
        "description": "The title of a geo:Feature",
        "qname": "dcterms:title",
        "type": "string",
    },
    "count": {
        "title": "Test prop with integer type",
        "description": "",
        "qname": "a:count",
        "type": "integer",
    }
}


def test_prop_exists():
    cql = CQLSearch("", "", "")
    assert cql._check_prop_exists("title")


def test_prop_exists_negative():
    cql = CQLSearch("", "", "")
    assert not cql._check_prop_exists("test")


def test_check_type():
    cql = CQLSearch("", "", "")
    assert cql._check_type("title", '"something"')


def test_check_type_negative():
    cql = CQLSearch("", "", "")
    assert not cql._check_type("title", "5")


def test_parse_eq_ops():
    cql = CQLSearch("", "", "")
    f = cql._parse_eq_ops('title<>"something"')
    assert f == '?title != "something"'


def test_parse_eq_ops_negative():
    cql = CQLSearch("", "", "")
    f = cql._parse_eq_ops('title=<"something"')
    assert not f == '?title <= "something"'


def test_parse_between():
    cql = CQLSearch("", "", "")
    f = cql._parse_between('count BETWEEN 0 AND 5')
    assert f == '(?count >= 0 && ?count <= 5)'


# def test_parse_between_negative():
#     cql = CQLSearch("", "", "")
#     f = cql._parse_between('count=<"something"')
#     assert not f == '?count <= "something"'
