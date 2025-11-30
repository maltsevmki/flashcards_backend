import datetime
import hashlib


def anki_field_checksum(field: str) -> int:
    return int.from_bytes(hashlib.sha1(field.encode('utf-8')).digest()[:8], 'big')


def get_modification_epoch(user_timezone_offset_minutes: int) -> int:
    utc_created = datetime.datetime.now(datetime.timezone.utc)
    local_mod = utc_created - datetime.timedelta(minutes=user_timezone_offset_minutes)

    return int(local_mod.timestamp())
