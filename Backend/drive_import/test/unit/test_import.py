import json
import sys
from pathlib import Path
from unittest.mock import Mock

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'src'))
from Converter.drive_link import parse_folder_link
from DAO import dao, drive
from Manager import manager


def payload(**changes):
    return dict(eventID='event', userID='user', jobId='job', folderID='folder', resourceKey='folder-key',
                uploadedAt='now', uploaderDisplayName='Meera', uploaderEmail='meera@example.com',
                page=0, pageToken='', downloadedCount=0, downloadFailedCount=0,
                totalCount=0, skippedCount=0, skippedFolders=0, **changes)


@pytest.mark.parametrize('url', [
    'http://drive.google.com/drive/folders/a', 'https://evil.com/drive/folders/a',
    'https://drive.google.com.evil.com/drive/folders/a', 'https://drive.google.com/file/d/a/view',
    'https://user@drive.google.com/drive/folders/a', 'https://drive.google.com:444/drive/folders/a',
    'https://drive.google.com/drive/folders/a?resourcekey=bad%0Akey', None,
])
def test_rejects_invalid_or_nonfolder_links(url):
    with pytest.raises(ValueError):
        parse_folder_link(url)


def test_folder_link_with_resource_key():
    assert parse_folder_link('https://drive.google.com/drive/u/0/folders/abc_1?resourcekey=0-key&usp=sharing') == ('abc_1', '0-key')


def test_start_authorizes_and_has_stable_request_id(monkeypatch):
    monkeypatch.setattr(manager, '_authorize', Mock())
    start = Mock()
    monkeypatch.setattr(dao, 'start_execution', start)
    body = {'folderUrl': 'https://drive.google.com/drive/folders/folder', 'requestId': '11111111-1111-4111-8111-111111111111'}
    first = manager.start_import('event', 'user', body)
    assert manager.start_import('event', 'user', body) == first
    assert manager.start_import('event', 'other', body) != first
    assert start.call_args[0][1]['userID'] == 'other'


@pytest.mark.parametrize('status', ['PENDING', 'BLOCKED', None])
def test_nonadmitted_users_cannot_import(monkeypatch, status):
    def get(table, key):
        if table == 'EVENTS_TABLE_NAME':
            return {'status': 'ACTIVE', 'organizerID': 'owner', 'contributionPolicy': 'ATTENDEES_CAN_ADD'}
        return {'status': status} if status else None
    monkeypatch.setattr(dao, 'get_item', get)
    with pytest.raises(PermissionError):
        manager._authorize('event', 'guest')


def test_flat_listing_skips_folders_shortcuts_junk_and_nonphotos(monkeypatch):
    monkeypatch.setattr(manager, '_authorize', Mock())
    listing = Mock(return_value={'nextPageToken': 'next-page', 'files': [
        {'id': '1', 'name': 'photo.jpg', 'mimeType': 'image/jpeg', 'resourceKey': 'file-key'},
        {'id': '2', 'name': 'nested', 'mimeType': manager.FOLDER},
        {'id': '3', 'name': 'shortcut', 'mimeType': 'application/vnd.google-apps.shortcut'},
        {'id': '4', 'name': 'Thumbs.db', 'mimeType': 'image/jpeg'},
        {'id': '5', 'name': 'photos.zip', 'mimeType': 'application/zip'},
    ]})
    monkeypatch.setattr(drive, 'list_page', listing)
    write = Mock()
    monkeypatch.setattr(dao, 'put_json', write)
    monkeypatch.setattr(dao, 'update_job', Mock())
    result = manager.list_files(payload())
    assert result['pageToken'] == 'next-page'
    assert result['skippedFolders'] == 1
    assert result['skippedCount'] == 3
    assert result['totalCount'] == 1
    item = write.call_args[0][1][0]
    assert item['resourceKey'] == 'folder-key'
    assert item['fileResourceKey'] == 'file-key'
    assert listing.call_count == 1  # no recursive folder listing


def test_download_streams_and_carries_identity(monkeypatch):
    monkeypatch.setattr(manager, '_authorize', Mock())
    response = Mock(headers={'Content-Length': '3'})
    response.iter_content.return_value = iter([b'ab', b'c'])
    context_manager = Mock()
    context_manager.__enter__ = Mock(return_value=response)
    context_manager.__exit__ = Mock(return_value=False)
    download = Mock(return_value=context_manager)
    monkeypatch.setattr(drive, 'download', download)
    upload = Mock(side_effect=lambda key, chunks, *args: b''.join(chunks))
    monkeypatch.setattr(dao, 'upload_chunks', upload)
    result = manager.download_file(payload(id='photo', name='photo.jpg', fileResourceKey='file-key'), None)
    assert result['status'] == 'SUCCEEDED'
    assert result['rawKey'].endswith('/drive/raw/photo')
    assert download.call_args[0] == ('photo', 'folder/folder-key,photo/file-key')
    assert upload.call_args[0][3] == 3


def test_access_revoked_is_individual_failure(monkeypatch):
    monkeypatch.setattr(manager, '_authorize', Mock())
    monkeypatch.setattr(drive, 'download', Mock(side_effect=drive.DriveAccessError(drive.PUBLIC_MESSAGE)))
    result = manager.download_file(payload(id='photo', name='photo.jpg'), None)
    assert result['status'] == 'FAILED'
    assert 'Anyone with the link' in result['reason']


def test_collect_keeps_successes_and_counts_task_failures(monkeypatch):
    files = {
        'manifest': {'ResultFiles': {'SUCCEEDED': [{'Key': 'ok'}], 'FAILED': [{'Key': 'bad'}]}},
        'ok': [{'Output': json.dumps({'status': 'SUCCEEDED', 'filename': 'one.jpg'})},
               {'Output': json.dumps({'status': 'FAILED', 'filename': 'two.jpg', 'reason': 'Private'})}],
        'bad': [{'Input': json.dumps({'name': 'three.jpg'}), 'Error': 'States.Timeout'}],
    }
    monkeypatch.setattr(dao, 'get_json', files.__getitem__)
    monkeypatch.setattr(dao, 'put_json', Mock())
    update = Mock()
    monkeypatch.setattr(dao, 'update_job', update)
    result = manager.collect_page(payload(downloadResultsKey='manifest'))
    assert result['downloadedCount'] == 1
    assert result['downloadFailedCount'] == 2
    assert result['page'] == 1
    manager.collect_page(payload(downloadResultsKey='manifest'))
    assert update.call_args_list[0] == update.call_args_list[1]


def test_prepare_emits_existing_ingestion_contract(monkeypatch):
    monkeypatch.setattr(manager, '_authorize', Mock())
    monkeypatch.setattr(dao, 'get_json', lambda key: [{'rawKey': key, 'filename': 'photo.jpg'}])
    monkeypatch.setattr(dao, 'update_job', Mock())
    written = []
    monkeypatch.setattr(dao, 'upload_chunks', lambda key, chunks, *args, **kwargs: written.append(json.loads(b''.join(chunks))))
    data = payload()
    data.update(page=2, downloadedCount=2)
    result = manager.prepare_manifest(data, None)
    assert len(written[0]) == 2
    assert result['jobId'] == 'job'
    assert result['stagedManifestKey'].endswith('/drive/staged-manifest.json')
    assert 'original.zip' not in result['stagedManifestKey']


def test_empty_folder_has_clear_error(monkeypatch):
    monkeypatch.setattr(manager, '_authorize', Mock())
    monkeypatch.setattr(dao, 'update_job', Mock())
    with pytest.raises(ValueError, match='No supported photos'):
        manager.prepare_manifest(payload(), None)


def test_final_counts_include_download_failures_and_duplicates(monkeypatch):
    monkeypatch.setattr(dao, 'get_item', lambda *args: {'totalCount': 10, 'downloadFailedCount': 2})
    monkeypatch.setattr(dao, 'update_job', Mock())
    result = manager.combine_results({'jobId': 'job', 'succeededCount': 5, 'failedCount': 1})
    assert result['failedCount'] == 3
    assert result['duplicateCount'] == 2


def test_multipart_aborted_on_short_transfer(monkeypatch):
    monkeypatch.setenv('PHOTOS_BUCKET', 'photos')
    s3 = Mock()
    s3.create_multipart_upload.return_value = {'UploadId': 'upload'}
    monkeypatch.setattr(dao.boto3, 'client', lambda service: s3)
    with pytest.raises(IOError, match='incomplete'):
        dao.upload_chunks('key', iter([b'abc']), expected_size=5)
    s3.abort_multipart_upload.assert_called_once()
    s3.complete_multipart_upload.assert_not_called()


def test_multipart_aborted_before_lambda_timeout(monkeypatch):
    monkeypatch.setenv('PHOTOS_BUCKET', 'photos')
    s3 = Mock()
    s3.create_multipart_upload.return_value = {'UploadId': 'upload'}
    monkeypatch.setattr(dao.boto3, 'client', lambda service: s3)
    context = Mock()
    context.get_remaining_time_in_millis.return_value = 1000
    with pytest.raises(TimeoutError):
        dao.upload_chunks('key', iter([b'abc']), context)
    s3.abort_multipart_upload.assert_called_once()


def test_google_throttle_is_retryable_without_exposing_api_key(monkeypatch):
    monkeypatch.setattr(drive, '_api_key', lambda: 'secret')
    response = Mock(status_code=403, is_redirect=False)
    response.json.return_value = {'error': {'errors': [{'reason': 'rateLimitExceeded'}]}}
    monkeypatch.setattr(drive.requests, 'get', lambda *args, **kwargs: response)
    with pytest.raises(drive.DriveTransientError, match='temporarily limited'):
        drive._request('file')
    response.close.assert_called_once()


def test_redirect_rejects_arbitrary_hosts(monkeypatch):
    monkeypatch.setattr(drive, '_api_key', lambda: 'secret')
    response = Mock(status_code=302, is_redirect=True, headers={'Location': 'https://evil.example/file'})
    get = Mock(return_value=response)
    monkeypatch.setattr(drive.requests, 'get', get)
    with pytest.raises(drive.DriveAccessError, match='unsupported'):
        drive._request('file')
    assert get.call_count == 1


def test_backend_receives_private_folder_error_through_job(monkeypatch):
    from decimal import Decimal
    monkeypatch.setattr(dao, 'get_item', lambda *args: {'failedCount': Decimal(0), 'downloadFailedCount': Decimal(2)})
    update = Mock()
    monkeypatch.setattr(dao, 'update_job', update)
    manager.fail({'jobId': 'job', 'driveError': {'Error': 'DriveAccessError', 'Cause': json.dumps({'errorMessage': drive.PUBLIC_MESSAGE})}})
    values = update.call_args[0][1]
    assert values['status'] == 'FAILED'
    assert values['failedCount'] == 2
    assert values['errorMessage'] == drive.PUBLIC_MESSAGE
    json.dumps(values)


def test_multipart_upload_roundtrip(monkeypatch):
    import boto3
    from moto import mock_aws
    monkeypatch.setenv('AWS_DEFAULT_REGION', 'us-east-1')
    monkeypatch.setenv('PHOTOS_BUCKET', 'drive-staging-test')
    with mock_aws():
        s3 = boto3.client('s3')
        s3.create_bucket(Bucket='drive-staging-test')
        data = b'x' * (dao.PART_BYTES + 17)
        assert dao.upload_chunks('uploads/drive/test', (data[i:i+1024*1024] for i in range(0, len(data), 1024*1024)), expected_size=len(data)) == len(data)
        assert s3.get_object(Bucket='drive-staging-test', Key='uploads/drive/test')['Body'].read() == data
        assert not s3.list_multipart_uploads(Bucket='drive-staging-test').get('Uploads')


def test_api_returns_accepted_job_and_rejects_bad_links(monkeypatch):
    from routeHandler import lambda_handler
    class Context:
        function_name = 'drive_import'
        memory_limit_in_mb = 512
        invoked_function_arn = 'arn:aws:lambda:us-east-1:000000000000:function:drive_import'
        aws_request_id = 'request'
    monkeypatch.setattr(manager, '_authorize', Mock())
    start = Mock()
    monkeypatch.setattr(dao, 'start_execution', start)
    event = {
        'resource': '/events/event/drive-import', 'path': '/events/event/drive-import', 'httpMethod': 'POST',
        'headers': {'Content-Type': 'application/json'}, 'multiValueHeaders': {}, 'queryStringParameters': None,
        'requestContext': {'authorizer': {'claims': {'sub': 'user'}}, 'stage': 'test'},
        'isBase64Encoded': False,
        'body': json.dumps({'folderUrl': 'https://drive.google.com/drive/folders/folder', 'requestId': '11111111-1111-4111-8111-111111111111'}),
    }
    result = lambda_handler(event, Context())
    assert result['statusCode'] == 202
    assert 'jobId' in json.loads(result['body'])
    assert start.call_args[0][1]['userID'] == 'user'
    event['body'] = json.dumps({'folderUrl': 'https://evil.example/', 'requestId': 'x'})
    assert lambda_handler(event, Context())['statusCode'] == 400
    assert start.call_count == 1
