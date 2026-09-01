import unittest
from quinaryram import Bank
from quinaryram.gui_support import demo_arguments

class BankTests(unittest.TestCase):
    def test_all_five_controls(self) -> None:
        bank = Bank(1, 5, -10, 10, [[5, -2, 7, 3, 1]])
        metrics = bank.step([[-2, -1, 0, 1, 2]], [[9, 9, 9, 4, -6]])
        self.assertEqual(bank.data, ((0, -1, 7, 7, -6),))
        self.assertEqual(metrics.changed, 4)
        self.assertEqual(metrics.controls["bypass"], 1)

    def test_saturates_without_overflow(self) -> None:
        bank = Bank(1, 2, -5, 5, [[4, -4]])
        metrics = bank.step([[1, 1]], [[10, -10]])
        self.assertEqual(bank.data, ((5, -5),))
        self.assertEqual(metrics.saturated, 2)

    def test_invalid_control_is_atomic(self) -> None:
        bank = Bank(1, 2, initial=[[1, 2]])
        with self.assertRaises(ValueError):
            bank.step([[1, 9]], [[1, 1]])
        self.assertEqual(bank.data, ((1, 2),))

    def test_snapshot_round_trip(self) -> None:
        bank = Bank(1, 2, -8, 8, [[3, -3]])
        self.assertEqual(Bank.from_snapshot(bank.snapshot()).data, bank.data)

    def test_snapshot_rejects_fractional_dimension_instead_of_truncating(self) -> None:
        payload = Bank(1, 1, -5, 5, [[2]]).snapshot()
        payload["slots"] = 1.9
        with self.assertRaisesRegex(ValueError, "snapshot slots must be an integer"):
            Bank.from_snapshot(payload)

    def test_bank_rejects_boolean_dimensions(self) -> None:
        with self.assertRaisesRegex(ValueError, "slots must be an integer"):
            Bank(True, 1)

    def test_gui_blank_arguments_use_bundled_program(self) -> None:
        self.assertEqual(demo_arguments(""), ("examples/program.json",))

    def test_gui_preserves_custom_arguments(self) -> None:
        self.assertEqual(
            demo_arguments('"my program.json" --out snapshot.json'),
            ("my program.json", "--out", "snapshot.json"),
        )

if __name__ == "__main__":
    unittest.main()
