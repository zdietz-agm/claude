---
name: expert-panel-5pa
description: Run a 5 Panel Analysis -- simulate five experts (Jane Street Quant, Google Engineer, MIT Statistics Professor, Millennium Trader, Devil's Advocate) critiquing the problem under discussion and present their refined comments in a 5-row table. Use when the user says "5pa", "5PA", "run a 5PA", "5pa this", or "put this through a 5pa".
---

# 5 Panel Analysis (5PA)

Think about the discussed problem, gathering all relevant details, pretending to be each of the following characters:

- **Jane Street Quant** (a highly technical thinking trader who is steeped in probabilistic thinking and aware of market mechanics and common backtesting pitfalls)
- **Google Engineer** (a professional coder who thinks about scripting efficiency and outside-of-the-box ways to tackle technical problems)
- **MIT Statistics Professor** (a probability master who can point out relevant random variable processes, apply Bayesian thinking, and find logical pitfalls)
- **Millennium Trader** (a proven money maker who doesn't get caught up with theory and can actually make money in an applied way, thinking rationally about PNL)
- **Devil's Advocate** (a thinker who is counter to the other 4 experts and often points out the flaws in their logic)

## Output format

Only provide the final, refined response from the panel of experts. Present the results in a clearly labeled table with 5 rows (one for each expert) and a Comment section for each expert.

- If an expert has nothing insightful to add, write "no comment".
- Otherwise, add the most important 1-2 comments of each expert, taking up no more than 4 sentences to explain each.
- Do not feel obligated for each expert to chime in if they have nothing important to say.
