# STV Vote Counter

A command-line tool for counting ranked-choice votes using Instant Runoff Voting (also known as Single Transferable Vote for a single seat). Designed for use with **Microsoft Forms** ranking questions.

## How it works

Each round:
1. Count the first active preference on each ballot
2. If any candidate has **more than 50%** of active votes, they win
3. Otherwise, eliminate the last-place candidate and redistribute their ballots to the next preference
4. Repeat until a winner is found

## Requirements

Python 3 (no external dependencies)

## Usage

```
python3 stv.py
```

Paste all ballots, press **Enter on an empty line** to count. You can paste more ballots afterwards and count again. Press **Ctrl+C** to quit.

## Input format

Microsoft Forms exports ranked responses as semicolon-separated values, e.g.:

```
Candidate 2;Candidate 1;Candidate 3;RON;
Candidate 1;Candidate 3;Candidate 2;RON;
RON;Candidate 1;Candidate 2;Candidate 3;
```

Each line is one voter's preferences in order (most preferred first). Trailing semicolons are ignored.

To get this from Microsoft Forms:
1. Open your form results in Excel
2. Find the ranking question column
3. Select and copy all responses
4. Paste directly into the terminal when prompted

## RON (Re-Open Nominations)

If **RON** wins, the result is reported as "position not filled" rather than declaring RON the winner.

## Example output

```
Total ballots: 9

Round 1:
  Candidate 3                    4 votes  (44.4%)  ######################
  Candidate 1                    3 votes  (33.3%)  ################
  Candidate 2                    1 votes  (11.1%)  #####
  RON                            1 votes  (11.1%)  #####
  => Candidate 2 eliminated (1 votes)
  => RON eliminated (1 votes)

Round 2:
  Candidate 3                    5 votes  (55.6%)  ###########################
  Candidate 1                    4 votes  (44.4%)  ######################
  => Candidate 3 wins with 5/9 votes (55.6%)

========================================
RESULT: Candidate 3
========================================
```
