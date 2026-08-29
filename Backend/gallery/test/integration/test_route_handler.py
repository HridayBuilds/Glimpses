import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

import boto3
from moto import mock_aws

from routeHandler import lambda_handler


class _FakeLambdaContext:
    function_name = "gallery"
    memory_limit_in_mb = 256
    invoked_function_arn = "arn:aws:lambda:ap-south-1:000000000000:function:gallery"
    aws_request_id = "test-request-id"


def _api_event(http_method, path, body=None, claims=None, path_parameters=None, query_string_parameters=None):
    return {
        "resource": path,
        "path": path,
        "httpMethod": http_method,
        "headers": {"Content-Type": "application/json"},
        "multiValueHeaders": {},
        "queryStringParameters": query_string_parameters,
        "multiValueQueryStringParameters": None,
        "pathParameters": path_parameters,
        "stageVariables": None,
        "requestContext": {
            "authorizer": {"claims": claims or {}},
            "resourcePath": path,
            "httpMethod": http_method,
            "path": path,
            "stage": "test",
        },
        "body": json.dumps(body) if body is not None else None,
        "isBase64Encoded": False,
    }


def _create_photos_table(dynamodb):
    dynamodb.create_table(
        TableName=os.environ["PHOTOS_TABLE_NAME"],
        KeySchema=[{"AttributeName": "photoID", "KeyType": "HASH"}],
        AttributeDefinitions=[
            {"AttributeName": "photoID", "AttributeType": "S"},
            {"AttributeName": "eventID", "AttributeType": "S"},
            {"AttributeName": "uploadedAtFilename", "AttributeType": "S"},
        ],
        GlobalSecondaryIndexes=[
            {
                "IndexName": "eventID-uploadedAtFilename-index",
                "KeySchema": [
                    {"AttributeName": "eventID", "KeyType": "HASH"},
                    {"AttributeName": "uploadedAtFilename", "KeyType": "RANGE"},
                ],
                "Projection": {"ProjectionType": "ALL"},
            }
        ],
        BillingMode="PAY_PER_REQUEST",
    )


def _create_events_table(dynamodb):
    dynamodb.create_table(
        TableName=os.environ["EVENTS_TABLE_NAME"],
        KeySchema=[{"AttributeName": "eventID", "KeyType": "HASH"}],
        AttributeDefinitions=[{"AttributeName": "eventID", "AttributeType": "S"}],
        BillingMode="PAY_PER_REQUEST",
    )


def _create_event_attendees_table(dynamodb):
    dynamodb.create_table(
        TableName=os.environ["EVENT_ATTENDEES_TABLE_NAME"],
        KeySchema=[
            {"AttributeName": "userID", "KeyType": "HASH"},
            {"AttributeName": "eventID", "KeyType": "RANGE"},
        ],
        AttributeDefinitions=[
            {"AttributeName": "userID", "AttributeType": "S"},
            {"AttributeName": "eventID", "AttributeType": "S"},
        ],
        BillingMode="PAY_PER_REQUEST",
    )


def _put_photo(dynamodb, **overrides):
    item = {
        "photoID": "p1",
        "eventID": "evt_1",
        "uploaderID": "user_1",
        "uploaderDisplayName": "Arjun",
        "filename": "img.jpg",
        "uploadedAt": "2026-08-15T10:00:00Z",
        "uploadedAtFilename": "2026-08-15T10:00:00Z#img.jpg",
        "sizeBytes": 1234,
        "s3Key": "photos/event/evt_1/p1.jpg",
        "thumbnailKey": "thumbnails/event/evt_1/p1.jpg",
    }
    item.update(overrides)
    dynamodb.Table(os.environ["PHOTOS_TABLE_NAME"]).put_item(Item=item)
    return item


def _put_event(dynamodb, **overrides):
    item = {"eventID": "evt_1", "organizerID": "user_9", "status": "ACTIVE"}
    item.update(overrides)
    dynamodb.Table(os.environ["EVENTS_TABLE_NAME"]).put_item(Item=item)
    return item


@mock_aws
def test_list_photos_returns_newest_first_and_cursor_paginates():
    dynamodb = boto3.resource("dynamodb", region_name="ap-south-1")
    _create_photos_table(dynamodb)
    _create_events_table(dynamodb)
    _create_event_attendees_table(dynamodb)
    _put_photo(dynamodb, photoID="p1", uploadedAt="2026-08-15T10:00:00Z", uploadedAtFilename="2026-08-15T10:00:00Z#a.jpg")
    _put_photo(dynamodb, photoID="p2", uploadedAt="2026-08-16T10:00:00Z", uploadedAtFilename="2026-08-16T10:00:00Z#b.jpg")

    response = lambda_handler(
        _api_event("GET", "/events/evt_1/photos", claims={"sub": "user_1"}, path_parameters={"event_id": "evt_1"}),
        _FakeLambdaContext(),
    )

    assert response["statusCode"] == 200
    body = json.loads(response["body"])
    assert [photo["photoID"] for photo in body["photos"]] == ["p2", "p1"]


@mock_aws
def test_list_photos_mine_true_resolves_via_matched_photo_ids():
    dynamodb = boto3.resource("dynamodb", region_name="ap-south-1")
    _create_photos_table(dynamodb)
    _create_events_table(dynamodb)
    _create_event_attendees_table(dynamodb)
    _put_photo(dynamodb, photoID="p1")
    _put_photo(dynamodb, photoID="p2", uploadedAtFilename="2026-08-16T10:00:00Z#b.jpg")
    dynamodb.Table(os.environ["EVENT_ATTENDEES_TABLE_NAME"]).put_item(
        Item={"userID": "user_2", "eventID": "evt_1", "status": "ATTENDEE", "matchedPhotoIDs": {"p1"}}
    )

    response = lambda_handler(
        _api_event(
            "GET",
            "/events/evt_1/photos",
            claims={"sub": "user_2"},
            path_parameters={"event_id": "evt_1"},
            query_string_parameters={"mine": "true"},
        ),
        _FakeLambdaContext(),
    )

    body = json.loads(response["body"])
    assert [photo["photoID"] for photo in body["photos"]] == ["p1"]


@mock_aws
def test_get_photo_returns_photo_url_and_thumbnail_url():
    dynamodb = boto3.resource("dynamodb", region_name="ap-south-1")
    _create_photos_table(dynamodb)
    _create_events_table(dynamodb)
    _create_event_attendees_table(dynamodb)
    _put_photo(dynamodb)

    response = lambda_handler(
        _api_event(
            "GET", "/events/evt_1/photos/p1", claims={"sub": "user_1"}, path_parameters={"event_id": "evt_1", "photo_id": "p1"}
        ),
        _FakeLambdaContext(),
    )

    body = json.loads(response["body"])
    assert body["photoUrl"].startswith(f"https://{os.environ['CLOUDFRONT_DOMAIN']}/photos/event/evt_1/p1.jpg?")
    assert body["thumbnailUrl"].startswith(f"https://{os.environ['CLOUDFRONT_DOMAIN']}/thumbnails/event/evt_1/p1.jpg?")
    assert "Signature=" in body["photoUrl"]
    assert "Key-Pair-Id=" in body["photoUrl"]


@mock_aws
def test_download_urls_mints_presigned_gets():
    dynamodb = boto3.resource("dynamodb", region_name="ap-south-1")
    _create_photos_table(dynamodb)
    _create_events_table(dynamodb)
    _create_event_attendees_table(dynamodb)
    _put_photo(dynamodb)
    s3 = boto3.client("s3", region_name="ap-south-1")
    s3.create_bucket(Bucket=os.environ["PHOTOS_BUCKET"], CreateBucketConfiguration={"LocationConstraint": "ap-south-1"})

    response = lambda_handler(
        _api_event(
            "POST",
            "/events/evt_1/photos/download-urls",
            body={"photoIDs": ["p1"]},
            claims={"sub": "user_1"},
            path_parameters={"event_id": "evt_1"},
        ),
        _FakeLambdaContext(),
    )

    body = json.loads(response["body"])
    assert body["downloadUrls"][0]["photoID"] == "p1"
    assert "p1.jpg" in body["downloadUrls"][0]["downloadUrl"]


@mock_aws
def test_delete_photo_by_uploader_invokes_cascade_delete_once_configured(monkeypatch):
    dynamodb = boto3.resource("dynamodb", region_name="ap-south-1")
    _create_photos_table(dynamodb)
    _create_events_table(dynamodb)
    _create_event_attendees_table(dynamodb)
    _put_photo(dynamodb, uploaderID="user_1")
    _put_event(dynamodb)

    response = lambda_handler(
        _api_event(
            "DELETE", "/events/evt_1/photos/p1", claims={"sub": "user_1"}, path_parameters={"event_id": "evt_1", "photo_id": "p1"}
        ),
        _FakeLambdaContext(),
    )

    assert response["statusCode"] == 200
    assert json.loads(response["body"]) == {"deleted": True}


@mock_aws
def test_delete_photo_rejects_when_event_archived():
    dynamodb = boto3.resource("dynamodb", region_name="ap-south-1")
    _create_photos_table(dynamodb)
    _create_events_table(dynamodb)
    _create_event_attendees_table(dynamodb)
    _put_photo(dynamodb, uploaderID="user_1")
    _put_event(dynamodb, organizerID="user_1", status="ARCHIVED")

    try:
        lambda_handler(
            _api_event(
                "DELETE", "/events/evt_1/photos/p1", claims={"sub": "user_1"}, path_parameters={"event_id": "evt_1", "photo_id": "p1"}
            ),
            _FakeLambdaContext(),
        )
        assert False, "expected ValueError"
    except ValueError:
        pass


@mock_aws
def test_delete_photo_by_organizer_when_not_uploader():
    dynamodb = boto3.resource("dynamodb", region_name="ap-south-1")
    _create_photos_table(dynamodb)
    _create_events_table(dynamodb)
    _create_event_attendees_table(dynamodb)
    _put_photo(dynamodb, uploaderID="user_1")
    _put_event(dynamodb, organizerID="user_9")

    response = lambda_handler(
        _api_event(
            "DELETE", "/events/evt_1/photos/p1", claims={"sub": "user_9"}, path_parameters={"event_id": "evt_1", "photo_id": "p1"}
        ),
        _FakeLambdaContext(),
    )

    assert response["statusCode"] == 200
    assert json.loads(response["body"]) == {"deleted": True}


@mock_aws
def test_delete_photo_rejects_non_uploader_non_organizer():
    dynamodb = boto3.resource("dynamodb", region_name="ap-south-1")
    _create_photos_table(dynamodb)
    _create_events_table(dynamodb)
    _create_event_attendees_table(dynamodb)
    _put_photo(dynamodb, uploaderID="user_1")
    _put_event(dynamodb, organizerID="user_9")

    try:
        lambda_handler(
            _api_event(
                "DELETE",
                "/events/evt_1/photos/p1",
                claims={"sub": "someone_else"},
                path_parameters={"event_id": "evt_1", "photo_id": "p1"},
            ),
            _FakeLambdaContext(),
        )
        assert False, "expected ValueError"
    except ValueError:
        pass


@mock_aws
def test_bulk_delete_drops_unauthorized_photos_from_batch():
    dynamodb = boto3.resource("dynamodb", region_name="ap-south-1")
    _create_photos_table(dynamodb)
    _create_events_table(dynamodb)
    _create_event_attendees_table(dynamodb)
    _put_photo(dynamodb, photoID="p1", uploaderID="user_1")
    _put_photo(dynamodb, photoID="p2", uploaderID="someone_else", uploadedAtFilename="2026-08-16T10:00:00Z#b.jpg")
    _put_event(dynamodb, organizerID="user_9")

    response = lambda_handler(
        _api_event(
            "POST",
            "/events/evt_1/photos/bulk-delete",
            body={"photoIDs": ["p1", "p2"]},
            claims={"sub": "user_1"},
            path_parameters={"event_id": "evt_1"},
        ),
        _FakeLambdaContext(),
    )

    assert response["statusCode"] == 200
    assert json.loads(response["body"]) == {"deletedPhotoIDs": ["p1"]}
