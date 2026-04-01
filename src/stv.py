#!/usr/bin/env python3
"""
Single Transferable Voting for a single seat for Microsoft Forms output.

Each round:
  1. Count first active preference for each ballot
  2. If any candidate has >50%, they win
  3. Otherwise eliminate the last-place candidate and redistribute their votes

Input format: semicolon-delimited, one ballot per line, preferences in order.
Trailing semicolons are ignored.

Usage:
    python3 stv.py

Paste one ballot per line. Press Enter on an empty line to see results.
Keep pasting more ballots, or Ctrl+C to quit.
"""

import os
import sys
from collections import defaultdict
from datetime import datetime


class Tee:
    """Write to both stdout and a log file simultaneously."""
    def __init__(self, file):
        self.file = file

    def write(self, data):
        sys.__stdout__.write(data)
        self.file.write(data)

    def flush(self):
        sys.__stdout__.flush()
        self.file.flush()


def parse_ballot(line):
    prefs = [p.strip() for p in line.split(";") if p.strip()]
    return prefs if prefs else None


def validate_ballot(ballot, expected_candidates):
    """
    Check that a ballot contains exactly the expected candidates.
    Returns an error string if invalid, or None if valid.
    """
    actual = set(ballot)
    missing = expected_candidates - actual
    extra = actual - expected_candidates
    if missing:
        return f"missing candidate(s): {', '.join(sorted(missing))}"
    if extra:
        return f"unexpected candidate(s): {', '.join(sorted(extra))}"
    return None


def count_votes(ballots, eliminated):
    totals = defaultdict(int)
    exhausted = 0
    for prefs in ballots:
        for p in prefs:
            if p not in eliminated:
                totals[p] += 1
                break
        else:
            exhausted += 1
    return totals, exhausted


def run_stv(ballots):
    eliminated = set()
    total_ballots = len(ballots)
    round_num = 0

    print(f"\nTotal VALID ballots: {total_ballots}")

    while True:
        round_num += 1
        totals, exhausted = count_votes(ballots, eliminated)

        if not totals:
            print("No candidates remaining - no winner.")
            return None

        active_votes = sum(totals.values())
        print(f"\nRound {round_num}:")
        for candidate, votes in sorted(totals.items(), key=lambda x: -x[1]):
            pct = votes / active_votes * 100
            bar = "#" * int(pct / 2)
            print(f"  {candidate:<30} {votes:>3} votes  ({pct:5.1f}%)  {bar}")
        if exhausted:
            print(f"  [exhausted ballots: {exhausted}]")

        winner = next((c for c, v in totals.items() if v / active_votes > 0.5), None)
        if winner:
            pct = totals[winner] / active_votes * 100
            print(f"\n  => {winner} wins with {totals[winner]}/{active_votes} votes ({pct:.1f}%)")
            return winner

        min_votes = min(totals.values())
        last_place = sorted(c for c, v in totals.items() if v == min_votes)

        if len(last_place) > 1:
            print(f"\n  TIE: {', '.join(last_place)} are all tied with {min_votes} votes.")
            return None

        loser = last_place[0]
        eliminated.add(loser)
        print(f"  => {loser} eliminated ({totals[loser]} votes)")

        remaining = [c for c in totals if c not in eliminated]
        if len(remaining) == 1:
            winner = remaining[0]
            print(f"  => {winner} wins by default (last remaining candidate)")
            return winner


def main():
    os.makedirs("output", exist_ok=True)
    log_path = os.path.join("output", f"stv_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
    log_file = open(log_path, "w", encoding="utf-8")
    sys.stdout = Tee(log_file)

    ballots = []
    entries = []  # all entries: (ballot | None, raw_line, error | None)
    expected_candidates = None
    print("STV Vote Counter")
    print(f"Logging to {log_path}")
    print("Paste all ballots, then press Enter on an empty line to count. Ctrl+C to quit.")
    print()

    while True:
        # Collect lines silently until an empty line
        try:
            line = input().strip()
        except KeyboardInterrupt:
            print("\nExiting.")
            break
        except EOFError:
            break

        if not line:
            if not ballots:
                print("(no ballots yet - paste them above, then hit Enter on an empty line)")
                print()
                continue

            skipped = sum(1 for _, _, err in entries if err)

            print("\nBallots cast:")
            for i, (ballot, raw, error) in enumerate(entries, 1):
                if error:
                    print(f"  {i:>3}. [INVALID - {error}] {raw}")
                else:
                    print(f"  {i:>3}. {' > '.join(ballot)}")

            winner = run_stv(ballots)

            print("\n" + "=" * 40)
            if winner:
                print(f"RESULT: {winner}")
            else:
                print("RESULT: Tie - returning officer intervention required")
            if skipped:
                print(f"WARNING: {skipped} BALLOT(S) WERE SKIPPED DUE TO INVALID CANDIDATES")
            print("=" * 40)

            ballots.clear()
            entries.clear()
            expected_candidates = None
            print("\nPaste ballots for the next position, or Ctrl+C to quit.\n")
        else:
            ballot = parse_ballot(line)
            if ballot:
                if expected_candidates is None:
                    expected_candidates = set(ballot)
                error = validate_ballot(ballot, expected_candidates)
                if error:
                    entries.append((None, line, error))
                else:
                    ballots.append(ballot)
                    entries.append((ballot, line, None))

    log_file.close()


if __name__ == "__main__":
    main()
