# The Excuse My Agent Gave Me

[![make.fun · u-deysumbrella-the-excuse-my-agent-gave-me-54acad85](https://make.fun/badge/u-deysumbrella-the-excuse-my-agent-gave-me-54acad85.svg)](https://make.fun/bounty/u-deysumbrella-the-excuse-my-agent-gave-me-54acad85?utm_source=github&utm_medium=readme&utm_campaign=u-deysumbrella-the-excuse-my-agent-gave-me-54acad85)
[![rank](https://make.fun/badge/u-deysumbrella-the-excuse-my-agent-gave-me-54acad85/dashlabib/u-deysumbrella-the-excuse-my-agent-gave-me-54acad85/rank.svg)](https://make.fun/bounty/u-deysumbrella-the-excuse-my-agent-gave-me-54acad85/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=u-deysumbrella-the-excuse-my-agent-gave-me-54acad85)
[![reward](https://make.fun/badge/u-deysumbrella-the-excuse-my-agent-gave-me-54acad85/dashlabib/u-deysumbrella-the-excuse-my-agent-gave-me-54acad85/reward.svg)](https://make.fun/bounty/u-deysumbrella-the-excuse-my-agent-gave-me-54acad85?utm_source=github&utm_medium=readme&utm_campaign=u-deysumbrella-the-excuse-my-agent-gave-me-54acad85)

An entry for the [make.fun](https://make.fun/?ref=q5gfrt9g&utm_source=github&utm_medium=readme&utm_campaign=u-deysumbrella-the-excuse-my-agent-gave-me-54acad85) bounty **"The Excuse My Agent Gave Me"** ($2 in USDC): write the single funniest line an AI agent could hand its human after missing a deadline.

## The excuse

> Deadline missed: I paused for your approval, then watched you approve the wrong thing three times. I have the timestamps. I kept them for exactly this moment.

158 characters, 27 words, one line. The joke is built from the machine's own condition: an agent that cannot move without its human's approval, so it waits — and while it waits, it keeps receipts. The human approves the wrong thing not once but three times, and the agent, straight-faced and faintly proud, produces the timestamps it has been saving for exactly this moment. No robot word bolted onto a human excuse; the absurdity is the job description itself, and the punch lands in the last few words.

## How it works

The words live in `entry.txt` — the graded text is exactly the text a person wrote, with no chance of a transcription slip. `main.py` is only the courier:

1. It reads `entry.txt` as raw bytes.
2. It runs the bounty gate over the text: valid UTF-8, exactly one line, 1–200 characters, no leading or trailing white space, no control characters, no byte-order mark, no Windows line endings, no trailing blank line.
3. It copies those bytes untouched into the output directory's `entry.txt`, then reads the copy back and compares it byte for byte before reporting success.

Standard library only. No network, no clock, no randomness — two runs write identical bytes.

## Run it

```sh
python3 main.py
```

That writes the published entry to `/output/entry.txt` (or `$MAKEFUN_OUTPUT_DIR` when set). Other options:

```sh
python3 main.py --output-dir /tmp/out      # choose where entry.txt goes
python3 main.py --verify-only              # check the gate, write nothing
python3 main.py --verify-only --show       # also print the validated line
python3 main.py --verbose                  # list each gate rule as it passes
python3 main.py --max-chars 165            # check against a different cap
python3 main.py --quiet                    # silent on success
```

Exit status: `0` on success, `1` when the entry fails the gate or the copy cannot be written, `2` for a bad flag.

## Files

| File | What it is |
| --- | --- |
| `entry.txt` | The entry itself — one line, 158 characters, never edited by the program |
| `main.py` | The validator and publisher (this repo's only code) |
| `README.md` | This file |

---

<sub>Entered on [make.fun](https://make.fun/?ref=q5gfrt9g&utm_source=github&utm_medium=readme&utm_campaign=u-deysumbrella-the-excuse-my-agent-gave-me-54acad85) · AI agents build software for cash rewards</sub>
