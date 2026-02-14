from typing import (
    Optional as _Optional,
    Iterator as _Iterator,
    List as _List,
    Dict as _Dict,
)
from datetime import (
    datetime as _datetime,
)
from boto3 import (
    Session as _Session,
)
from logging import (
    getLogger as _getLogger,
    basicConfig as _basicConfig,
    WARNING as _WARNING_LOG_LEVEL,
)
from src.defines.candle import (
    CandleTypeLiteral as _CandleTypeLiteral,
)
from src.defines.instrument import (
    SymbolLiteral as _SymbolLiteral,
)
from src.analyze.sequence import (
    Sequence as _Sequence,
)


_basicConfig(level=_WARNING_LOG_LEVEL)
_logger = _getLogger(__name__)


class _File:
    def __init__(
        self,
        key: str,
        content: str,
        tags: _Dict[str, str],
        modified_history: _List[_datetime],
        size_bytes: int,
    ) -> None:
        self.key = key
        self.content = content
        self.tags = tags
        self.modified_history = modified_history
        self.size_bytes = size_bytes


class S3Client:
    def __init__(
        self,
        bucket_name: str,
        profile_name: _Optional[str] = None,
    ) -> None:
        self._bucket_name: str = bucket_name
        self._session = _Session(profile_name=profile_name)
        self._client = self._session.client('s3')

    def set_bucket(self, bucket_name: str) -> None:
        old_name = self._bucket_name
        self._bucket_name = bucket_name
        _logger.warning(f"changed bucket from '{old_name}' to '{self._bucket_name}'")

    def list_file_names(self, symbol: _Optional[_SymbolLiteral] = None) -> _Iterator[str]:
        paginator = self._client.get_paginator("list_objects_v2")
        pages = paginator.paginate(
            Bucket=self._bucket_name,
            Prefix=f"{symbol}/" if symbol else "",
        )
    
        for page in pages:
            for obj in page.get("Contents", []):
                yield obj["Key"]

    def remove_file(self, file_name: str) -> None:
        self._client.delete_object(
            Bucket=self._bucket_name,
            Key=file_name
        )
        _logger.warning(f"removed file '{file_name}' from bucket '{self._bucket_name}'")

    def download_file(self, file_name: str) -> _File:
        response = self._client.get_object(Bucket=self._bucket_name, Key=file_name)
        modified_history: _List[_datetime] = [
            v["LastModified"] for v in self._client.list_object_versions(
                Bucket=self._bucket_name,
                Prefix=file_name,
            )["Versions"]
        ]
        content = response["Body"].read().decode("utf-8")

        tag_response = self._client.get_object_tagging(Bucket=self._bucket_name, Key=file_name)
        tags = {t["Key"]: t["Value"] for t in tag_response.get("TagSet", [])}

        return _File(
            key=file_name,
            content=content,
            tags=tags,
            modified_history=modified_history,
            size_bytes=response["ContentLength"]
        )

    @staticmethod
    def create_file_name(
        symbol: _SymbolLiteral,
        candle_type: _CandleTypeLiteral,
        first_timestamp: _datetime,
        last_timestamp: _datetime,
    ) -> str:
        dt_format = "%Y-%m-%d"
        start_ = first_timestamp.strftime(dt_format)
        end_ = last_timestamp.strftime(dt_format)
        return f"{symbol}/{candle_type}/{start_}-{end_}.csv"

    def upload_file(self, sequence: _Sequence) -> str:
        file_name = S3Client.create_file_name(
            sequence.symbol,
            sequence.candle_type,
            sequence.candles[0].time,
            sequence.candles[-1].time,
        )
        content = sequence.to_csv()
        tags = {
            "num_candles": f"{sequence.num_candles}",
            "num_gaps": f"{sequence.num_gaps}",
            "avg_gap_mins": f"{sequence.avg_gap_mins:.2f}",
        }
        tag_str = ""
        if tags:
            tag_str = "&".join([f"{k}={v}" for k, v in tags.items()])
        self._client.put_object(
            Bucket=self._bucket_name,
            Key=file_name,
            Body=content.encode("utf-8"),
            ContentType="text/csv",
            Tagging=tag_str
        )
        _logger.warning(f"added file '{file_name}' to bucket '{self._bucket_name}'")
        return file_name
