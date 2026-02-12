from typing import (
    Optional as _Optional,
    Iterator as _Iterator,
)
from boto3 import (
    Session as _Session,
)
from src.defines.instrument import (
    SymbolLiteral as _SymbolLiteral,
)


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
        self._bucket_name = bucket_name

    def list_file_names(self, symbol: _Optional[_SymbolLiteral] = None) -> _Iterator[str]:
        paginator = self._client.get_paginator("list_objects_v2")
        pages = paginator.paginate(
            Bucket=self._bucket_name,
            Prefix=f"{symbol}/" if symbol else "",
        )
    
        for page in pages:
            for obj in page.get("Contents", []):
                yield obj["Key"]

    def fetch_file_content(self, file_name: str) -> str:
        response = self._client.get_object(Bucket=self._bucket_name, Key=file_name)
        return response["Body"].read().decode("utf-8")
