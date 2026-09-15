---
name: casual-style-zach-voice
description: "How Zach writes when he says \"make it casual\" / \"match my style\" -- with a verbatim before/after pair from a 2026-08-21 SpiderRock message"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 8623b7c8-b4ff-4e32-b7c4-642d72f30a5e
  modified: 2026-08-21T13:25:50.699Z
---

When Zach asks for a message in his casual style (vendor support, a colleague, any outbound
note he will send as himself), write it the way he rewrites mine. Supersedes the narrower
[[feedback-support-questions-conversational]] observation, and corrects one detail from it:
that note said he likes a "Quick one on..." opener. He does not -- on 2026-08-21 he cut
exactly that phrase.

**Why:** on 2026-08-21 I drafted a SpiderRock message about the v7-vs-v8 `satm` discrepancy
(see [[spiderrock-v8-migration]]). He kept 100% of the factual scaffolding I built -- both
queries verbatim, the two CT run times, the 3-day number table -- and rewrote everything
around it. The delta is the style lesson, so both versions are recorded below.

**How to apply:**

- **Never write the phrase "quick one".** He stated this flatly on 2026-08-21: "I do not like
  the phrase 'quick one'." Banned everywhere -- drafts he will send, and my own replies to
  him. Same for its cousins as openers ("quick question", "just a quick note", "quick favor").
- **Lead with the plain problem in sentence one.** No warm-up, no framing device, no
  scene-setting about surrounding context. He deleted "Quick one on the v7 -> v8 migration.
  We're running both books in parallel right now, and..." in favor of "I'm seeing different
  behavior pulling atmVol for SPXW 0 day options when I query on v7 versus v8."
- **Cut your own diagnosis.** Give the observation, not the hypothesis. He deleted my entire
  two-sentence analysis paragraph (the stable ~2.2x / ~2.7x ratios, the "doesn't look like a
  units thing", the "v8 barely budges day to day"). Let the vendor investigate; handing them
  a theory narrows what they look at and makes the note longer.
- **Close with why it matters, then ask for the concrete deliverable.** He added "The reason
  this matters to me is I have some trades which are calibrated to this satm value I want to
  make sure I'm able to continue these trades on V8", and asked "Is there a table I can use
  on v8 where the satm value would match" instead of my conceptual "is satm supposed to mean
  the same thing... what should we be reading instead?"
- Smaller tells: first person **"I"**, never "we/us/our". Plain words over jargon with
  outsiders ("0 day options", not "0DTE"). "Hi," / "Thanks, Zach". No dashes used for drama.
  Still true from the older note: drop non-essential sub-questions entirely.

---

**WHAT I WROTE (do not imitate):**

```
Hey -

Quick one on the v7 -> v8 migration. We're running both books in parallel right now, and the
0DTE ATM vol we read off the quote table comes back about half as big on v8 as it does on v7,
every single day. Same query on both sides, only the table name changes.

[queries, CT times, and the 3-day number table -- these he kept unchanged]

We take satm off the first row, so the nearest OTM put. Both scripts run that identical line,
and okey_yr/mn/dy is always the current day since these are 0DTE.

Two things that stood out to us. The ratio is pretty stable at each time of day - roughly 2.2x
at 14:49:55 and 2.7x at 14:54:55 - so it doesn't look like a simple units thing. And the v8
number at 14:54:55 barely budges day to day (0.032, 0.032, 0.034) while v7 moves around with
the tape.

So mainly: is satm supposed to mean the same thing in msgliveimpliedquoteadj as it does in
msgoptionimpliedquote? And if not, what should we be reading instead for a 0DTE ATM vol on v8?

Thanks,
Zach
```

**WHAT HE SENT (imitate this):**

```
Hi,

I'm seeing different behavior pulling atmVol for SPXW 0 day options when I query on v7 versus
v8. Here's what I am querying:

[same two query blocks]

I then take the "satm" value off the first row these queries return. And okey_yr/mn/dy is
always the current day (I made it 8/20/26 in my example).

I run it twice each afternoon, at the following times:

  14:49:55 CT
  14:54:55 CT

Here's what satm comes back as, v7 vs v8, over the last 3 days:

[same number table]

So it seems like I am pulling different values from the two different table on v7 vs v8. Is
that expected? Is there a table I can use on v8 where the "satm" value would match what I am
pulling from v7 for the 0 day options around the end of the day? The reason this matters to me
is I have some trades which are calibrated to this "satm" value I want to make sure I'm able to
continue these trades on V8.
Thanks,
Zach
```

Note he leaves small imperfections in ("the two different table", no blank line before
"Thanks") -- do not over-polish a message meant to sound like him.
