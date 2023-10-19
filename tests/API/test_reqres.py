import json

import allure

import jsonschema
import requests
from curlify import to_curl
from allure_commons.types import AttachmentType

from tests.utils import load_schema


def reqres_api(method, url, **kwargs):
    base_url = 'https://reqres.in'
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


def test_get_list_users():
    page = 2

    response = reqres_api(
        'get',
        url='/api/users',
        params={"page": page}
    )

    assert response.status_code == 200
    assert response.json()["page"] == 2


def test_get_single_existing_user():
    response = reqres_api(
        'get',
        url='/api/users/2'
    )

    assert response.status_code == 200
    assert response.json()["data"]["id"] == 2


def test_get_user_not_found():
    response = reqres_api(
        'get',
        url='/api/users/23'
    )

    assert response.status_code == 404


def test_get_user_schema_validation():
    schema = load_schema('reqres', 'get_users.json')

    response = reqres_api(
        'get',
        url='/api/users/2'
    )

    assert response.status_code == 200
    jsonschema.validate(response.json(), schema)


def test_add_new_user():
    response = reqres_api(
        'post',
        url='/api/users',
        json={
            "name": "morpheus",
            "job": "leader"
        }
    )

    assert response.status_code == 201
    assert response.json()["name"] == "morpheus"


def test_update_user():
    schema = load_schema('reqres', 'update_user.json')

    response = reqres_api(
        'put',
        url='/api/users/2',
        json={
            "name": "morpheus",
            "job": "zion resident"
        }
    )

    assert response.json()["job"] == 'zion resident'
    jsonschema.validate(response.json(), schema)


def test_delete_user():
    response = reqres_api(
        'delete',
        url='/api/users/2')

    assert response.status_code == 204


def test_successful_registration_schema_validation():
    schema = load_schema('reqres', 'registration_user.json')

    response = reqres_api(
        'post',
        url='/api/register',
        json={
            "email": "eve.holt@reqres.in",
            "password": "pistol"
        }
    )

    assert response.status_code == 200
    jsonschema.validate(response.json(), schema)


def test_successful_login_status_code():
    response = reqres_api(
        'get',
        url='/api/login',
        json={
            "email": "eve.holt@reqres.in",
            "password": "cityslicka"
        }
    )

    assert response.status_code == 200


def test_unsuccessful_login():
    response = reqres_api(
        'post',
        url='/api/login',
        json={
            "email": "peter@klaven"
        }
    )

    assert response.status_code == 400
    assert response.json()["error"] == "Missing password"
