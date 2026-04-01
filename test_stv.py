import unittest
from unittest.mock import patch
from io import StringIO

from stv import parse_ballot, count_votes, run_stv


class TestParseBallot(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(parse_ballot("Alice;Bob;Carol"), ["Alice", "Bob", "Carol"])

    def test_trailing_semicolon(self):
        self.assertEqual(parse_ballot("Alice;Bob;Carol;"), ["Alice", "Bob", "Carol"])

    def test_whitespace_trimmed(self):
        self.assertEqual(parse_ballot(" Alice ; Bob ; Carol "), ["Alice", "Bob", "Carol"])

    def test_empty_string(self):
        self.assertIsNone(parse_ballot(""))

    def test_only_semicolons(self):
        self.assertIsNone(parse_ballot(";;;"))

    def test_single_candidate(self):
        self.assertEqual(parse_ballot("Alice;"), ["Alice"])


class TestCountVotes(unittest.TestCase):
    def test_first_preferences(self):
        ballots = [["Alice", "Bob"], ["Bob", "Alice"], ["Alice", "Carol"]]
        totals, exhausted = count_votes(ballots, set())
        self.assertEqual(totals["Alice"], 2)
        self.assertEqual(totals["Bob"], 1)
        self.assertEqual(exhausted, 0)

    def test_skips_eliminated(self):
        ballots = [["Alice", "Bob"], ["Alice", "Carol"]]
        totals, exhausted = count_votes(ballots, {"Alice"})
        self.assertEqual(totals["Bob"], 1)
        self.assertEqual(totals["Carol"], 1)

    def test_exhausted_ballot(self):
        ballots = [["Alice"]]
        totals, exhausted = count_votes(ballots, {"Alice"})
        self.assertEqual(exhausted, 1)
        self.assertEqual(sum(totals.values()), 0)


class TestRunStv(unittest.TestCase):
    def _run(self, ballots):
        with patch("sys.stdout", new_callable=StringIO):
            return run_stv(ballots)

    def test_clear_majority_round_one(self):
        ballots = [
            ["Alice", "Bob"],
            ["Alice", "Bob"],
            ["Bob", "Alice"],
        ]
        self.assertEqual(self._run(ballots), "Alice")

    def test_winner_after_elimination(self):
        # Bob is eliminated in round 1; his vote transfers to Alice giving her majority
        ballots = [
            ["Alice", "Bob"],
            ["Alice", "Bob"],
            ["Bob", "Alice"],
            ["Carol", "Alice"],
            ["Carol", "Alice"],
        ]
        # Round 1: Alice 2, Carol 2, Bob 1 — Bob eliminated
        # Round 2: Alice 3, Carol 2 — Alice wins
        self.assertEqual(self._run(ballots), "Alice")

    def test_redistribution(self):
        # Carol has 1 vote and is eliminated; her voter prefers Bob, giving Bob majority
        ballots = [
            ["Alice", "Carol"],
            ["Alice", "Carol"],
            ["Bob", "Carol"],
            ["Bob", "Carol"],
            ["Carol", "Bob"],
        ]
        # Round 1: Alice 2, Bob 2, Carol 1 — Carol eliminated
        # Round 2: Alice 2, Bob 3 — Bob wins
        self.assertEqual(self._run(ballots), "Bob")

    def test_single_candidate(self):
        ballots = [["Alice"], ["Alice"]]
        self.assertEqual(self._run(ballots), "Alice")

    def test_exhausted_ballots_do_not_transfer(self):
        # Carol's single voter only listed Carol; her ballot exhausts on elimination
        ballots = [
            ["Alice", "Bob"],
            ["Alice", "Bob"],
            ["Alice", "Bob"],
            ["Bob", "Alice"],
            ["Bob", "Alice"],
            ["Carol"],
        ]
        # Round 1: Alice 3, Bob 2, Carol 1 — Carol eliminated, her ballot exhausts
        # Round 2: Alice 3, Bob 2 — Alice wins (exhausted ballot not transferred)
        self.assertEqual(self._run(ballots), "Alice")

    def test_tie_returns_none(self):
        # Alice and Bob are exactly tied; no winner, returning officer needed
        ballots = [
            ["Alice", "Bob"],
            ["Bob", "Alice"],
        ]
        self.assertIsNone(self._run(ballots))

    def test_tie_message_printed(self):
        ballots = [
            ["Alice", "Bob"],
            ["Bob", "Alice"],
        ]
        with patch("sys.stdout", new_callable=StringIO) as mock_out:
            run_stv(ballots)
            self.assertIn("TIE", mock_out.getvalue())

    def test_no_candidates(self):
        self.assertIsNone(self._run([]))


if __name__ == "__main__":
    unittest.main()
