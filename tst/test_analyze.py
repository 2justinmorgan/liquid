from unittest import TestCase
from src.analyze import Cursor


class TestAnalyze(TestCase):
    def test_sma_5(self) -> None:
        def decide_to_buy(cursor: Cursor) -> bool:
            return False
        def decide_to_sell(cursor: Cursor) -> bool:
            return False
        cursor = Cursor(
            decide_to_buy,
            decide_to_sell,
        )
        nums = [2, 4, 1, 8, 7, 9, 5, 1]
        cursor.move(nums.pop(0))
        cursor.move(nums.pop(0))
        cursor.move(nums.pop(0))
        cursor.move(nums.pop(0))
        cursor.move(nums.pop(0))
        self.assertEqual(cursor.sma_5, 4.4)

        cursor.move(nums.pop(0))
        self.assertEqual(cursor.sma_5, 5.8)

    def test_min_max_no_trades(self) -> None:
        def decide_to_buy(cursor: Cursor) -> bool:
            return False
        def decide_to_sell(cursor: Cursor) -> bool:
            return False
        cursor = Cursor(
            decide_to_buy,
            decide_to_sell,
        )
        nums = [2, 4, 1, 8, 7, 9, 5, 1]
        self.assertEqual(cursor.min, Cursor.DEFAULT_MIN)
        self.assertEqual(cursor.max, 0)

        cursor.move(nums.pop(0))
        self.assertEqual(cursor.min, 2)
        self.assertEqual(cursor.max, 2)

        cursor.move(nums.pop(0))
        self.assertEqual(cursor.min, 2)
        self.assertEqual(cursor.max, 4)

        cursor.move(nums.pop(0))
        self.assertEqual(cursor.min, 1)
        self.assertEqual(cursor.max, 4)

        cursor.move(nums.pop(0))
        self.assertEqual(cursor.min, 1)
        self.assertEqual(cursor.max, 8)

        cursor.move(nums.pop(0))
        self.assertEqual(cursor.min, 1)
        self.assertEqual(cursor.max, 8)

        cursor.move(nums.pop(0))
        self.assertEqual(cursor.min, 1)
        self.assertEqual(cursor.max, 9)

        cursor.move(nums.pop(0))
        self.assertEqual(cursor.min, 1)
        self.assertEqual(cursor.max, 9)

        cursor.move(nums.pop(0))
        self.assertEqual(cursor.min, 1)
        self.assertEqual(cursor.max, 9)

    def test_min_max_with_trades(self) -> None:
        def decide_to_buy(cursor: Cursor) -> bool:
            return cursor.curr < 2
        def decide_to_sell(cursor: Cursor) -> bool:
            return cursor.curr > 8
        cursor = Cursor(
            decide_to_buy,
            decide_to_sell,
        )
        nums = [2, 4, 1, 8, 7, 9, 5, 1]
        self.assertEqual(cursor.min, Cursor.DEFAULT_MIN)
        self.assertEqual(cursor.max, 0)

        cursor.move(nums.pop(0))
        self.assertEqual(cursor.min, 2)
        self.assertEqual(cursor.max, 2)

        cursor.move(nums.pop(0))
        self.assertEqual(cursor.min, 2)
        self.assertEqual(cursor.max, 4)

        cursor.move(nums.pop(0))
        self.assertEqual(cursor.min, 1)
        self.assertEqual(cursor.max, 4)

        cursor.move(nums.pop(0))
        self.assertEqual(cursor.min, 1)
        self.assertEqual(cursor.max, 8)

        cursor.move(nums.pop(0))
        self.assertEqual(cursor.min, 1)
        self.assertEqual(cursor.max, 8)

        cursor.move(nums.pop(0))
        self.assertEqual(cursor.min, Cursor.DEFAULT_MIN)
        self.assertEqual(cursor.max, 0)

        cursor.move(nums.pop(0))
        self.assertEqual(cursor.min, 5)
        self.assertEqual(cursor.max, 5)

        cursor.move(nums.pop(0))
        self.assertEqual(cursor.min, 1)
        self.assertEqual(cursor.max, 5)

    def test_p_and_l(self) -> None:
        def decide_to_buy(cursor: Cursor) -> bool:
            if cursor.is_in_position:
                return False
            return cursor.curr < 3
        def decide_to_sell(cursor: Cursor) -> bool:
            if not cursor.is_in_position:
                return False
            return cursor.curr > 8
        cursor = Cursor(
            decide_to_buy,
            decide_to_sell,
        )
        nums = [2, 4, 1, 8, 7, 9, 5, 1]
        self.assertEqual(cursor.p_and_l, 0)
        self.assertEqual(cursor.p_and_l_percentage, 0)
        cursor.move(nums.pop(0))
        self.assertEqual(cursor.p_and_l, 0)
        self.assertEqual(cursor.p_and_l_percentage, 0)

        cursor.move(nums.pop(0))
        cursor.move(nums.pop(0))
        cursor.move(nums.pop(0))
        cursor.move(nums.pop(0))
        cursor.move(nums.pop(0))
        self.assertEqual(cursor.p_and_l, 7)
        self.assertEqual(cursor.p_and_l_percentage, (9 - 2)/2)

        cursor.move(nums.pop(0))
        cursor.move(nums.pop(0))
        self.assertEqual(cursor.p_and_l, 7)
        self.assertEqual(cursor.p_and_l_percentage, (9 - 2)/2)
