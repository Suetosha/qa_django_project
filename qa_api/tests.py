import uuid
import pytest
from django.urls import reverse
from rest_framework.test import APIClient

@pytest.fixture
def api_client():
    return APIClient()


@pytest.mark.django_db
def test_create_question(api_client):
    data = {"text": "Какой ваш любимый язык программирования?"}
    url = reverse("qa_api:question-list-create")
    response = api_client.post(url, data, format="json")
    assert response.status_code == 201
    assert response.data["success"] is True
    assert response.data["data"]["text"] == data["text"]


@pytest.mark.django_db
def test_get_question_list(api_client):
    api_client.post(reverse("qa_api:question-list-create"), {"text": "Вопрос 1"}, format="json")
    api_client.post(reverse("qa_api:question-list-create"), {"text": "Вопрос 2"}, format="json")

    url = reverse("qa_api:question-list-create")
    response = api_client.get(url)
    assert response.status_code == 200
    assert response.data["success"] is True


@pytest.mark.django_db
def test_get_question_detail(api_client):
    question_resp = api_client.post(
        reverse("qa_api:question-list-create"),
        {"text": "Вопрос для теста"},
        format="json"
    )
    question_id = question_resp.data["data"]["id"]

    url = reverse("qa_api:question-detail", args=[question_id])
    response = api_client.get(url)
    assert response.status_code == 200
    assert response.data["success"] is True
    assert response.data["data"]["id"] == question_id


@pytest.mark.django_db
def test_delete_question(api_client):
    question_resp = api_client.post(
        reverse("qa_api:question-list-create"),
        {"text": "Вопрос для удаления"},
        format="json"
    )
    question_id = question_resp.data["data"]["id"]

    url = reverse("qa_api:question-detail", args=[question_id])
    response = api_client.delete(url)
    assert response.status_code in (200, 204)
    assert response.data["success"] is True

    get_resp = api_client.get(url)
    assert get_resp.status_code == 404


@pytest.mark.django_db
def test_create_answer(api_client):
    question_resp = api_client.post(
        reverse("qa_api:question-list-create"),
        {"text": "Вопрос для ответа"},
        format="json"
    )
    question_id = question_resp.data["data"]["id"]

    url = reverse("qa_api:answer-create", args=[question_id])
    data = {"text": "Это ответ на вопрос", "user_id": str(uuid.uuid4())}
    response = api_client.post(url, data, format="json")
    assert response.status_code == 201
    assert response.data["success"] is True
    assert response.data["data"]["text"] == data["text"]
    assert response.data["data"]["question"] == question_id


@pytest.mark.django_db
def test_get_answer_detail(api_client):
    question_resp = api_client.post(
        reverse("qa_api:question-list-create"),
        {"text": "Вопрос для ответа"},
        format="json"
    )
    question_id = question_resp.data["data"]["id"]

    answer_data = {"text": "Ответ для теста", "user_id": str(uuid.uuid4())}
    answer_resp = api_client.post(
        reverse("qa_api:answer-create",
                args=[question_id]),
        answer_data,
        format="json"
    )
    answer_id = answer_resp.data["data"]["id"]

    url = reverse("qa_api:answer-detail", args=[answer_id])
    response = api_client.get(url)
    assert response.status_code == 200
    assert response.data["success"] is True
    assert response.data["data"]["id"] == answer_id


@pytest.mark.django_db
def test_delete_answer(api_client):
    question_resp = api_client.post(
        reverse("qa_api:question-list-create"),
        {"text": "Вопрос для ответа"},
        format="json"
    )
    question_id = question_resp.data["data"]["id"]

    answer_data = {"text": "Ответ для удаления", "user_id": str(uuid.uuid4())}
    answer_resp = api_client.post(
        reverse("qa_api:answer-create",
                args=[question_id]),
        answer_data,
        format="json"
    )
    answer_id = answer_resp.data["data"]["id"]

    url = reverse("qa_api:answer-detail", args=[answer_id])
    response = api_client.delete(url)
    assert response.status_code in (200, 204)
    assert response.data["success"] is True

    get_resp = api_client.get(url)
    assert get_resp.status_code == 404
