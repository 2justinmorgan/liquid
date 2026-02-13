from unittest import TestCase
from unittest.mock import patch, MagicMock
from datetime import datetime, timezone, time
from src.defines.instrument import (
    TradingHour,
    _TradingHourDto,
    WeekdayLiteral,
    Session,
    EventTypeLiteral,
)


def append_target_module(var_name: str) -> str:
    return f"src.defines.instrument.{var_name}"


class TestTradingHour(TestCase):
    def create_th(self, day: WeekdayLiteral, time_str: str) -> TradingHour:
        # Note: Added eventType to match your DTO requirement
        dto = _TradingHourDto(weekDay=f"{day}, {time_str}Z", eventType="SESSION_OPEN")
        return TradingHour(dto)

    def test_to_dt_earlier_today(self) -> None:
        # Focal: Wednesday, Feb 11th, 15:00
        focal_now = datetime(2026, 2, 11, 15, 0, 0, tzinfo=timezone.utc)
        
        # Target: Wednesday, 10:00 (occurs earlier the same day)
        th = self.create_th("Wednesday", "10:00:00")
        result = th.to_dt(focal_now)
        
        self.assertEqual(result, datetime(2026, 2, 11, 10, 0, 0, tzinfo=timezone.utc))

    def test_to_dt_later_today(self) -> None:
        # Focal: Wednesday, Feb 11th, 15:00
        focal_now = datetime(2026, 2, 11, 15, 0, 0, tzinfo=timezone.utc)
        
        # Target: Wednesday, 22:00 (hasn't happened yet today, should look back 7 days)
        th = self.create_th("Wednesday", "22:00:00")
        result = th.to_dt(focal_now)
        
        # Expected: Previous Wednesday, Feb 4th
        expected = datetime(2026, 2, 4, 22, 0, 0, tzinfo=timezone.utc)
        self.assertEqual(result, expected)

    def test_to_dt_earlier_in_week(self) -> None:
        # Focal: Wednesday, Feb 11th, 15:00
        focal_now = datetime(2026, 2, 11, 15, 0, 0, tzinfo=timezone.utc)
        
        # Target: Monday, 09:00
        th = self.create_th("Monday", "09:00:00")
        result = th.to_dt(focal_now)
        
        # Expected: Monday, Feb 9th
        expected = datetime(2026, 2, 9, 9, 0, 0, tzinfo=timezone.utc)
        self.assertEqual(result, expected)

    def test_to_dt_exact_match(self) -> None:
        # Focal: Wednesday, Feb 11th, 22:00
        focal_now = datetime(2026, 2, 11, 22, 0, 0, tzinfo=timezone.utc)
        
        th = self.create_th("Wednesday", "22:00:00")
        result = th.to_dt(focal_now)
        
        self.assertEqual(result, focal_now)

    def test_to_dt_cross_year_boundary(self) -> None:
        # Focal: Friday, Jan 2nd, 2026
        focal_now = datetime(2026, 1, 2, 10, 0, 0, tzinfo=timezone.utc)
        
        # Target: Wednesday, 10:00
        th = self.create_th("Wednesday", "10:00:00")
        result = th.to_dt(focal_now)
        
        # Expected: Wednesday, Dec 31st, 2025
        expected = datetime(2025, 12, 31, 10, 0, 0, tzinfo=timezone.utc)
        self.assertEqual(result, expected)

    def test_to_dt_lookback_trigger(self) -> None:
        # Focal: Thursday, Feb 12th, 07:00:00
        focal_now = datetime(2026, 2, 12, 7, 0, 0, tzinfo=timezone.utc)

        # Target: Thursday at 08:00:00 (one hour 'after' focal time)
        th = self.create_th("Thursday", "08:00:00")
        result = th.to_dt(focal_now)

        # Expected: Thursday, Feb 5th
        expected = datetime(2026, 2, 5, 8, 0, 0, tzinfo=timezone.utc)
        self.assertEqual(result, expected)


class TestSession(TestCase):
    def create_th(self, day: WeekdayLiteral, time_str: str, event: EventTypeLiteral) -> TradingHour:
        return TradingHour.const(day, time.fromisoformat(time_str), event)

    @patch(append_target_module("_datetime"))
    def test_session_init_success(self, mock_datetime: MagicMock) -> None:
        # Thursday, Feb 12
        mock_now = datetime(2026, 2, 12, 12, 0, 0, tzinfo=timezone.utc)
        mock_datetime.now.return_value = mock_now
        mock_datetime.combine = datetime.combine

        th_open = self.create_th("Friday", "17:00:00", "SESSION_OPEN")
        th_close = self.create_th("Saturday", "10:00:00", "SESSION_CLOSE")

        session = Session(th_open, th_close)

        # Friday, Feb 6th
        self.assertEqual(session.start_day, "Friday")
        self.assertEqual(
            session.open_time,
            datetime(2026, 2, 6, 17, 0, 0, tzinfo=timezone.utc),
        )
        self.assertEqual(
            session.close_time,
            datetime(2026, 2, 7, 10, 0, 0, tzinfo=timezone.utc),
        )

    def test_session_init_invalid_types(self) -> None:
        th_open = self.create_th("Monday", "08:00:00", "SESSION_CLOSE")
        th_close = self.create_th("Monday", "17:00:00", "SESSION_CLOSE")

        with self.assertRaises(ValueError) as cm:
            Session(th_open, th_close)

        self.assertIn("sessions need to begin and end", str(cm.exception))

    def test_session_init_too_long_times(self) -> None:
        th_open = self.create_th("Monday", "08:00:00", "SESSION_OPEN")
        th_close = self.create_th("Tuesday", "17:00:00", "SESSION_CLOSE")

        with self.assertRaises(ValueError) as cm:
            Session(th_open, th_close)

        self.assertIn("sessions can not be longer than 24 hours", str(cm.exception))

    @patch(append_target_module("_datetime"))
    def test_create_sessions_with_specific_focal(self, mock_datetime: MagicMock) -> None:
        # Wednesday, Feb 11th
        focal = datetime(2026, 2, 11, 13, 35, 15, tzinfo=timezone.utc)
        mock_datetime.now.return_value = focal
        mock_datetime.combine = datetime.combine

        trading_hours = [
            self.create_th("Sunday", "08:00:00", "SESSION_OPEN"),
            self.create_th("Sunday", "17:00:00", "SESSION_CLOSE"),
            self.create_th("Saturday", "08:00:00", "SESSION_OPEN"),
            self.create_th("Saturday", "17:00:00", "SESSION_CLOSE"),
            self.create_th("Friday", "09:30:00", "SESSION_OPEN"),
            self.create_th("Friday", "14:45:00", "SESSION_CLOSE"),
            self.create_th("Monday", "08:00:00", "SESSION_OPEN"),
            self.create_th("Monday", "17:00:00", "SESSION_CLOSE"),
            self.create_th("Tuesday", "08:00:00", "SESSION_OPEN"),
            self.create_th("Tuesday", "17:00:00", "SESSION_CLOSE"),
            self.create_th("Wednesday", "08:00:00", "SESSION_OPEN"),
            self.create_th("Wednesday", "17:00:00", "SESSION_CLOSE"),
            self.create_th("Thursday", "08:00:00", "SESSION_OPEN"),
            self.create_th("Thursday", "17:00:00", "SESSION_CLOSE"),
        ]

        sessions = Session.create_sessions(trading_hours)

        # Monday, Feb 9th
        self.assertEqual(sessions[3].start_day, "Monday")
        self.assertEqual(
            sessions[3].open_time,
            datetime(2026, 2, 9, 8, 0, 0, tzinfo=timezone.utc),
        )
        self.assertEqual(
            sessions[3].close_time,
            datetime(2026, 2, 9, 17, 0, 0, tzinfo=timezone.utc),
        )

        # Tuesday, Feb 10th
        self.assertEqual(sessions[4].start_day, "Tuesday")
        self.assertEqual(
            sessions[4].open_time,
            datetime(2026, 2, 10, 8, 0, 0, tzinfo=timezone.utc),
        )
        self.assertEqual(
            sessions[4].close_time,
            datetime(2026, 2, 10, 17, 0, 0, tzinfo=timezone.utc),
        )

        # Wednesday, Feb 4th
        self.assertEqual(sessions[5].start_day, "Wednesday")
        self.assertEqual(
            sessions[5].open_time,
            datetime(2026, 2, 4, 8, 0, 0, tzinfo=timezone.utc)
        )
        self.assertEqual(
            sessions[5].close_time,
            datetime(2026, 2, 4, 17, 0, 0, tzinfo=timezone.utc)
        )

        # Thursday, Feb 5th
        self.assertEqual(sessions[6].start_day, "Thursday")
        self.assertEqual(
            sessions[6].open_time,
            datetime(2026, 2, 5, 8, 0, 0, tzinfo=timezone.utc)
        )
        self.assertEqual(
            sessions[6].close_time,
            datetime(2026, 2, 5, 17, 0, 0, tzinfo=timezone.utc)
        )

        # Friday, Feb 6th
        self.assertEqual(sessions[2].start_day, "Friday")
        self.assertEqual(
            sessions[2].open_time,
            datetime(2026, 2, 6, 9, 30, 0, tzinfo=timezone.utc)
        )
        self.assertEqual(
            sessions[2].close_time,
            datetime(2026, 2, 6, 14, 45, 0, tzinfo=timezone.utc)
        )

        # Saturday, Feb 7th
        self.assertEqual(sessions[1].start_day, "Saturday")
        self.assertEqual(
            sessions[1].open_time,
            datetime(2026, 2, 7, 8, 0, 0, tzinfo=timezone.utc)
        )
        self.assertEqual(
            sessions[1].close_time,
            datetime(2026, 2, 7, 17, 0, 0, tzinfo=timezone.utc)
        )

        # Sunday, Feb 8th
        self.assertEqual(sessions[0].start_day, "Sunday")
        self.assertEqual(
            sessions[0].open_time,
            datetime(2026, 2, 8, 8, 0, 0, tzinfo=timezone.utc)
        )
        self.assertEqual(
            sessions[0].close_time,
            datetime(2026, 2, 8, 17, 0, 0, tzinfo=timezone.utc)
        )
