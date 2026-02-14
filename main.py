from os import getenv
from datetime import datetime, timedelta, time, timezone
from json import dumps, loads
from src.liquid import Liquid
from src.analyze.sequence import Sequence
from src.storage.s3.client import S3Client
from src.defines.instrument import Session, TradingHour


liquid = Liquid(getenv("LIQUID_UN"), getenv("LIQUID_PW"), getenv("LIQUID_API_BASE_URL"), getenv("LIQUID_ACCOUNT_ID"))
instruments = liquid.get_instruments()
s3 = S3Client("minute-candles")
file_names = set(s3.list_file_names())


DEFAULT_TRADING_HOURS = [
    TradingHour.const("Monday", time(0, 0, 0), "SESSION_OPEN"),
    TradingHour.const("Monday", time(23, 59, 0), "SESSION_CLOSE"),
    TradingHour.const("Tuesday", time(0, 0, 0), "SESSION_OPEN"),
    TradingHour.const("Tuesday", time(23, 59, 0), "SESSION_CLOSE"),
    TradingHour.const("Wednesday", time(0, 0, 0), "SESSION_OPEN"),
    TradingHour.const("Wednesday", time(23, 59, 0), "SESSION_CLOSE"),
    TradingHour.const("Thursday", time(0, 0, 0), "SESSION_OPEN"),
    TradingHour.const("Thursday", time(23, 59, 0), "SESSION_CLOSE"),
    TradingHour.const("Friday", time(0, 0, 0), "SESSION_OPEN"),
    TradingHour.const("Friday", time(23, 59, 0), "SESSION_CLOSE"),
    TradingHour.const("Saturday", time(0, 0, 0), "SESSION_OPEN"),
    TradingHour.const("Saturday", time(23, 59, 0), "SESSION_CLOSE"),
    TradingHour.const("Sunday", time(0, 0, 0), "SESSION_OPEN"),
    TradingHour.const("Sunday", time(23, 59, 0), "SESSION_CLOSE"),
]

for i in instruments:
    symbol = i.symbol
    print(f"symbol:{symbol}")
    if i.currency != "USD":
        print("  --ignore-not-usd")
        continue
    if symbol[-5:] == ".cent":
        print("  --ignore-dot-cent")
        continue
    sessions = Session.create_sessions(
        i.trading_hours or DEFAULT_TRADING_HOURS,
        datetime.now(tz=timezone.utc) - timedelta(days=1),
    )
    for session in sessions:
        file_name = S3Client.create_file_name(
            symbol,
            "m",
            session.open_time,
            session.close_time,
        )
        if file_name in file_names:
            print(f"  EXISTS:{file_name}")
            continue
        else:
            print(f"    GOING FOR {symbol}")
        try:
            sequence = Sequence.fetch_sequence(
                symbol,
                "m",
                session,
                liquid,
            )
        except Exception as exception:
            print("    err:", str(exception))
            continue
        s3.upload_file(sequence)
