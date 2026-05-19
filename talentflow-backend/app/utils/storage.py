import logging
import uuid
from typing import Optional

import os
from aiobotocore.session import get_session
from botocore.config import Config
from botocore.exceptions import ClientError
from app.config import settings

logger = logging.getLogger(__name__)

def _get_s3_client():
    endpoint_url = f"https://{settings.R2_ACCOUNT_ID}.r2.cloudflarestorage.com"
    session = get_session()
    return session.create_client(
        "s3",
        region_name="auto",
        endpoint_url=endpoint_url,
        aws_access_key_id=settings.R2_ACCESS_KEY_ID,
        aws_secret_access_key=settings.R2_SECRET_ACCESS_KEY,
        config=Config(signature_version="s3v4"),
    )

async def download_file_bytes(r2_key: str) -> Optional[bytes]:
    """
    Downloads file from R2 via presigned URL or directly via S3 client.
    Placeholder for actual R2 integration.
    """
    logger.info(f"Downloading {r2_key} from storage...")
    
    if os.path.exists(r2_key):
        logger.info(f"Reading local file: {r2_key}")
        with open(r2_key, "rb") as f:
            return f.read()

    try:
        async with _get_s3_client() as client:
            response = await client.get_object(
                Bucket=settings.R2_BUCKET_NAME,
                Key=r2_key,
            )
            body = response["Body"]
            return await body.read()
    except ClientError as e:
        logger.error(f"Failed to download {r2_key} from R2: {e}")
        return None
    except Exception as e:
        logger.error(f"Failed to download {r2_key} from R2: {e}")
        return None

async def generate_presigned_upload_url(filename: str, content_type: str, size_bytes: int):
    r2_key = f"raw/{uuid.uuid4().hex}_{filename}"

    async with _get_s3_client() as client:
        upload_url = client.generate_presigned_url(
            "put_object",
            Params={
                "Bucket": settings.R2_BUCKET_NAME,
                "Key": r2_key,
                "ContentType": content_type or "application/octet-stream",
            },
            ExpiresIn=3600,
        )
    return {"filename": filename, "upload_url": upload_url, "r2_key": r2_key}

async def generate_presigned_download_url(r2_key: str):
    async with _get_s3_client() as client:
        return client.generate_presigned_url(
            "get_object",
            Params={"Bucket": settings.R2_BUCKET_NAME, "Key": r2_key},
            ExpiresIn=3600,
        )

async def verify_r2_key_exists(r2_key: str) -> bool:
    try:
        async with _get_s3_client() as client:
            await client.head_object(Bucket=settings.R2_BUCKET_NAME, Key=r2_key)
            return True
    except ClientError:
        return False
    except Exception as e:
        logger.error(f"R2 head failed for {r2_key}: {e}")
        return False

async def validate_file_magic_bytes(r2_key: str) -> bool:
    try:
        import magic
    except Exception:
        logger.warning("python-magic not available; skipping file validation")
        return True

    file_bytes = await download_file_bytes(r2_key)
    if not file_bytes:
        return False

    mime = magic.from_buffer(file_bytes[:2048], mime=True)
    return mime in {"application/pdf", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"}
