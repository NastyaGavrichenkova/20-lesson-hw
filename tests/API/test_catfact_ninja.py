import json

import allure

import jsonschema
import requests
from curlify import to_curl
from allure_commons.types import AttachmentType

from tests.utils import load_schema


def catfact_ninja_api(method, url, **kwargs):
    base_url = 'https://catfact.ninja'
    new_url = base_url + url
    method = method.upper()
    with ((allure.step(f'{method} {url}'))):
        with requests.sessions.Session() as session:
            response = session.request(method=method, url=new_url, **kwargs)
            message = to_curl(response.request)
            allure.attach(body=message.encode("utf8"),
                          name="Curl",
                          attachment_type=AttachmentType.TEXT,
                          extension='txt')
            try:
                allure.attach(body=json.dumps(response.json(), indent=4).encode("utf8"),
                              name="Response Json",
                              attachment_type=AttachmentType.JSON,
                              extension='json')
            except:
                allure.attach(body=response.content,
                              name="Response text",
                              attachment_type=AttachmentType.TEXT,
                              extension='txt')
    return response


def test_get_breeds():
    page = 1

    response = catfact_ninja_api(
        'get',
        url='/breeds',
        params={"page": page}
    )

    assert response.status_code == 200
    assert response.json()["current_page"] == 1


def test_breeds_schema_validation():
    schema = load_schema('catfact', 'get_breeds.json')

    response = catfact_ninja_api(
        'get',
        url='/breeds'
    )

    assert response.status_code == 200
    jsonschema.validate(response.json(), schema)


def test_get_random_fact():
    schema = load_schema('catfact', 'get_randon_fact.json')

    response = catfact_ninja_api(
        'get',
        url='/fact'
    )

    assert response.status_code == 200
    jsonschema.validate(response.json(), schema)
