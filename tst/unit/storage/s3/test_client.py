from unittest import TestCase
from unittest.mock import MagicMock, patch
from datetime import datetime


def append_target_module(var_name: str) -> str:
    return f"src.storage.s3.client.{var_name}"


class TestS3Client(TestCase):
    def setUp(self):
        self.bucket_name = "test-bucket"
        
        with patch(append_target_module("_Session")) as mock_session_class:
            self.mock_session = mock_session_class.return_value
            self.mock_client = MagicMock()
            self.mock_session.client.return_value = self.mock_client
            
            from src.storage.s3.client import S3Client
            self.s3_client = S3Client(self.bucket_name)

    @patch(append_target_module("_logger"))
    def test_set_bucket(self, _logger: MagicMock):
        new_bucket = "new-awesome-bucket"
        self.s3_client.set_bucket(new_bucket)
        self.assertEqual(self.s3_client._bucket_name, new_bucket)
        _logger.warning.assert_called_once_with(
            f"changed bucket from '{self.bucket_name}' to '{new_bucket}'"
        )

    def test_list_file_names(self):
        mock_paginator = MagicMock()
        self.mock_client.get_paginator.return_value = mock_paginator
        
        mock_paginator.paginate.return_value = [
            {"Contents": [{"Key": "file1.csv"}, {"Key": "file2.csv"}]},
            {"Contents": [{"Key": "file3.csv"}]}
        ]

        result = list(self.s3_client.list_file_names(symbol="BTC"))
        
        self.assertEqual(result, ["file1.csv", "file2.csv", "file3.csv"])
        mock_paginator.paginate.assert_called_once_with(
            Bucket=self.bucket_name,
            Prefix="BTC/"
        )

    @patch(append_target_module("_logger"))
    def test_remove_file(self, _logger: MagicMock):
        file_to_remove = "old_data.csv"
        self.s3_client.remove_file(file_to_remove)
        
        self.mock_client.delete_object.assert_called_once_with(
            Bucket=self.bucket_name,
            Key=file_to_remove
        )
        _logger.warning.assert_called_once_with(
            "removed file 'old_data.csv' from bucket 'test-bucket'"
        )

    def test_download_file(self):
        file_name = "test.csv"
        mock_content = "col1,col2\nval1,val2"
        mock_date = datetime(2023, 1, 1)
        
        # Mock get_object response
        self.mock_client.get_object.return_value = {
            "Body": MagicMock(read=lambda: mock_content.encode("utf-8")),
            "LastModified": mock_date,
            "ContentLength": 100
        }
        
        # Mock get_object_tagging response
        self.mock_client.get_object_tagging.return_value = {
            "TagSet": [{"Key": "num_candles", "Value": "10"}]
        }

        downloaded_file = self.s3_client.download_file(file_name)

        self.assertEqual(downloaded_file.key, file_name)
        self.assertEqual(downloaded_file.content, mock_content)
        self.assertEqual(downloaded_file.tags["num_candles"], "10")
        self.assertEqual(downloaded_file.last_modified, mock_date)

    @patch(append_target_module("_logger"))
    def test_upload_file(self, _logger: MagicMock):
        mock_sequence = MagicMock()
        mock_candle = MagicMock()
        mock_candle.time = datetime(2023, 1, 1, 12, 0)
        
        mock_sequence.symbol = "ETH"
        mock_sequence.candle_type = "1m"
        mock_sequence.candles = [mock_candle, mock_candle]
        mock_sequence.to_csv.return_value = "csv_data"
        mock_sequence.num_candles = 2
        mock_sequence.num_gaps = 0
        mock_sequence.avg_gap_mins = 0.0

        expected_key = "ETH/1m/2023-01-01-2023-01-01.csv"
        
        returned_key = self.s3_client.upload_file(mock_sequence)

        self.assertEqual(returned_key, expected_key)
        self.mock_client.put_object.assert_called_once()
        
        args, kwargs = self.mock_client.put_object.call_args
        self.assertIn("num_candles=2", kwargs["Tagging"])
        self.assertIn("num_gaps=0", kwargs["Tagging"])
        _logger.warning.assert_called_once_with(
            "added file 'ETH/1m/2023-01-01-2023-01-01.csv' to bucket 'test-bucket'"
        )
