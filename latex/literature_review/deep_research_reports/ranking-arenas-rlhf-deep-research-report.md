# Background Literature for PCG Arena: Pairwise Ranking Systems, Online Preference Arenas, RLHF, and DPO

## Executive summary

Your thesis centers on a web-based “arena” that collects blind pairwise preferences (A/B votes), aggregates them into an uncertainty-aware global ranking (Glicko-2), and then reuses the resulting preference signal (plus synthetic “judge” preferences) to train a procedural generator via DPO. The most relevant non-PCG background literature therefore falls into four tightly coupled threads.

First, there is a deep measurement tradition on how to convert subjective pairwise judgments into a latent scale, starting with early psychometrics (Thurstone) and formal statistical paired-comparison models (Bradley–Terry). citeturn1search0turn6search0

Second, there are practical skill rating systems (Elo, Glicko, Glicko-2, TrueSkill) that operationalize paired comparisons as online updates, along with explicit uncertainty representations (RD, volatility, Bayesian posteriors) and matchmaking implications. citeturn0search0turn0search1turn0search2turn0search3

Third, there is research on how to choose which pairs to compare next to maximize learning efficiency—directly relevant to your adaptive matchmaking (AGIS). This includes adaptive paired-comparison experimental design (explicitly based on information gain / KL divergence), active ranking from pairwise comparisons, and dueling bandits. citeturn6search2turn4search14turn4search4

Fourth, there is the modern “preference optimization” lineage: RLHF (preferences → reward model → policy optimization) and direct preference fine-tuning methods such as DPO (preferences → direct policy optimization without explicit RL). These works provide the conceptual justification for treating “levels as sequences,” “players as preference labelers,” and your learned or heuristic judge as a scalable substitute for additional human comparisons. citeturn2search4turn2search6turn2search7

Because your platform recruits participants online and collects telemetry, one additional “worth adding” background cluster is ethics and data-quality literature for online experiments and crowdsourced judgments. This is not optional in many thesis review contexts: it helps you justify consent choices, risks, and the validity of non-expert votes. citeturn6search3turn8search3turn10view1

## Paired-comparison measurement foundations

Title: A Law of Comparative Judgment  
URL: `https://anishathalye.com/_next/static/files/cd2730840d0ce25fd4a179d8835c1aca/thurstone1927.pdf` citeturn1search0  
Summary: This classic paper by entity["people","L. L. Thurstone","psychometrician"] formalizes how comparative judgments (e.g., “A is better than B”) can be modeled as noisy observations of underlying latent psychological values. The key contribution is turning pairwise preferences into an interval-like scale under distributional assumptions, connecting observed choice proportions to latent distances. In contemporary terms, Thurstone scaling is one of the earliest, most cited theoretical justifications for using pairwise judgments instead of absolute ratings when the construct is subjective and hard to anchor. citeturn1search0  
How to use it in your thesis: Cite this in “Human evaluation methods” to justify why pairwise comparisons are a principled measurement tool (not merely a convenience UI choice). It supports the claim that pairwise voting reduces scale interpretation problems that plague absolute ratings, and it provides historical grounding for converting many A/B votes into a global ordering. citeturn1search0  
Suggested APA citation (copy/paste):  
```text
Thurstone, L. L. (1927). A law of comparative judgment. Psychological Review, 34(4), 273–286.
```  
citeturn1search0

Title: Rank Analysis of Incomplete Block Designs: I. The Method of Paired Comparisons  
URL: `https://academic.oup.com/biomet/article-abstract/39/3-4/324/326091` citeturn6search0  
Summary: This Biometrika paper by Bradley and Terry introduces what is now widely known as the Bradley–Terry model: a logistic paired-comparison model where each item i has a latent “ability” parameter, and the probability that i beats j is a logistic function of the ability difference. The model’s lasting value is that it gives a clean statistical bridge from “who won each comparison” to “global scores/rankings,” enabling maximum likelihood estimation, uncertainty estimates, and extensions (ties, time dynamics, hierarchies). citeturn6search0turn6search1  
How to use it in your thesis: Use it to strengthen the statistical foundations of your arena: Elo/Glicko-like systems can be explained as practical online approximations to paired-comparison latent-variable models. This also helps when you discuss limitations: simple rating systems assume a mostly-transitive latent scale; cycles (“rock-paper-scissors”) are possible and that’s where matrix views or richer models become relevant. citeturn6search0  
Suggested APA citation (copy/paste):  
```text
Bradley, R. A., & Terry, M. E. (1952). Rank analysis of incomplete block designs: I. The method of paired comparisons. Biometrika, 39(3–4), 324–345. https://doi.org/10.1093/biomet/39.3-4.324
```  
citeturn6search0

## Skill rating systems for pairwise outcomes and uncertainty

Title: The Rating of Chessplayers, Past and Present  
URL: `https://gwern.net/doc/statistics/order/comparison/1978-elo-theratingofchessplayerspastandpresent.pdf` citeturn0search0  
Summary: entity["people","Arpad Elo","chess rating inventor"]’s book is the canonical origin of the Elo rating method. It explains the foundational assumptions: player performance is modeled probabilistically (often with a normal/logistic approximation), expected score depends on rating difference, and ratings are updated proportionally to the surprise (actual minus expected outcome), scaled by a step-size factor (K). Beyond chess, the book is historically important because it established ratings as an operational, continuously updated statistical estimator rather than a static league table. citeturn0search0  
How to use it in your thesis: Cite Elo to introduce the core “pairwise results → ratings → expected win probability” idea that later arena systems adopt. In your context, generators play “matches” via human preference votes; Elo is the conceptual baseline against which you motivate switching to Glicko-2 for uncertainty and faster convergence properties. citeturn0search0  
Suggested APA citation (copy/paste):  
```text
Elo, A. E. (1978). The rating of chessplayers, past and present. Arco Publishing.
```  
citeturn0search0

Title: The Glicko System  
URL: `https://www.glicko.net/glicko/glicko.pdf` citeturn0search1  
Summary: This technical note by entity["people","Mark E. Glickman","statistician glicko"] introduces the Glicko system as a response to a “deficiency in the Elo system,” and explicitly frames Glicko as derived from a statistical model for game outcomes with mathematical approximations for computational simplicity. The central addition is Rating Deviation (RD), an uncertainty term that down-weights unreliable opponents and rises with inactivity, allowing rating uncertainty to be tracked rather than implicitly assumed. citeturn0search1  
How to use it in your thesis: Use this to justify that “uncertainty-aware ranking” is not an ad hoc engineering choice but a statistically motivated refinement of Elo. This paper is also useful when you need to explain RD intuitively (new generators have high RD; after many votes RD falls; after long inactivity RD rises). citeturn0search1  
Suggested APA citation (copy/paste):  
```text
Glickman, M. E. (1995). The Glicko rating system. Boston University (technical report). https://www.glicko.net/glicko/glicko.pdf
```  
citeturn0search1

Title: Parameter Estimation in Large Dynamic Paired Comparison Experiments  
URL: `https://www.glicko.net/research/glicko.pdf` citeturn3search2  
Summary: This journal-style paper places Glicko on a clearer statistical footing: it formulates a dynamic paired-comparison model (skills change over time), proposes a computationally simple updating algorithm, and emphasizes that incorporating uncertainty in parameter estimates improves upon Elo-like updates. The paper is important for thesis rigor because it is closer to a peer-reviewed “primary source” explanation of why Glicko-type systems are statistically motivated and how parameters can be estimated for large populations with changing skills. citeturn3search2turn3search6  
How to use it in your thesis: Cite this when you want to be explicit that your platform’s ranking is a statistical inference procedure under a paired-comparison model with time dynamics. It also strengthens your “matchmaking needs uncertainty” narrative: if you track and exploit uncertainty, you can decide which match-ups are informationally valuable. citeturn3search2turn3search6  
Suggested APA citation (copy/paste):  
```text
Glickman, M. E. (1999). Parameter estimation in large dynamic paired comparison experiments. Journal of the Royal Statistical Society: Series C (Applied Statistics), 48(3), 377–394.
```  
citeturn3search2turn3search6

Title: Example of the Glicko-2 System  
URL: `https://www.glicko.net/glicko/glicko2.pdf` citeturn0search2  
Summary: This document defines the operational Glicko-2 system used widely in practice. It introduces volatility (σ) in addition to rating and RD, and it provides the scale conversion constants and worked examples. A notable practical guideline is that Glicko-2 “works best” when the number of games per rating period is “moderate to large,” with a rule-of-thumb average of about 10–15 games per player per rating period. citeturn0search2  
How to use it in your thesis: This is your key “methodology citation” for implementing Glicko-2 correctly and explaining what μ, RD, and σ mean. It also gives you a principled justification for your rating-period choices (or for using per-battle rating periods) and for interpreting confidence intervals from RD. If your committee questions why you add RD bounds or volatility bounds, you can motivate those as practical stabilizers around the standard formulation. citeturn0search2  
Suggested APA citation (copy/paste):  
```text
Glickman, M. E. (2012). Example of the Glicko-2 system. Boston University. https://www.glicko.net/glicko/glicko2.pdf
```  
citeturn0search2

Title: TrueSkill: A Bayesian Skill Rating System  
URL: `https://papers.neurips.cc/paper/3079-trueskilltm-a-bayesian-skill-rating-system.pdf` citeturn0search3  
Summary: This NeurIPS paper by entity["people","Ralf Herbrich","trueskill author"], entity["people","Tom Minka","trueskill author"], and entity["people","Thore Graepel","trueskill author"] introduces TrueSkill, a Bayesian rating system designed to handle cases that strain Elo/Glicko: team games, more than two competitors, and ranking outcomes beyond winner/loser. It models skill as a distribution and uses factor-graph inference for tractable updates. TrueSkill is relevant because it clarifies what rating systems are “really doing”: approximate Bayesian inference over latent skills. citeturn0search3turn0search15  
How to use it in your thesis: TrueSkill is valuable as “related alternatives.” It helps you argue that you selected Glicko-2 because your arena is primarily pairwise (A/B) and you want an uncertainty parameter, but you are aware of Bayesian generalizations. If reviewers ask “why not TrueSkill,” you can answer that your match structure is strictly pairwise and Glicko-2 is simpler, but TrueSkill frames the broader family of Bayesian skill estimation methods and could be a future extension if you add multi-level comparisons or multi-generator tournaments. citeturn0search3turn0search15  
Suggested APA citation (copy/paste):  
```text
Herbrich, R., Minka, T., & Graepel, T. (2006). TrueSkill: A Bayesian skill rating system. In Advances in Neural Information Processing Systems (NeurIPS).
```  
citeturn0search3turn0search15

## Adaptive pairing, matchmaking, and information gain for ranking

Title: Adaptive Paired Comparison Design  
URL: `https://faculty.wharton.upenn.edu/wp-content/uploads/2012/04/Shanejensen.tourney05.pdf` citeturn6search2  
Summary: This paper by Mark Glickman and entity["people","Shane T. Jensen","statistician"] addresses a problem extremely close to your AGIS motivation: how to decide which pairs to compare so that you learn rankings efficiently. It formalizes pairing as Bayesian optimal experimental design under a paired-comparison outcome model and develops a pairing method that maximizes the expected gain in information (described in terms of KL divergence from prior to posterior) subject to tournament-style constraints. citeturn6search2turn6search17  
How to use it in your thesis: This is arguably the single most on-point “theory anchor” for AGIS. It gives you language and credibility for phrases like “maximize information gain,” “optimal pairing,” and “efficient convergence,” and it provides a canonical justification for using uncertainty plus expected informativeness to schedule comparisons. You can cite it as a direct antecedent and then position AGIS as your platform-specific instantiation (with coverage constraints, similarity weights, and practical heuristics). citeturn6search2turn6search17  
Suggested APA citation (copy/paste):  
```text
Glickman, M. E., & Jensen, S. T. (2005). Adaptive paired comparison design. Journal of Statistical Planning and Inference, 127(1–2), 279–293. https://doi.org/10.1016/j.jspi.2003.09.022
```  
citeturn6search2turn6search17

Title: Active Ranking Using Pairwise Comparisons  
URL: `https://home.ipipan.waw.pl/j.mielniczuk/active-ranking-using-pairwise-comparisons_2011.pdf` citeturn4search14  
Summary: This paper studies the sample complexity of identifying an unknown ranking using pairwise comparisons and proposes active strategies that can reduce the number of required comparisons relative to naive approaches. It frames ranking as an algorithmic problem (not only a statistical estimation problem): which comparisons should you request next, and how many do you need to infer the sorted order reliably? citeturn4search14  
How to use it in your thesis: Use this to justify why adaptive selection matters computationally and statistically. It provides a “computer science flavored” complement to Glickman & Jensen’s Bayesian design framing, and it helps you motivate design goals like minimizing the number of battles required for stable generator rankings in an online setting with limited user attention. citeturn4search14  
Suggested APA citation (copy/paste):  
```text
Jamieson, K. G., & Nowak, R. D. (2011). Active ranking using pairwise comparisons. In Advances in Neural Information Processing Systems (NeurIPS).
```  
citeturn4search14

Title: The K-Armed Dueling Bandits Problem  
URL: `https://www.sciencedirect.com/science/article/pii/S0022000012000281` citeturn4search4  
Summary: This paper formulates “dueling bandits,” where only relative feedback between two chosen actions is observed (“which one is better?”) rather than absolute numeric rewards. The key conceptual link is that dueling bandits formalize the exploration–exploitation tradeoff when comparisons are noisy and expensive: you must choose which pairs to compare to quickly identify strong options. citeturn4search4turn4search16  
How to use it in your thesis: Your arena is a dueling-bandit-like environment at the meta level: the system chooses two generators (arms), gets a noisy binary signal (vote), and seeks to infer a global ranking. This paper gives you principled vocabulary for why “random pairing” is statistically wasteful, and it can justify AGIS-like selection rules as heuristic approximations of more formal regret-minimizing strategies. citeturn4search4turn4search16  
Suggested APA citation (copy/paste):  
```text
Yue, Y., Broder, J., Kleinberg, R., & Joachims, T. (2012). The k-armed dueling bandits problem. Journal of Computer and System Sciences, 78(5), 1538–1556.
```  
citeturn4search4turn4search16

Title: Active Sampling for Pairwise Comparisons via Approximate Message Passing and Information Gain Maximization  
URL: `https://arxiv.org/abs/2004.05691` citeturn4search1  
Summary: This paper proposes an active sampling method for pairwise comparisons that explicitly uses expected information gain to pick informative pairs, motivated by the high “cost per comparison” in many human judgment settings (e.g., video quality comparisons). It is notable for emphasizing full posterior updates (approximate message passing) and batch selection strategies aimed at computational tractability, plus it reports an open-source GPU implementation. citeturn4search1  
How to use it in your thesis: This is a strong “modern” reference to support the claim that information-gain-based pair selection is a current active research topic in human judgment experiments. It can strengthen the argument that AGIS is aligned with state-of-the-art principles even if its mechanics are simpler and tailored to your web platform constraints. citeturn4search1  
Suggested APA citation (copy/paste):  
```text
Mikhailiuk, A., Wilmot, C., Perez-Ortiz, M., Yue, D., & Mantiuk, R. (2020). Active sampling for pairwise comparisons via approximate message passing and information gain maximization. arXiv:2004.05691.
```  
citeturn4search1

## Online A/B testing methodology, crowdsourced arenas, and ethics

Title: Online Controlled Experiments at Large Scale  
URL: `https://chbrown.github.io/kdd-2013-usb/kdd/p1168.pdf` citeturn6search3  
Summary: This KDD paper by Kohavi and collaborators is a cornerstone reference for rigorous large-scale A/B testing. It catalogs the practical challenges of running controlled experiments in production, grouping them into cultural/organizational, engineering, and trustworthiness dimensions. It also emphasizes power/sensitivity realities (small detectable effects require very large user counts) and explains why negative results are still valuable. citeturn6search3turn6search14  
How to use it in your thesis: Cite this when framing PCG Arena as a production-like online experimentation platform rather than a one-off lab study. It supports discussions like “why web deployment matters,” “why scale improves statistical power,” and “why instrumentation and trustworthiness are core to your architecture.” citeturn6search3turn6search14  
Suggested APA citation (copy/paste):  
```text
Kohavi, R., Deng, A., Frasca, B., Walker, T., Xu, Y., & Pohlmann, N. (2013). Online controlled experiments at large scale. In Proceedings of the ACM SIGKDD International Conference on Knowledge Discovery and Data Mining (KDD).
```  
citeturn6search3turn6search14

Title: Chatbot Arena: An Open Platform for Evaluating LLMs by Human Preference  
URL: `https://arxiv.org/abs/2403.04132` citeturn3search0  
Summary: This paper describes a real-world, high-traffic “arena” for blind pairwise comparisons, collecting crowdsourced votes to rank models. It reports operating at large scale (on the order of hundreds of thousands of votes) and explains the statistical methodology used for evaluation and ranking, while also analyzing data quality (agreement between crowd votes and expert votes) and question diversity. citeturn3search0turn3search4  
How to use it in your thesis: This is arguably the closest “systems analog” to PCG Arena outside games. You can use it to argue that anonymous head-to-head battles plus rating-based leaderboards are a validated pattern for evaluating generative systems when absolute metrics are insufficient. It also gives you credible precedent for discussion of vote quality, bias mitigation, and why open arenas can become reference leaderboards. citeturn3search0turn3search4  
Suggested APA citation (copy/paste):  
```text
Chiang, W.-L., Zheng, L., Sheng, Y., Angelopoulos, A. N., Li, T., Li, D., Zhang, H., Zhu, B., Jordan, M. I., Gonzalez, J. E., & Stoica, I. (2024). Chatbot Arena: An open platform for evaluating LLMs by human preference. arXiv:2403.04132.
```  
citeturn3search0turn3search4

Title: Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena  
URL: `https://arxiv.org/abs/2306.05685` citeturn3search1  
Summary: This paper is relevant because it studies the reliability and biases of using strong models as automated judges for evaluating other models, and it connects that evaluation methodology to a human-preference arena dataset. It identifies several systematic biases (e.g., position, verbosity, self-enhancement) and proposes mitigation strategies, while also reporting agreement rates between strong LLM judges and human evaluations in certain settings. citeturn3search5turn3search13  
How to use it in your thesis: You can use this in two ways. First, as a cautionary reference: if you ever replace human votes with automated judging (or add an “AI vote” channel), you must analyze judge bias. Second, as a forward-looking extension of your “Judge Function”: your thesis already uses a heuristic/synthetic judge idea for scalable preference data; this paper gives you modern terminology (“LLM-as-a-judge”) and an evaluation playbook for validating judge reliability against human votes. citeturn3search5turn3search13  
Suggested APA citation (copy/paste):  
```text
Zheng, L., Chiang, W.-L., Sheng, Y., Zhuang, S., Wu, Z., Zhuang, Y., Lin, Z., Li, Z., Li, D., & Stoica, I. (2023). Judging LLM-as-a-judge with MT-Bench and Chatbot Arena. arXiv:2306.05685.
```  
citeturn3search5turn3search13

Title: Engagement Effects of Player Rating System-Based Matchmaking for Level Ordering in Human Computation Games  
URL: `https://dl.acm.org/doi/pdf/10.1145/3102071.3102093` citeturn4search19  
Summary: This paper studies how rating-system-driven matchmaking can affect player engagement in human computation games, and it explicitly uses Glicko-2 as part of matching players and tasks/levels. It is a rare direct bridge between (a) rating systems, (b) adaptive task selection, and (c) human participation/engagement—exactly the triad your platform must manage. citeturn4search19turn4search12  
How to use it in your thesis: Use this as domain-adjacent precedent that rating-based matchmaking can serve a dual purpose: improving measurement quality and maintaining engagement. This supports your claim that matchmaking is not just a ranking accelerant but can be part of a “healthy experiment design” that avoids repetitive, demotivating match-ups. citeturn4search19turn4search12  
Suggested APA citation (copy/paste):  
```text
Sarkar, A., Cooper, S., & Kan, E. (2017). Engagement effects of player rating system-based matchmaking for level ordering in human computation games. In Proceedings of the Foundations of Digital Games (FDG).
```  
citeturn4search19

Title: Cheap and Fast—But Is It Good? Evaluating Non-Expert Annotations for Natural Language Tasks  
URL: `https://ai.stanford.edu/~rion/papers/amt_emnlp08.pdf` citeturn8search0  
Summary: This paper evaluates whether crowdsourced non-expert labels can match expert annotation quality, across multiple tasks, using Amazon Mechanical Turk. It is widely cited because it provides empirical evidence that non-expert judgments—when aggregated correctly—can yield high-quality supervision while drastically reducing cost and time. citeturn8search0turn8search4  
How to use it in your thesis: Your platform’s votes are essentially “crowdsourced labels” about which generator output is better. This paper helps you defend the legitimacy of non-expert player preferences as a data source, especially if you include basic quality controls (e.g., minimum playtime, consistency checks, bot prevention, repeated comparisons, or uncertainty-aware rating). citeturn8search0turn8search4  
Suggested APA citation (copy/paste):  
```text
Snow, R., O’Connor, B., Jurafsky, D., & Ng, A. (2008). Cheap and fast—But is it good? Evaluating non-expert annotations for natural language tasks. In Proceedings of the Conference on Empirical Methods in Natural Language Processing (EMNLP).
```  
citeturn8search0turn8search4

Title: The Ethics of Online Controlled Experiments (A/B Testing)  
URL: `https://link.springer.com/article/10.1007/s11023-023-09644-y` citeturn8search3  
Summary: This paper presents ethical principles and practical prompting questions for responsible online controlled experiments, motivated by the fact that A/B tests can affect users without their explicit awareness and may impose harms unevenly. It explicitly argues that compliance and governance are non-trivial and cannot be solved by a single mechanism. citeturn8search3turn8search7  
How to use it in your thesis: PCG Arena is an online experiment system: you collect human data, influence user experience (level difficulty, frustration), and potentially expose participants to risk (e.g., negative experiences, privacy issues). This paper gives you academic grounding for a short “Ethics and responsible experimentation” subsection: consent posture, debriefing, opt-out, minimizing harm, and transparency. citeturn8search3  
Suggested APA citation (copy/paste):  
```text
Polonioli, A., & Ghioni, A. (2023). The ethics of online controlled experiments (A/B testing). Minds and Machines, 33, 1–23.
```  
citeturn8search3

Title: Internet Research: Ethical Guidelines 3.0  
URL: `https://aoir.org/reports/ethics3.pdf` citeturn10view1  
Summary: These guidelines (Association of Internet Researchers) provide a structured approach to ethical decision-making for internet-mediated research. They emphasize that ethics involves contextual judgment rather than a fixed recipe, and they include sections that are directly relevant to your work: informed consent, data acquisition/storage, platform considerations, and especially guidance touching on algorithms and machine learning contexts. citeturn10view1  
How to use it in your thesis: This is an excellent “ethics framework” citation for a master’s thesis that runs an online platform. You can cite it when describing how you approached consent, telemetry, data retention, and anonymization, and when justifying design decisions like hiding generator identities (bias reduction) while still protecting participants. citeturn10view1  
Suggested APA citation (copy/paste):  
```text
Franzke, A. S., Bechmann, A., Zimmer, M., Ess, C., & Association of Internet Researchers (AoIR). (2020). Internet research: Ethical guidelines 3.0. https://aoir.org/reports/ethics3.pdf
```  
citeturn10view1

Title: The Belmont Report: Ethical Principles and Guidelines for the Protection of Human Subjects of Research  
URL: `https://www.hhs.gov/ohrp/sites/default/files/the-belmont-report-508c_FINAL.pdf` citeturn8search2  
Summary: The Belmont Report is a foundational statement of three core principles—respect for persons, beneficence, and justice—and applications such as informed consent and risk/benefit assessment. It is not a “methods paper,” but it is routinely cited as the baseline ethical framework for human-subject research. citeturn8search2turn8search18  
How to use it in your thesis: If your thesis must pass formal departmental ethics expectations (even without a full IRB process), Belmont is the most recognizable citation anchor. It can support a concise justification of your consent and privacy posture, telemetry minimization, and participant autonomy (skip votes, withdraw, etc.). citeturn8search2turn8search18  
Suggested APA citation (copy/paste):  
```text
National Commission for the Protection of Human Subjects of Biomedical and Behavioral Research. (1979). The Belmont Report: Ethical principles and guidelines for the protection of human subjects of research. U.S. Department of Health and Human Services.
```  
citeturn8search2turn8search18

## RLHF and preference-based reinforcement learning

Title: Deep Reinforcement Learning from Human Preferences  
URL: `https://papers.neurips.cc/paper/7017-deep-reinforcement-learning-from-human-preferences.pdf` citeturn2search4  
Summary: This NeurIPS paper is the canonical modern RLHF ancestor: it proposes collecting human preference comparisons between short trajectory segments, training a reward model from those comparisons, and then optimizing a policy against the learned reward. It demonstrates that complex behaviors can be learned with relatively small amounts of human feedback by carefully structuring comparisons and iterating reward learning plus policy training. citeturn2search4turn2search0  
How to use it in your thesis: This paper provides the cleanest conceptual bridge between your platform and RLHF: your A/B battles are preference queries; your “Judge Function” is a reward proxy; and your generator training is preference optimization. Even though your domain is PCG rather than control, the preference-learning logic is the same: subjective human judgment is treated as supervision. citeturn2search4  
Suggested APA citation (copy/paste):  
```text
Christiano, P. F., Leike, J., Brown, T. B., Martic, M., Legg, S., & Amodei, D. (2017). Deep reinforcement learning from human preferences. In Advances in Neural Information Processing Systems (NeurIPS).
```  
citeturn2search4

Title: Fine-Tuning Language Models from Human Preferences  
URL: `https://arxiv.org/pdf/1909.08593` citeturn2search5  
Summary: This paper is one of the earliest demonstrations of applying preference-based reward learning and RL fine-tuning to language models. It trains a reward model from human comparisons over model outputs, then uses RL to fine-tune the language model to maximize predicted preference. The paper is also useful for its pragmatic details: preference dataset sizes, task choices, and observed failure modes (e.g., exploiting labeler heuristics). citeturn2search5turn2search1  
How to use it in your thesis: Your “levels as sequences of ASCII characters” approach parallels LM-based generation. This paper helps you justify that preference-based pipelines apply to sequence generation domains, while also giving you a cautionary story: reward models can be gamed, so you should validate your judge signal against actual human votes (which your platform enables). citeturn2search5  
Suggested APA citation (copy/paste):  
```text
Ziegler, D. M., Stiennon, N., Wu, J., Brown, T. B., Radford, A., Amodei, D., Christiano, P., & Irving, G. (2019). Fine-tuning language models from human preferences. arXiv:1909.08593.
```  
citeturn2search5

Title: Learning to Summarize from Human Feedback  
URL: `https://proceedings.neurips.cc/paper/2020/file/1f89885d556929e98d3ef9b86448f951-Paper.pdf` citeturn7search1  
Summary: This paper demonstrates that optimizing directly for human preference can outperform traditional proxy metrics (such as ROUGE) in summarization. It is important because it treats “metric mismatch” as a core motivation for human feedback: automatic metrics are often cheap but misaligned with what humans care about, so preference learning provides a better objective. citeturn7search1turn7search5  
How to use it in your thesis: Your thesis motivation is structurally identical: automated PCG metrics are incomplete proxies for enjoyment, so you build an infrastructure to collect human feedback. This paper gives you a high-impact “outside games” precedent showing that preference optimization can beat metric-optimized systems precisely because the metric is misaligned. citeturn7search1  
Suggested APA citation (copy/paste):  
```text
Stiennon, N., Ouyang, L., Wu, J., Ziegler, D. M., Lowe, R., Voss, C., Radford, A., Amodei, D., & Christiano, P. (2020). Learning to summarize from human feedback. In Advances in Neural Information Processing Systems (NeurIPS).
```  
citeturn7search1

Title: Training Language Models to Follow Instructions with Human Feedback  
URL: `https://cdn.openai.com/papers/Training_language_models_to_follow_instructions_with_human_feedback.pdf` citeturn2search6  
Summary: This widely cited paper (InstructGPT) popularizes the RLHF training recipe in modern LLMs: supervised fine-tuning on demonstrations, collecting rankings of outputs, training a reward model, and RL fine-tuning to maximize the reward. It also reports that a smaller aligned model can be preferred over a larger unaligned model in human evaluations—highlighting the practical value of preference optimization. citeturn2search6turn2search2  
How to use it in your thesis: This paper is a direct “methodology analog” for your Mario-DPO pipeline narrative: SFT on a seed corpus, preference collection (human votes + synthetic judge), and preference-based fine-tuning. It also gives you strong authority for the claim that aligning to human preference can dominate raw likelihood training for subjective quality objectives. citeturn2search6  
Suggested APA citation (copy/paste):  
```text
Ouyang, L., Wu, J., Jiang, X., Almeida, D., Wainwright, C. L., Mishkin, P., Zhang, C., Agarwal, S., Slama, K., Ray, A., Schulman, J., Hilton, J., Kelton, F., Miller, L., Simens, M., Askell, A., Welinder, P., Christiano, P., Leike, J., & Lowe, R. (2022). Training language models to follow instructions with human feedback. In Advances in Neural Information Processing Systems (NeurIPS).
```  
citeturn2search6

Title: Constitutional AI: Harmlessness from AI Feedback  
URL: `https://arxiv.org/pdf/2212.08073` citeturn7search8  
Summary: This paper introduces a scalable alternative to pure RLHF by using AI-generated feedback guided by an explicit “constitution” of principles, reducing reliance on direct human labeling for certain safety-alignment goals. It operationalizes the idea that some preference data can be synthesized or mediated by models, though its own methods still involve careful alignment and evaluation. citeturn7search8turn7search0  
How to use it in your thesis: This is highly relevant to your “RLAIF-style data expansion” claim: you generate synthetic preference pairs from a judge. Constitutional AI gives you a respected precedent for substituting some human feedback with AI-mediated feedback—while also reminding you to validate that synthetic labels don’t drift from real human preferences. citeturn7search8  
Suggested APA citation (copy/paste):  
```text
Bai, Y., Kadavath, S., Kundu, S., Askell, A., Kernion, J., Jones, A., Chen, A., Goldie, A., Mirhoseini, A., McKinnon, C., et al. (2022). Constitutional AI: Harmlessness from AI feedback. arXiv:2212.08073.
```  
citeturn7search8

Title: RLAIF: Scaling Reinforcement Learning from Human Feedback with AI Feedback  
URL: `https://openreview.net/pdf?id=AAxIs3D2ZZ` citeturn7search10  
Summary: This paper studies how AI feedback can scale preference-based alignment when human labels are expensive. It frames RLAIF as addressing the scalability bottleneck of RLHF while still aiming for comparable performance, and it introduces variants that can bypass explicit reward-model training by querying an off-the-shelf judge. citeturn7search10turn7search2  
How to use it in your thesis: If you discuss “synthetic preferences” (judge function, LLM judge, heuristics), this paper helps you position that choice as part of a broader trend: replacing or augmenting human comparisons to scale. It also gives you a vocabulary distinction: human votes are gold labels; judge-derived comparisons are silver labels that require validation. citeturn7search10  
Suggested APA citation (copy/paste):  
```text
Lee, H., et al. (2023). RLAIF: Scaling reinforcement learning from human feedback with AI feedback. OpenReview (ICLR submission). https://openreview.net/pdf?id=AAxIs3D2ZZ
```  
citeturn7search10

Title: Advances in Preference-Based Reinforcement Learning  
URL: `https://arxiv.org/pdf/2408.11943` citeturn7search3  
Summary: This survey synthesizes the state of preference-based reinforcement learning (PbRL), including theoretical guarantees, benchmarking, and recent applications. It is useful because it situates RLHF and its variants as part of a broader scientific area: learning from preference signals instead of scalar rewards. citeturn7search3  
How to use it in your thesis: If your committee expects a “survey anchor” beyond individual RLHF/DPO papers, this provides it. You can use it to justify terminology, to motivate why preference learning is appropriate for subjective constructs (fun, aesthetic quality), and to contextualize limitations (noise, sample efficiency, preference inconsistency). citeturn7search3  
Suggested APA citation (copy/paste):  
```text
Abdelkareem, Y., et al. (2024). Advances in preference-based reinforcement learning. arXiv:2408.11943.
```  
citeturn7search3

## DPO and direct preference fine-tuning

Title: Direct Preference Optimization: Your Language Model Is Secretly a Reward Model  
URL: `https://arxiv.org/pdf/2305.18290` citeturn2search7  
Summary: This paper introduces DPO as a way to optimize a policy to match preferences without explicitly training a reward model and running reinforcement learning in the loop. The key idea is a reparameterization that yields a closed-form relationship between an implicit reward and the optimal policy, allowing preference optimization with a simple classification-style loss over paired preferences between outputs, relative to a reference policy. The paper emphasizes practical benefits: training stability, computational simplicity, and eliminating sampling-in-the-loop complexity typical of RLHF. citeturn2search7turn2search3  
How to use it in your thesis: This is your primary citation for the “Mario-DPO” concept. It justifies treating your preference pairs (human A/B votes + synthesized judge comparisons) as training data for direct optimization of the generator, and it provides the mathematical narrative for why DPO can be interpreted as “the policy already encodes a reward model implicitly.” It also supports an argument for why DPO is engineering-feasible in a master’s scope: fewer moving parts than full RLHF. citeturn2search7  
Suggested APA citation (copy/paste):  
```text
Rafailov, R., Sharma, A., Mitchell, E., Ermon, S., Manning, C. D., & Finn, C. (2023). Direct preference optimization: Your language model is secretly a reward model. In Advances in Neural Information Processing Systems (NeurIPS).
```  
citeturn2search7turn2search11

Title: The Mario AI Benchmark and Competitions  
URL: `https://julian.togelius.com/Karakovskiy2012The.pdf` citeturn9search3  
Summary: This paper (often cited as the “Mario AI Benchmark and Competitions”) describes the benchmark environment, interfaces, and competition design around a Mario-like platformer AI framework. It is relevant here not for PCG itself, but for documenting the engine assumptions and level formats that your platform inherits and ports to the browser. citeturn9search3turn9search0  
How to use it in your thesis: Your draft currently cites “General Video Game Level Generation” in a way that can be misread as the Mario AI framework reference. This paper is the clean primary source for describing the Mario AI benchmark that your engine is derived from and for justifying claims like “faithful physics/format recreation.” It also helps reviewers recognize that your platform is built on a known benchmark lineage, increasing perceived validity. citeturn9search3turn9search0  
Suggested APA citation (copy/paste):  
```text
Karakovskiy, S., & Togelius, J. (2012). The Mario AI benchmark and competitions. IEEE Transactions on Computational Intelligence and AI in Games, 4(1), 55–67.
```  
citeturn9search3turn9search0

Title: Search-Based Procedural Content Generation: A Taxonomy and Survey  
URL: `https://julian.togelius.com/Togelius2011Searchbased.pdf` citeturn9search1  
Summary: This survey formalizes “search-based PCG” as a design space where content is represented explicitly and then optimized via search (evolutionary algorithms, other metaheuristics) against an evaluation function. You do not need this to re-explain PCG, but it is directly relevant to your “Judge Function” section: it frames evaluation functions (fitness) as central and highlights the difficulty of specifying them. citeturn9search1turn9search11  
How to use it in your thesis: Use it to position your Judge Function as a modern, empirically grounded attempt to build a better fitness signal—one derived from human preferences rather than purely hand-engineered structural metrics. That makes your DPO/RLAIF narrative feel like a natural extension of SBPCG evaluation challenges. citeturn9search1  
Suggested APA citation (copy/paste):  
```text
Togelius, J., Yannakakis, G. N., Stanley, K. O., & Browne, C. (2011). Search-based procedural content generation: A taxonomy and survey. IEEE Transactions on Computational Intelligence and AI in Games, 3(3), 172–186.
```  
citeturn9search1turn9search4

## What else from your draft is worth adding to related work

Your draft contains several elements that typically benefit from one or two additional citations each, even if they are “engineering” rather than “algorithm” contributions.

First, your blind A/B arena design closely parallels the architecture of modern model-evaluation leaderboards; the Chatbot Arena paper is your strongest cross-domain precedent, and it makes your project feel less like a one-off website and more like a recognized evaluation paradigm. citeturn3search0turn3search4

Second, your AGIS framing (“optimize information gain”) becomes much more defensible if you cite adaptive paired-comparison design explicitly (Glickman & Jensen) and optionally one active ranking / dueling bandit reference to show the broader algorithmic lineage. citeturn6search2turn4search14turn4search4

Third, because you run online experiments with telemetry, adding one compact ethics subsection is often a “silent requirement” for committees. A minimal but strong citation set is: Kohavi et al. for online experiments at scale, AoIR Ethics guidelines for internet-mediated research ethics structure, and Polonioli & Ghioni for ethical issues specific to A/B testing. citeturn6search3turn10view1turn8search3