from unittest import TestCase
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
from src.defines.candle import Candle
from src.analyze.sequence import Sequence


def append_target_module(var_name: str) -> str:
    return f"src.analyze.sequence.{var_name}"


class TestAnalyze(TestCase):
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

        sequence = Sequence("SYM", "m", candles)

        self.assertEqual(sequence.num_candles, 4)
        self.assertEqual(sequence.candle_type, "m")
        self.assertEqual(sequence.num_gaps, 1)
        self.assertEqual(sequence.avg_gap_mins, 2.0)
        _logger.warning.assert_called_once_with(
            "'SYM' candle-times '2026-02-14 13:56:13' and '2026-02-14 13:59:13' are not sequential"
        )
