from unittest import TestCase
from unittest.mock import patch, MagicMock
from parameterized import parameterized
from typing import List, Callable
from datetime import datetime, timezone, timedelta, date
from src.defines.instrument import TradingHour, EventTypeLiteral, WeekdayLiteral
from src.defines.candle import Candle
from src.analyze.sequence import _Week, _Day, Sequence


def append_target_module(var_name: str) -> str:
    return f"src.analyze.sequence.{var_name}"


event_type: EventTypeLiteral = [
    "SESSION_OPEN",
    "SESSION_CLOSE",
]


class TestAnalyze(TestCase):
    @parameterized.expand([
        (
            "Friday",
            [
                TradingHour(MagicMock(weekDay="Monday, 07:00:00Z", eventType=event_type[0])),
                TradingHour(MagicMock(weekDay="Monday, 20:55:00Z", eventType=event_type[1])),
                TradingHour(MagicMock(weekDay="Wednesday, 07:00:00Z", eventType=event_type[0])),
                TradingHour(MagicMock(weekDay="Wednesday, 20:55:00Z", eventType=event_type[1])),
                TradingHour(MagicMock(weekDay="Friday, 07:00:00Z", eventType=event_type[0])),
                TradingHour(MagicMock(weekDay="Friday, 20:55:00Z", eventType=event_type[1])),
            ],
            [2, 0, -2],
        ),
        (
            "Sunday",
            [
                TradingHour(MagicMock(weekDay="Monday, 07:00:00Z", eventType=event_type[0])),
                TradingHour(MagicMock(weekDay="Monday, 20:55:00Z", eventType=event_type[1])),
                TradingHour(MagicMock(weekDay="Wednesday, 07:00:00Z", eventType=event_type[0])),
                TradingHour(MagicMock(weekDay="Wednesday, 20:55:00Z", eventType=event_type[1])),
                TradingHour(MagicMock(weekDay="Friday, 07:00:00Z", eventType=event_type[0])),
                TradingHour(MagicMock(weekDay="Friday, 20:55:00Z", eventType=event_type[1])),
            ],
            [4, 2, 0],
        ),
        (
            "Tuesday",
            [
                TradingHour(MagicMock(weekDay="Monday, 07:00:00Z", eventType=event_type[0])),
                TradingHour(MagicMock(weekDay="Monday, 20:55:00Z", eventType=event_type[1])),
                TradingHour(MagicMock(weekDay="Tuesday, 07:00:00Z", eventType=event_type[0])),
                TradingHour(MagicMock(weekDay="Tuesday, 20:55:00Z", eventType=event_type[1])),
                TradingHour(MagicMock(weekDay="Wednesday, 07:00:00Z", eventType=event_type[0])),
                TradingHour(MagicMock(weekDay="Wednesday, 20:55:00Z", eventType=event_type[1])),
                TradingHour(MagicMock(weekDay="Thursday, 07:00:00Z", eventType=event_type[0])),
                TradingHour(MagicMock(weekDay="Thursday, 20:55:00Z", eventType=event_type[1])),
                TradingHour(MagicMock(weekDay="Friday, 07:00:00Z", eventType=event_type[0])),
                TradingHour(MagicMock(weekDay="Friday, 20:55:00Z", eventType=event_type[1])),
            ],
            [0, -2, -4, -6, -8],
        ),
    ])
    def test__get_prev_week_indices(
        self,
        today: WeekdayLiteral,
        trading_hours: List[TradingHour],
        expected: List[int],
    ) -> None:
        actual = _Week._get_prev_week_indices(today, trading_hours)
        self.assertEqual(actual, expected)

    @parameterized.expand([
        (
            # Thursday, Jan 15th
            datetime(2026, 1, 15).date(),
            TradingHour(MagicMock(weekDay="Thursday, 08:30:00Z", eventType=event_type[0])),
            TradingHour(MagicMock(weekDay="Thursday, 12:15:00Z", eventType=event_type[1])),
            lambda case, _day: (
                case.assertEqual(_day.start_time.year, 2026),
                case.assertEqual(_day.start_time.month, 1),
                case.assertEqual(_day.start_time.day, 15),
                case.assertEqual(_day.start_time.hour, 8),
                case.assertEqual(_day.start_time.minute, 30),
                case.assertEqual(_day.start_time.second, 0),
                case.assertEqual(_day.end_time.year, 2026),
                case.assertEqual(_day.end_time.month, 1),
                case.assertEqual(_day.end_time.day, 15),
                case.assertEqual(_day.end_time.hour, 12),
                case.assertEqual(_day.end_time.minute, 15),
                case.assertEqual(_day.end_time.second, 0),
            ),
        ),
        (
            # Thursday, Jan 15th
            datetime(2026, 1, 15).date(),
            TradingHour(MagicMock(weekDay="Thursday, 20:00:00Z", eventType=event_type[0])),
            TradingHour(MagicMock(weekDay="Friday, 09:25:00Z", eventType=event_type[1])),
            lambda case, _day: (
                case.assertEqual(_day.start_time.year, 2026),
                case.assertEqual(_day.start_time.month, 1),
                case.assertEqual(_day.start_time.day, 15),
                case.assertEqual(_day.start_time.hour, 20),
                case.assertEqual(_day.start_time.minute, 0),
                case.assertEqual(_day.start_time.second, 0),
                case.assertEqual(_day.end_time.year, 2026),
                case.assertEqual(_day.end_time.month, 1),
                case.assertEqual(_day.end_time.day, 16),
                case.assertEqual(_day.end_time.hour, 9),
                case.assertEqual(_day.end_time.minute, 25),
                case.assertEqual(_day.end_time.second, 0),
            ),
        ),
    ])
    def test_to_day(
        self,
        open_date: date,
        open_th: TradingHour,
        close_th: TradingHour,
        assert_expected: Callable[[TestCase, _Day], tuple],
    ) -> None:
        actual = _Day.to_day(open_date, open_th, close_th)
        assert_expected(self, actual)

    @parameterized.expand([
        (
            # Thursday
            3,
            # Thursday, Jan 15th
            datetime(2026, 1, 15).date(),
            lambda case, _date: (
                case.assertEqual(_date.year, 2026),
                case.assertEqual(_date.month, 1),
                case.assertEqual(_date.day, 8),
                case.assertEqual(_date.weekday(), 3),
            ),
        ),
        (
            # Friday
            4,
            # Thursday, Jan 15th
            datetime(2026, 1, 15).date(),
            lambda case, _date: (
                case.assertEqual(_date.year, 2026),
                case.assertEqual(_date.month, 1),
                case.assertEqual(_date.day, 9),
                case.assertEqual(_date.weekday(), 4),
            ),
        ),
        (
            # Friday
            4,
            # Sunday, Feb 1st
            datetime(2026, 2, 1).date(),
            lambda case, _date: (
                case.assertEqual(_date.year, 2026),
                case.assertEqual(_date.month, 1),
                case.assertEqual(_date.day, 30),
                case.assertEqual(_date.weekday(), 4),
            ),
        ),
    ])
    def test__get_last_date(
        self,
        weekday: int,
        curr_date: date,
        assert_expected: Callable[[TestCase, date], tuple],
    ) -> None:
        actual = _Week._get_last_date(weekday, curr_date)
        assert_expected(self, actual)

    def test_get_prev_week(self) -> None:
        trading_hours = [
            TradingHour(MagicMock(weekDay="Monday, 07:00:00Z", eventType=event_type[0])),
            TradingHour(MagicMock(weekDay="Monday, 20:55:00Z", eventType=event_type[1])),
            TradingHour(MagicMock(weekDay="Tuesday, 07:00:00Z", eventType=event_type[0])),
            TradingHour(MagicMock(weekDay="Tuesday, 20:55:00Z", eventType=event_type[1])),
            TradingHour(MagicMock(weekDay="Wednesday, 07:00:00Z", eventType=event_type[0])),
            TradingHour(MagicMock(weekDay="Wednesday, 20:55:00Z", eventType=event_type[1])),
            TradingHour(MagicMock(weekDay="Thursday, 07:00:00Z", eventType=event_type[0])),
            TradingHour(MagicMock(weekDay="Thursday, 20:55:00Z", eventType=event_type[1])),
            TradingHour(MagicMock(weekDay="Friday, 09:30:00Z", eventType=event_type[0])),
            TradingHour(MagicMock(weekDay="Friday, 19:25:00Z", eventType=event_type[1])),
        ]
        # Wednesday, Jan 14th at 13:35 and 13 seconds
        now = datetime(2026, 1, 14, 13, 35, 13, tzinfo=timezone.utc)
        actual: _Week = _Week.get_prev_week(now, trading_hours)

        self.assertEqual(actual.num_days, 5)
        # Wednesday, Jan 7th
        curr_day = actual.first_day
        self.assertEqual(curr_day.start_time.year, 2026)
        self.assertEqual(curr_day.start_time.month, 1)
        self.assertEqual(curr_day.start_time.day, 7)
        self.assertEqual(curr_day.start_time.hour, 7)
        self.assertEqual(curr_day.start_time.minute, 0)
        self.assertEqual(curr_day.start_time.second, 0)
        self.assertEqual(curr_day.end_time.year, 2026)
        self.assertEqual(curr_day.end_time.month, 1)
        self.assertEqual(curr_day.end_time.day, 7)
        self.assertEqual(curr_day.end_time.hour, 20)
        self.assertEqual(curr_day.end_time.minute, 55)
        self.assertEqual(curr_day.end_time.second, 0)

        # Thursday, Jan 8th
        curr_day = actual.first_day.next_
        self.assertEqual(curr_day.start_time.year, 2026)
        self.assertEqual(curr_day.start_time.month, 1)
        self.assertEqual(curr_day.start_time.day, 8)
        self.assertEqual(curr_day.start_time.hour, 7)
        self.assertEqual(curr_day.start_time.minute, 0)
        self.assertEqual(curr_day.start_time.second, 0)
        self.assertEqual(curr_day.end_time.year, 2026)
        self.assertEqual(curr_day.end_time.month, 1)
        self.assertEqual(curr_day.end_time.day, 8)
        self.assertEqual(curr_day.end_time.hour, 20)
        self.assertEqual(curr_day.end_time.minute, 55)
        self.assertEqual(curr_day.end_time.second, 0)

        # Friday, Jan 9th
        curr_day = actual.first_day.next_.next_
        self.assertEqual(curr_day.start_time.year, 2026)
        self.assertEqual(curr_day.start_time.month, 1)
        self.assertEqual(curr_day.start_time.day, 9)
        self.assertEqual(curr_day.start_time.hour, 9)
        self.assertEqual(curr_day.start_time.minute, 30)
        self.assertEqual(curr_day.start_time.second, 0)
        self.assertEqual(curr_day.end_time.year, 2026)
        self.assertEqual(curr_day.end_time.month, 1)
        self.assertEqual(curr_day.end_time.day, 9)
        self.assertEqual(curr_day.end_time.hour, 19)
        self.assertEqual(curr_day.end_time.minute, 25)
        self.assertEqual(curr_day.end_time.second, 0)

        # Monday, Jan 12th
        curr_day = actual.first_day.next_.next_.next_
        self.assertEqual(curr_day.start_time.year, 2026)
        self.assertEqual(curr_day.start_time.month, 1)
        self.assertEqual(curr_day.start_time.day, 12)
        self.assertEqual(curr_day.start_time.hour, 7)
        self.assertEqual(curr_day.start_time.minute, 0)
        self.assertEqual(curr_day.start_time.second, 0)
        self.assertEqual(curr_day.end_time.year, 2026)
        self.assertEqual(curr_day.end_time.month, 1)
        self.assertEqual(curr_day.end_time.day, 12)
        self.assertEqual(curr_day.end_time.hour, 20)
        self.assertEqual(curr_day.end_time.minute, 55)
        self.assertEqual(curr_day.end_time.second, 0)

        # Tuesday, Jan 13th
        curr_day = actual.first_day.next_.next_.next_.next_
        self.assertEqual(curr_day.start_time.year, 2026)
        self.assertEqual(curr_day.start_time.month, 1)
        self.assertEqual(curr_day.start_time.day, 13)
        self.assertEqual(curr_day.start_time.hour, 7)
        self.assertEqual(curr_day.start_time.minute, 0)
        self.assertEqual(curr_day.start_time.second, 0)
        self.assertEqual(curr_day.end_time.year, 2026)
        self.assertEqual(curr_day.end_time.month, 1)
        self.assertEqual(curr_day.end_time.day, 13)
        self.assertEqual(curr_day.end_time.hour, 20)
        self.assertEqual(curr_day.end_time.minute, 55)
        self.assertEqual(curr_day.end_time.second, 0)

    def test_sequence_const(self) -> None:
        now = datetime(2026, 2, 14, 13, 55, 13)
        candles = [
            Candle(MagicMock(open=3, close=4, high=4.5, low=2.5, time=now)),
            Candle(MagicMock(open=3, close=4, high=4.5, low=2.5, time=now + timedelta(minutes=1))),
            Candle(MagicMock(open=3, close=4, high=4.5, low=2.5, time=now + timedelta(minutes=2))),
            Candle(MagicMock(open=3, close=4, high=4.5, low=2.5, time=now + timedelta(minutes=3))),
            Candle(MagicMock(open=3, close=4, high=4.5, low=2.5, time=now + timedelta(minutes=4))),
        ]
        sequence = Sequence("", "m", candles)
        self.assertEqual(sequence.num_candles, 5)
        self.assertEqual(sequence.candle_type, "m")
        self.assertEqual(sequence.candles, candles)

    @patch(append_target_module("_logger"))
    def test_sequence_const_missing_candles(self, _logger: MagicMock) -> None:
        now = datetime(2026, 2, 14, 13, 55, 13)
        candles = [
            Candle(MagicMock(open=3, close=4, high=4.5, low=2.5, time=now)),
            Candle(MagicMock(open=3, close=4, high=4.5, low=2.5, time=now + timedelta(minutes=1))),
            Candle(MagicMock(open=3, close=4, high=4.5, low=2.5, time=now + timedelta(minutes=4))),
            Candle(MagicMock(open=3, close=4, high=4.5, low=2.5, time=now + timedelta(minutes=5))),
        ]

        sequence = Sequence("", "m", candles)

        self.assertEqual(sequence.num_candles, 4)
        self.assertEqual(sequence.candle_type, "m")
        self.assertEqual(sequence.num_gaps, 1)
        self.assertEqual(sequence.avg_gap_mins, 2.0)
        _logger.warning.assert_called_once_with(
            "candle-times '2026-02-14 13:56:13' and '2026-02-14 13:59:13' are not sequential"
        )
