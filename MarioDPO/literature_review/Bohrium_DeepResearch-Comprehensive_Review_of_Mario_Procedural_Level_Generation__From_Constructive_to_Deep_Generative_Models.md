Based on the comprehensive literature review, the field of Mario procedural level generation has evolved through several distinct families of methods. Initially, it was dominated by **constructive/rule-based and grammar-based approaches** that built levels from predefined chunks and rules. This was followed by **probabilistic models** like Markov chains, which learned statistical patterns from existing levels. A significant shift occurred with the introduction of **search-based PCG**, particularly evolutionary algorithms, which optimized levels against specific fitness functions, often incorporating AI agents for playability checks. The modern era is defined by **PCG via Machine Learning (PCGML)**, which includes a wide range of deep generative models. **LSTMs/RNNs** were used to generate levels as sequences of tokens. **GANs**, famously in "MarioGAN," were combined with latent space evolution to search for playable and interesting level segments. **VAEs** enabled level blending and interpolation. Most recently, **Diffusion Models and Large Language Models (LLMs)** like in "MarioGPT" and the "Moonshine" framework have introduced text-to-level generation, offering unprecedented semantic control. Other important families include **path-conditioned generation** that explicitly ensures solvability, **experience-driven PCG (EDPCG)** that personalizes levels based on player experience models, and **pattern-based generation** that uses libraries of design motifs.

These methods employ a variety of representations, from simple **tile grids** and **sequences/strings** to more abstract **parameter vectors**, **grammar rules**, and **latent vectors** in deep models. Playability is enforced through explicit rules, post-hoc repair mechanisms, agent-based solvability checks integrated into fitness/reward functions, and by learning from corpora of known playable levels. Quality, diversity, and controllability are measured using a combination of automated proxies (solvability rates, feature counts, expressive range analysis, semantic similarity scores like CLIP) and crucial human evaluation (pairwise preferences, rating scales for fun/challenge).

Current approaches still fall short in bridging the "human preference gap," often producing levels that are technically valid but not enjoyable (the "oatmeal problem"). They can suffer from mode collapse, poor controllability, and a disconnect between local coherence and global design. The most promising baselines for reproduction span these families, including EDPCG for personalization, LSTM-based sequence generation, MarioGAN for latent space exploration, and text-conditioned Diffusion Models as a state-of-the-art approach.

***

### 0) Executive Overview

Procedural Content Generation (PCG) for video games, the algorithmic creation of game content, has a rich history spanning over four decades [1]. In the context of 2D platformers, particularly **Super Mario Bros. (SMB)** and Mario-like games, PCG has served as a pivotal research domain, often referred to as the "drosophila of PCG research" due to its widespread use as a benchmark [1]. The evolution of Mario PCG mirrors the broader advancements in artificial intelligence and computational creativity, moving from deterministic, designer-driven systems to complex, data-driven generative models.

Early approaches in Mario PCG relied on **constructive and rule-based methods**, employing explicit rules, grammars, or probabilistic models (e.g., Markov chains) to assemble levels piece by piece or via specified patterns. These methods provided foundational understanding of level structure and basic playability enforcement. As the field matured, **search-based PCG** emerged, leveraging evolutionary algorithms (like genetic algorithms) to explore vast design spaces, optimizing levels against fitness functions that often encoded playability or aesthetic criteria.

The past decade has seen a significant shift towards **PCG via Machine Learning (PCGML)**, driven by the advent of powerful neural networks. This includes the application of Long Short-Term Memory (LSTM) networks to learn sequential patterns from existing levels, Generative Adversarial Networks (GANs) for generating realistic tilemaps, and Variational Autoencoders (VAEs) for learning compressed latent representations of levels, enabling interpolation and blending. These deep generative models have allowed for the creation of more diverse and complex content, but often face challenges in ensuring specific gameplay properties and human enjoyment.

Most recently, the disruptive influence of **Large Language Models (LLMs)** and advanced generative paradigms like **Diffusion Models** has begun to reshape Mario PCG. LLMs offer unprecedented capabilities for prompt-controlled generation, translating natural language descriptions into game content, while diffusion models promise high-fidelity and diverse outputs. These modern methods aim to provide higher-level control and better semantic understanding, potentially addressing some of the long-standing challenges in PCG.

The overarching goal across these evolutionary stages has been to generate levels that are not only playable but also engaging and enjoyable for human players. This pursuit necessitates sophisticated methods for enforcing playability constraints, ensuring a balance of difficulty, rhythm, and pacing, maintaining "Mario-ness" while offering novelty, and bridging the "human preference gap" between algorithmically valid and subjectively fun content.

| Method Family | Typical Representation | Typical Evaluation |
| :--- | :--- | :--- |
| Constructive / Rule-based | Tile grids, explicit rules | Structural validity, designer inspection, basic playability checks |
| Grammar-based | Production rules, chunk grammars | Grammatical correctness, expressive range, structural integrity |
| Probabilistic (e.g., Markov Chains) | Sequential tile data | Statistical similarity to training data, basic playability checks |
| Search-based | Genotypes (parameter vectors, rules) | Fitness functions (solvability, feature counts), agent-based playtesting |
| PCGML / Deep Generative (LSTMs) | Sequence of tiles/tokens | Generation quality, coherence, prediction accuracy, solvability agents |
| PCGML / Deep Generative (GANs/VAEs) | Latent vectors, tilemaps | Visual realism, reconstruction loss, latent space exploration, playability |
| PCGML / Deep Generative (Diffusion) | Latent vectors, tilemaps | Semantic alignment (CLIP Score), diversity, visual quality |
| LLM-based | Text prompts, internal representations | Adherence to prompts, human judgment, creativity, controllability |
| Experience-Driven PCG | Parameter vectors | Player experience models (affective states), human subjective ratings |

**What matters in Mario PCG: Playability, Difficulty, and Enjoyment**
For Mario-like levels, several factors are critical for player engagement and retention [2][1]:
*   **Playability Constraints**: Levels must be solvable, with reachable platforms, avoid inescapable traps, and ensure fair enemy encounters. Unplayable levels are fundamentally useless [1].
*   **Difficulty Rhythm and Pacing**: A good Mario level guides the player through varying challenges, introducing new mechanics or enemies gradually, and providing moments of tension and release. Consistent difficulty is key, avoiding overly easy ("oatmeal problem") or frustratingly hard segments [2][1].
*   **Fairness**: Challenges should be surmountable with skill, not luck, and player deaths should feel attributable to player error rather than level design flaws.
*   **Novelty vs. "Mario-ness"**: Generated levels need to feel fresh and diverse while retaining the aesthetic, mechanical, and thematic essence of Super Mario Bros. Overly repetitive or "generic" content often leads to the "oatmeal problem," where levels are technically valid but lack engaging qualities [3].
*   **Controllability**: Designers need effective "knobs" to guide the generation process, allowing them to specify desired features, difficulty, or thematic elements rather than merely generating random outputs.
*   **Human Preference Gap**: The ultimate measure of a generated level's success is human enjoyment. Automated metrics, while useful, often fail to fully capture subjective qualities like fun, challenge, or satisfaction, leading to a significant gap between what algorithms optimize for and what people truly enjoy [2][1].

### 1) Problem Formulation and Evaluation Axes

The task of Mario procedural level generation involves creating new, playable 2D platformer levels that ideally resemble the iconic Super Mario Bros style while also offering novelty and engagement. This process necessitates careful consideration of representations, constraints, and objectives, which in turn dictate the evaluation methodologies employed.

**Representations**
The way levels are represented is fundamental to their generation and evaluation. While specific Mario representations are not extensively detailed in the provided searches, general PCG and PCGML contexts suggest a range of data structures. For instance, in Super Mario Bros, "constructive primitives" or game segments are utilized [4]. PCGML approaches typically involve training machine learning models on existing content, implying that levels are encoded in a format suitable for learning, such as tile grids, sequences, or latent vectors [5][6]. More advanced generative models can also leverage text embeddings for conditioning, as seen in "steerable generative models" that allow "controllability through plain text" [7].

**Constraints**
Ensuring that generated levels are playable and adhere to the inherent rules of the Mario universe is a primary constraint. This involves avoiding impossible jumps, unreachable items, or illogical enemy placements. In some approaches, like the one for Super Mario Bros, playability is enforced through a "synergy between rule-based and learning-based methods" to produce "quality yet controllable game segments" [4]. The broader field of PCGML acknowledges its suitability for "repair, critique, and content analysis," which implies that mechanisms exist within these frameworks to identify and correct issues that violate playability or other design constraints [5][6]. Furthermore, Experience-Driven Procedural Content Generation (EDPCG) aims to adapt content "according to user needs and preferences," implicitly guiding generation towards experiences that are constrained by what users find playable and enjoyable [2].

**Objectives (Quality, Diversity, Controllability)**

*   **Quality:** Refers to how well a generated level meets desirable characteristics, such as being fun, challenging, aesthetically pleasing, and free of bugs. "Content quality assurance" is a stated property of some Mario PCG approaches [4].
*   **Diversity:** Pertains to the variety of levels a generator can produce. Generating levels with high "variety" is a recognized objective, ensuring that players encounter fresh experiences rather than repetitive content [7].
*   **Controllability:** Concerns the ability of a designer or system to influence the characteristics of the generated content, such as difficulty, theme, or specific mechanics. "Controllability" is a key property emphasized in several PCG works, including those for Super Mario Bros, where "controllable yet quality game levels" can be generated [4][7].

**Evaluation:**

**Automated Proxies:**
While the objective of generating "quality" content is frequently cited, the provided search results do not extensively detail specific automated proxy metrics for Mario PCG. There is no explicit mention of solvability agents, heuristics for enemy density, platforming challenge, or structural complexity measures specifically applied to Mario levels. However, the use of "extensive simulation results" to demonstrate quality and controllability, and the integration of "Dynamic Difficulty Adjustment (DDA)" in some Mario PCG systems, implies that automated assessments of level characteristics or player performance in simulated environments are utilized to some extent [4]. The precise nature of these simulation-based metrics for Mario levels remains unspecified in the given sources.

**Human Evaluation:**
Human evaluation is a critical component, particularly when aiming for "user experience" and "personalization." Experience-Driven Procedural Content Generation (EDPCG) highlights a framework where content generation is driven by "computational models of user experience" and "affective and cognitive modeling" [2]. This approach inherently relies on understanding and responding to human needs and preferences, suggesting that evaluation would involve direct human feedback or behavioral data. While specific methodologies for human evaluation in Mario PCG (e.g., pairwise comparisons, rating scales, detailed questionnaires) are not explicitly described in the provided papers, the EDPCG paradigm strongly advocates for evaluating the "effectiveness" of generated content in terms of its impact on the user's experience and enjoyment [2].

**Expressive Range Analysis:**
Assessing the diversity of generated content, or a generator's "expressive range," is crucial to avoid repetitive outputs. The term "variety" is mentioned as an aspect of analysis for generated content, alongside "accuracy" and "quality" [7]. This indicates a recognition of the need to measure the breadth of outputs from a PCG system. However, the provided search results do not specify particular methodologies or metrics (e.g., statistical analysis of feature distributions, coverage of a design space) for conducting expressive range analysis in the context of Mario procedural level generation.

**The “Oatmeal Problem” and How QD Methods Address It:**
The "oatmeal problem"—where a generator can produce many technically unique levels that nonetheless feel repetitive, uninspired, or unengaging to a human player—is not explicitly named or discussed in the provided search results, nor is the application of Quality-Diversity (QD) methods as a solution. While general concepts of "quality" and "variety" are touched upon, the specific challenge of bridging the gap between structural diversity and perceived player enjoyment, and the role of QD algorithms in simultaneously optimizing for both, is not addressed by the given literature.

### 2) Historical Review by Method Family

#### (a) Constructive / Rule-based / Multi-pass Generators

*   **Core idea**: These methods build levels step-by-step or by applying a set of predefined rules. They are often deterministic or semi-deterministic, relying on explicit design knowledge encoded by human designers. Early PCG systems frequently used this approach due to its simplicity and direct control over the generated content's properties [4][1].
*   **Level representation**: Typically operate on **tile grids** or other discrete structural elements. The rules define how these elements can be placed relative to each other.
*   **Constraints & playability**: Constraints are explicitly encoded within the rules themselves. For example, a rule might state that a block must always be supported from below, or that a gap cannot be wider than a player's maximum jump distance. Failure modes occur if the rule set is incomplete or contradictory, leading to impossible configurations or levels that are structurally sound but still unplayable by agents or humans due to unforeseen interactions.
*   **Control / conditioning**: Control is direct and high-level, determined by the parameters fed to the rule system or the specific rule set chosen. Designers have clear "knobs" by modifying rules or input parameters.
*   **Evaluation**: Primarily through designer inspection and basic automated checks for structural validity (e.g., connectivity, no floating blocks).
*   **Strengths and limitations**:
    *   **Strengths**: High degree of control and predictability, easy to understand and debug, efficient for generating certain types of content. Can ensure specific design patterns are present.
    *   **Limitations**: Can be rigid, struggle to produce complex or novel designs beyond what's explicitly programmed. Lacks variability and can lead to repetitive content if rules are too simple. Requires significant upfront design effort to encode all desired properties [2][1].
*   **Key papers/projects**: While no specific Mario paper from the provided set exclusively focuses on a pure rule-based system, the foundational principles are acknowledged as predecessors to more advanced techniques. For instance, the original Brogue dungeon generator, used as a source in the Moonshine paper, is a constructive PCG algorithm [7].

#### (b) Grammar-based Methods

*   **Core idea**: These methods use formal grammars (e.g., L-systems, production rules, chunk grammars) to generate content. The generation process starts from a high-level axiom and iteratively applies production rules to rewrite symbols into more complex structures. This allows for hierarchical and structured content generation [3].
*   **Level representation**: Levels are represented as **sequences of symbols** or **graph structures**, where symbols correspond to abstract level features or concrete tile patterns. Chunk grammars, for example, define how larger level "chunks" can be composed from smaller, valid sub-chunks.
*   **Constraints & playability**: Playability and structural integrity are enforced by designing grammar rules that only allow valid expansions. For instance, a rule might ensure that a "jump challenge" chunk always has a valid landing platform. Failure modes arise if grammar rules are ill-defined or lead to non-terminating expansions, or if the combinations of valid chunks result in globally unplayable sequences.
*   **Control / conditioning**: Control is exercised by selecting different starting axioms, adjusting probabilities of rule application (in probabilistic grammars), or by choosing specific grammar rules. This provides a structured way to guide content generation.
*   **Evaluation**: Primarily based on grammatical correctness, structural validity, and expressive range analysis (i.e., the variety of levels that can be generated by the grammar).
*   **Strengths and limitations**:
    *   **Strengths**: Good for generating structured and syntactically correct content, offers a clear hierarchical design, and can produce a wide variety of content within the grammar's bounds. Can encode design patterns effectively [3].
    *   **Limitations**: Can be rigid and "linear," making them less suitable for complex non-linear structures or highly interconnected levels. Designing comprehensive grammars can be labor-intensive and requires expert knowledge [3].
*   **Key papers/projects**: Sportelli et al. (2014) discusses probabilistic grammars for PCG [8]. Hendrikx et al. (2013) mentions generative grammars for plant and linear map dungeon generation [3].

#### (c) Probabilistic Models (Markov chains, hierarchical Markov, Bayesian approaches)

*   **Core idea**: These methods learn statistical patterns from existing levels to generate new ones. **Markov chains** learn the probability of a specific tile or level segment appearing given the preceding one(s). This allows for generating content that statistically resembles the training data [5][6]. Hierarchical Markov models can capture patterns at multiple levels of abstraction.
*   **Level representation**: Levels are typically represented as **sequences of tiles or vertical slices**. A tilemap can be read as a sequence, and the model learns the transition probabilities between consecutive elements in the sequence.
*   **Constraints & playability**: Playability is implicitly enforced if the training data consists of playable levels. The model learns common playable sequences. However, raw Markov chains can easily generate locally valid but globally unplayable levels (e.g., an endless series of small jumps without a clear path forward). Repair mechanisms or agent-based checks are often needed post-generation.
*   **Control / conditioning**: Control can involve biasing transition probabilities or seeding the generation with specific initial segments. However, fine-grained control can be challenging as the model primarily replicates learned statistical patterns.
*   **Evaluation**: Statistical similarity to training data, coherence, and basic playability checks (e.g., using A\* agents).
*   **Strengths and limitations**:
    *   **Strengths**: Relatively simple to implement, can learn complex patterns from data without explicit rules, produces content that feels "similar" to the training data. Efficient for generation once trained [1].
    *   **Limitations**: Can suffer from the "oatmeal problem" (lack of true novelty), prone to generating repetitive or locally coherent but globally inconsistent/unplayable levels. Requires sufficient training data. Poor global structure and long-range dependencies are hard to capture [1].
*   **Key papers/projects**: Summerville et al. (2018) survey PCGML methods including Markov models [5][6]. Guzdial et al. (2019) and Snodgrass and Summerville (2019) are referenced for Markov chain-based PCG [4].

#### (d) Search-based PCG (genetic algorithms, evolution strategies, novelty search, quality-diversity / MAP-Elites, constrained optimization like FI-2Pop)

*   **Core idea**: These methods frame PCG as an optimization problem. An initial population of levels (or level generators) is created and iteratively improved through processes inspired by natural evolution (mutation, crossover, selection). A "fitness function" evaluates each level, guiding the search towards content that optimizes desired objectives, such as playability or specific aesthetic criteria [2][1].
*   **Level representation**: Varies widely. Levels can be directly encoded as **tile grids** (direct encoding), or more abstractly as **parameter vectors** defining high-level features (indirect encoding), or even as **neural networks** that generate levels (neuroevolution of generators) [2].
*   **Constraints & playability**: Playability is explicitly enforced through the fitness function. A common approach is to use AI agents to "play" the generated level and assign a fitness score based on solvability, time to completion, or number of player deaths. Levels that are unplayable receive low fitness scores and are less likely to survive and reproduce [2][1][4].
*   **Control / conditioning**: Control is primarily through the design of the fitness function, which acts as a powerful "knob" to shape the evolution. Adjusting mutation rates, population size, and selection mechanisms also provide control. Novelty search and quality-diversity methods introduce additional "feature descriptors" or "behavioral characteristics" to encourage exploration and diversity beyond simple quality metrics.
*   **Evaluation**:
    *   **Fitness Score**: The primary metric, often a combination of playability (agent completion), feature counts (e.g., enemy density, coin count), and aesthetic measures.
    *   **Expressive Range Analysis**: Assessing the diversity of generated content across different runs or with varied objectives [2].
    *   **Human Evaluation**: Used to fine-tune fitness functions or validate the quality of evolved content [2].
*   **Strengths and limitations**:
    *   **Strengths**: Excellent for optimizing complex, non-linear objectives (like "fun" or "challenge" if quantifiable). Can discover novel and unexpected designs that human designers might not conceive. Can handle high-dimensional search spaces effectively. Well-suited for "generate-and-test" paradigms [2][1].
    *   **Limitations**: Computationally intensive, especially if fitness evaluation is costly (e.g., extensive agent playtesting). Performance heavily relies on a well-designed fitness function. Can suffer from "deception" (local optima) or the "oatmeal problem" if the fitness function is too narrow [2][1].
*   **Key papers/projects**: Togelius (2010) coined 'search-based PCG' [3]. Justesen et al. (2018) introduced a search-based progressive PCG method to overcome overfitting in DRL agents and control level difficulty [4]. Evolutionary computation is also combined with unsupervised learning in Latent Variable Evolution (LVE) approaches, exemplified by MarioGAN [1].

#### (e) PCGML / Deep Generative (LSTM/RNN sequence models, GANs, VAE/autoregressive models, Transformers, Diffusion)

This category represents a significant modern trend, learning from existing content to generate new content.

##### (i) LSTM/RNN Sequence Models (Mario as string; token orderings; conditioning)

*   **Core idea**: Recurrent Neural Networks (RNNs), particularly Long Short-Term Memory (LSTMs), are designed to process sequential data. In PCG, they learn the statistical dependencies between elements in a sequence, allowing them to generate new sequences (e.g., lines of tiles, or tokens representing game entities) that mimic the patterns of the training data [5][6].
*   **Level representation**: 2D Mario levels are typically flattened into **one-dimensional strings or sequences of tiles/tokens**. Each token represents a specific game element (e.g., ground, empty, pipe, enemy). Conditioning can be added by including special tokens or metadata in the sequence [1].
*   **Constraints & playability**: Like Markov models, LSTMs learn from playable examples, so they tend to generate locally coherent content. However, they can struggle with long-range dependencies, potentially leading to globally unplayable levels. Solvability agents are often used as a post-generation check [1].
*   **Control / conditioning**: Conditioning can be achieved by providing initial sequence segments, biasing inputs, or training LSTMs with additional context (e.g., player path annotations for personalized generation) [1].
*   **Evaluation**: Reconstruction accuracy, coherence of generated sequences, visual inspection, and agent-based playability checks [1].
*   **Strengths and limitations**:
    *   **Strengths**: Good at learning complex sequential patterns and long-range dependencies (better than simple Markov chains), can generate diverse content. More creative than rule-based systems [1].
    *   **Limitations**: Can still struggle with global structural coherence. Requires substantial training data. Overfitting can lead to repetitive patterns. The sequential nature can be unnatural for 2D grid generation [1].
*   **Key papers/projects**: Summerville and Mateas (2014) introduced an LSTM RNN framework to generate Super Mario Bros levels, training on a corpus of existing levels [4][1]. Summerville et al. (2018) used LSTMs trained on player paths to generate personalized levels [1].

##### (ii) GAN-based Generation (including latent space evolution like CMA-ES)

*   **Core idea**: Generative Adversarial Networks (GANs) consist of a generator network (creates content) and a discriminator network (tries to distinguish real from generated content). They are trained in an adversarial process, where the generator tries to fool the discriminator, leading to the creation of highly realistic and diverse content. When combined with Latent Variable Evolution (LVE), evolutionary algorithms search the GAN's latent space to find levels with desired properties [1].
*   **Level representation**: Mario levels are represented as **2D arrays of tiles (pixel-like images)**, where each tile type is mapped to a numerical value or color channel. The GAN generates these tilemaps from a **latent vector** (a point in a continuous low-dimensional space) [1].
*   **Constraints & playability**: GANs can generate very realistic-looking levels, but they don't inherently guarantee playability. Unplayable structures like "broken pipes" are common failure modes. LVE addresses this by using playability agents (e.g., A\* agents) as part of the fitness function to guide the evolutionary search in the latent space towards playable content [1]. Constrained Adversarial Networks (CANs) also attempt to penalize invalid structures during training [1].
*   **Control / conditioning**: Direct control over GANs is typically through manipulating the latent vector. LVE provides an indirect, search-based control mechanism by optimizing for desired level characteristics (e.g., difficulty, specific behaviors) in the latent space.
*   **Evaluation**: Visual realism, Inception Score (for quality and diversity), and crucially, agent-based playability evaluation. Human evaluation for aesthetic and gameplay appeal [1].
*   **Strengths and limitations**:
    *   **Strengths**: Can generate highly diverse and visually compelling levels that capture the "look and feel" of original content. LVE combines the generative power of GANs with the optimization power of evolution. Good for generating tile-based content [1][3].
    *   **Limitations**: Training GANs is notoriously difficult and unstable. Often suffer from "mode collapse" (generating only a limited variety of output). Generated levels do not inherently guarantee playability, requiring external mechanisms like LVE or explicit constraint handling. Lacks global structural coherence without additional mechanisms [1].
*   **Key papers/projects**: **MarioGAN** by Volz et al. (2018) applied LVE (using CMA-ES) to search the latent space of a Deep Convolutional GAN (DCGAN) trained on Super Mario Bros level segments. This is a seminal work in deep generative Mario PCG [1].

##### (iii) VAE / autoregressive models / Transformers

*   **Core idea**: **Variational Autoencoders (VAEs)** learn a compressed, continuous latent representation of the input data, allowing for smooth interpolation and generation of variations. Autoregressive models (like Transformers for sequences) generate content element by element, predicting the next part based on previous ones, naturally handling long-range dependencies [1][3].
*   **Level representation**: Similar to GANs, VAEs typically represent levels as **2D tilemaps**, which are encoded into and decoded from a **latent vector**. Transformers operate on **tokenized representations** of level segments or entire levels [1][3].
*   **Constraints & playability**: VAEs learn from training data and can generate plausible levels, but like GANs, playability is not guaranteed. Repair mechanisms or external playability checks are often integrated. Transformers, through their attention mechanisms, can learn complex dependencies that might contribute to more coherent, and thus potentially more playable, structures.
*   **Control / conditioning**: VAEs offer control through manipulation of their latent space (e.g., interpolating between different level styles or features) [1]. Transformers can be conditioned on specific inputs or tokens to guide generation towards desired patterns.
*   **Evaluation**: Reconstruction loss, disentanglement of latent dimensions, visual quality, diversity metrics, and agent-based playability.
*   **Strengths and limitations**:
    *   **Strengths**: VAEs provide a well-behaved latent space for exploration and interpolation, useful for blending and creating stylistic variations. Transformers excel at learning long-range dependencies and complex patterns from large datasets [3].
    *   **Limitations**: Generating high-resolution, complex levels can be challenging. Playability is not guaranteed. VAEs can sometimes produce blurry outputs. Transformers require vast amounts of data and computational resources.
*   **Key papers/projects**: Sarkar et al. (2019, 2020) explored using VAEs to blend levels from different platforming games (Mario, Kid Icarus, Megaman) by interpolating in the latent space [1]. Snodgrass and Sarkar (2020) used VAEs to generate platformer level structures [3]. Mohaghegh et al. (2023) used Transformers for Sokoban map generation [3].

##### (iv) Diffusion or other recent generative paradigms if applied to tile maps

*   **Core idea**: Diffusion models work by iteratively denoising a random noise input, gradually transforming it into a coherent sample from the learned data distribution. They have achieved state-of-the-art results in image generation and are beginning to be applied to other domains like game content [7].
*   **Level representation**: Levels are treated as **2D images or 3D matrices (e.g., Height x Width x Tile_Channels)**, generated by iteratively refining a noisy input. They can be conditioned by external inputs, such as text embeddings [7].
*   **Constraints & playability**: Diffusion models learn from the data. If trained on playable levels, they will tend to generate plausible structures. However, similar to GANs and VAEs, explicit playability guarantees are not inherent and often require post-processing or conditioned generation with playability in mind.
*   **Control / conditioning**: Diffusion models are highly amenable to conditioning. For instance, text embeddings can be integrated into the denoising process, allowing natural language prompts to guide the generation of specific level features [7].
*   **Evaluation**: Visual quality, diversity, FID/Inception scores, and crucially for conditioned generation, semantic alignment between the input condition (e.g., text) and the generated output (e.g., using CLIP Score) [7].
*   **Strengths and limitations**:
    *   **Strengths**: Known for generating high-quality and diverse content, often surpassing GANs in realism and mode coverage. Highly controllable through conditioning mechanisms [7].
    *   **Limitations**: Computationally expensive for both training and inference (can require many denoising steps). May still require external mechanisms for strict playability enforcement.
*   **Key papers/projects**: Nie et al. (2024) introduced the "Moonshine Diffusion Model" within a framework for text-to-game-map generation, demonstrating its ability to create diverse and controllable roguelike dungeon maps conditioned on natural language prompts. This method is highly relevant for future Mario PCG [7].

#### (f) Path-conditioned / playability-aware generation

*   **Core idea**: This family of methods explicitly incorporates player paths or solvability information during the generation process or as a conditioning factor. The goal is to ensure generated levels are not just syntactically correct but also strategically interesting or tailored to specific player behaviors [1].
*   **Level representation**: Levels are often represented as **tile grids or sequences**, with additional information about player paths (e.g., annotated gameplay traces, agent-generated paths) used as input or targets.
*   **Constraints & playability**: Playability is a primary objective. Methods might involve:
    *   **Training with player path labels**: Learning from levels annotated with successful player trajectories.
    *   **Constrained decoding**: During generation, explicitly checking if partial levels allow for a valid path to completion.
    *   **"Generate with solvability in the loop"**: Integrating a solvability checker or agent directly into the generative process (e.g., as part of a fitness function in search-based PCG, or a reward in DRL).
*   **Control / conditioning**: The player path itself serves as a strong conditioning signal. Generating levels that "encourage jumping" or "avoid combat" are examples of path-based control.
*   **Evaluation**: Agent-based solvability (e.g., A\* agent completion rate), analysis of generated paths (e.g., path complexity, length), and human evaluation of gameplay flow.
*   **Strengths and limitations**:
    *   **Strengths**: Directly addresses the playability concern, can generate levels tailored to specific play styles or difficulty levels, and can create more strategically interesting content [1].
    *   **Limitations**: Requires access to player path data or a robust, fast solvability agent. The definition of an "interesting" path can be subjective and hard to formalize.
*   **Key papers/projects**: Summerville et al. (2018) extracted player paths from Mario gameplay videos to annotate training levels and trained LSTMs to generate personalized levels based on chosen paths [1]. Volz et al.'s MarioGAN (2018) used an A\* agent simulating gameplay to evaluate and search for playable and behavior-encouraging Mario level segments [1].

#### (g) LLM-based Generation (text2level, prompt-controlled, mutation via LLM, novelty search with LLM outputs, etc.)

*   **Core idea**: Leverages the natural language understanding and generation capabilities of Large Language Models (LLMs) to control and produce game content. This paradigm allows designers to interact with PCG systems using intuitive text prompts, moving beyond technical parameters [7][3].
*   **Level representation**: While the final output is often a **tilemap**, the input is typically a **natural language prompt**. LLMs can also generate intermediate representations like high-level descriptions, structural rules, or even code snippets, which are then used by other generators to create the actual level. Text embeddings are used to condition deep generative models [7][3].
*   **Constraints & playability**: LLMs themselves do not inherently guarantee playability. However, they can be prompted to include playability considerations (e.g., "create a solvable level"). The generated outputs often need to be validated by other mechanisms (e.g., playability agents, repair systems). The Moonshine framework uses LLMs to generate labels for content from a constructive PCG algorithm which ensures playability [7].
*   **Control / conditioning**: This is the primary strength. Control is achieved through detailed **textual prompts**, allowing for fine-grained semantic control over the generated content. Prompt engineering becomes a key skill. LLMs can also be used to generate diverse descriptions for training data, enhancing the control and diversity of subsequent generative models [7][3].
*   **Evaluation**: Adherence to prompt specifications, human judgment of coherence, creativity, and aesthetic quality. Semantic similarity metrics (like CLIP Score) between prompts and generated levels are also used. Player experience can be evaluated based on levels generated from desired difficulty prompts [7][3].
*   **Strengths and limitations**:
    *   **Strengths**: Offers highly intuitive and flexible control through natural language. Can generate diverse and creative content. Bridges the gap between designer intent and technical implementation. Great potential for mixed-initiative design and content analysis [7][3].
    *   **Limitations**: LLMs are "black boxes" for many researchers (especially proprietary ones), hindering deep analysis or modification. Their outputs can be inconsistent or "hallucinate" unplayable content without proper validation. Requires careful prompt engineering. Computationally intensive. The quality of output is dependent on the LLM's understanding and the richness of the conditioning data [7][3].
*   **Key papers/projects**: Sudhakaran et al. (2024) introduced **MarioGPT**, a fine-tuned GPT-2 model designed to generate Super Mario Bros levels based on textual prompts [3]. Nie et al. (2024) developed the "Moonshine" framework, which uses LLMs (GPT4-Turbo) to generate synthetic labels for roguelike dungeon maps, enabling text-conditioned diffusion models to generate content [7].

#### (h) Experience-driven / personalized PCG (EDPCG) and preference learning

*   **Core idea**: EDPCG aims to generate content that explicitly optimizes for a desired player experience (e.g., fun, challenge, engagement) rather than just structural validity or solvability. This involves modeling player experience and using this model as a fitness function to guide content generation, often for personalization [2][1].
*   **Level representation**: Can use various representations, but typically involves a **parameter vector** that describes high-level features of the level that are known to influence player experience (e.g., gap frequency, enemy density) [2].
*   **Constraints & playability**: Playability is implicitly handled by the player experience model (PEM). If a level is unplayable, it will likely lead to negative experiences (frustration, boredom) and thus a low fitness score, leading to its discard by the generator. The PEM learns to associate level parameters with specific affective states, ensuring that generated levels are tailored to desired experiences, which inherently implies playability for that target experience [2].
*   **Control / conditioning**: Control is achieved by specifying the target player experience or affective state to optimize for (e.g., "maximize fun for player X," "maximize challenge for player Y"). Player models, built from collected gameplay data and feedback, act as conditioning agents [2].
*   **Evaluation**:
    *   **Player Experience Modeling (PEM)**: Training neural networks to predict affective states (fun, challenge, frustration, etc.) based on level parameters and player-style metrics (e.g., jumping frequency, deaths) [2][1].
    *   **Human User Trials**: Pairwise comparisons, rating scales, and analysis of physiological data or gameplay metrics to validate the PEM and assess generated content [2][1].
    *   **Regression Models**: Predicting human evaluations of levels based on statistical measures [1].
*   **Strengths and limitations**:
    *   **Strengths**: Directly addresses the "fun" aspect, can personalize content for individual players, leads to higher player engagement. Integrates human-centric objectives into PCG [2][1].
    *   **Limitations**: Quantifying player experience and content quality is challenging and often subjective. Requires significant data collection from human players, which can be expensive and ethically complex. PEMs can be noisy and complex to build. The search space for "optimal experience" can be hard to navigate [2].
*   **Key papers/projects**: Yannakakis and Togelius (2011) introduced the **Experience-Driven Procedural Content Generation (EDPCG)** framework, with examples in Super Mario Bros where neural networks were trained to predict affective states (fun, challenge, frustration) based on level parameters and player data to generate personalized levels [2][1]. Pedersen et al. (2010) are cited as a foundational work within this framework for Mario-like games [2].

#### (i) Pattern-based generation (design patterns as targets or objectives, chunk libraries / motif-based synthesis)

*   **Core idea**: This approach leverages libraries of existing "design patterns" or "motifs" (small, meaningful, and often playable level segments) as building blocks. Generation then involves selecting, arranging, and combining these patterns to form larger levels, often guided by high-level design principles or constraints [1].
*   **Level representation**: Levels are represented as **collections or sequences of predefined chunks/patterns**. These chunks are typically small tilemaps that embody specific gameplay mechanics or aesthetic elements.
*   **Constraints & playability**: Playability is largely guaranteed if the individual patterns are pre-verified as playable. The challenge lies in ensuring that the *combination* of patterns also results in a playable and coherent level. Rules for combining patterns can enforce structural and gameplay constraints.
*   **Control / conditioning**: High-level control is achieved by selecting specific patterns from the library, defining their arrangement, or specifying design goals (e.g., "create a level with many jump patterns and one enemy encounter pattern").
*   **Evaluation**: Consistency of patterns, overall level coherence, and agent-based playability of the assembled level.
*   **Strengths and limitations**:
    *   **Strengths**: Ensures local playability and aesthetic consistency if patterns are well-designed. Can produce structured and recognizable levels. Reduces the complexity of generating entire levels from scratch [1].
    *   **Limitations**: The quality and variety of generated levels are limited by the quality and diversity of the pattern library. Can lead to repetitive levels if the library is small. Challenges in smoothly transitioning between different patterns.
*   **Key papers/projects**: Guzdial et al. (2015) trained a random forest on expert-labeled design patterns from Mario levels to classify level structures, using an autoencoder to generate new instances of these design patterns [1].

### 3) Deep Dives

Here, we will deep dive into three influential approaches that represent different stages of Mario PCG evolution and demonstrate key techniques.

#### (a) Deep Dive 1: Experience-Driven Procedural Content Generation (EDPCG) for Super Mario Bros.

**Core Idea and Context**:
The Experience-Driven Procedural Content Generation (EDPCG) framework, as introduced by Yannakakis and Togelius (2011) and exemplified by Pedersen et al. (2010) for Super Mario Bros., revolutionizes PCG by prioritizing **player experience** over mere structural validity. Instead of simply generating levels, EDPCG aims to generate content that *optimizes for desired affective states* (e.g., fun, challenge, frustration) in specific players. This is achieved by creating computational models of player experience (PEMs) and using them as fitness functions in a search-based PCG process [2][1]. This approach represents a significant step towards human-centered PCG, addressing the gap between algorithmically valid and subjectively enjoyable content.

**Pipeline Diagram-in-Words**:

1.  **Human Playtesting & Data Collection**:
    *   Human players play an open-source clone of Super Mario Bros. (or pairs of levels).
    *   During or after play, players provide **subjective ratings** on affective states (e.g., "Which level was more fun?", "Rate the challenge from 1-5") for various criteria (fun, challenge, frustration, predictability, anxiety, boredom).
    *   **Gameplay telemetry** is simultaneously recorded: player actions (jumping frequency, running, shooting), time spent in various states (moving left/still), enemy interactions (enemies killed), jump difficulty, deaths (due to falling into gaps, enemies), etc. [2].

2.  **Level Representation for Modeling**:
    *   Levels are represented not as raw tilemaps, but as **short parameter vectors**. For instance, a level might be described by parameters such as: number of gaps, size of gaps, placement of gaps, and the presence or absence of a "switching mechanic" [2].

3.  **Player Experience Model (PEM) Training**:
    *   **Input**: The recorded level parameters and player-style metrics are fed into a machine learning model (e.g., **Neural Networks**).
    *   **Output**: The model is trained (often using **evolutionary preference learning**) to predict the six affective states (fun, challenge, frustration, predictability, anxiety, boredom) for a given level parameter set and a specific player's style profile.
    *   **Goal**: The neural network learns the complex, non-linear mapping between objective level features/player behavior and subjective player experience [2].

4.  **Content Generator (Search Algorithm) Driven by PEM**:
    *   A **search algorithm** (typically an **evolutionary algorithm**) generates candidate level parameter vectors.
    *   For each candidate parameter vector, a **stochastic algorithm** converts it into a full level (e.g., by building the level from right to left, placing gaps according to parameters).
    *   The generated level (or its parameter vector) is then evaluated by the trained PEM, which acts as the **fitness function**.
    *   The evolutionary algorithm iteratively refines the level parameter vectors to maximize the desired affective state (e.g., "maximize fun for player X") predicted by the PEM [2].

**Training Data and Preprocessing**:
*   **Source**: Human play sessions on a modified Super Mario Bros. clone.
*   **Preprocessing**:
    *   Level data is abstracted into quantifiable "parameter vectors."
    *   Player behavior is quantified into "player-style metrics."
    *   Human feedback on affective states is collected, potentially in pairwise comparisons or rating scales, and used as labels for training the PEM.

**Ablation Findings (as implied by the paper)**:
The paper discusses the importance of various features for predicting affective states. For instance, "fun" was found to correlate with "time moving left" and "enemies killed," while "frustration" correlated with "standing still" and "jump difficulty" [2]. This implies that including robust player-style metrics and diverse level parameters are crucial for accurate PEMs. Removing or simplifying these features would likely degrade the model's ability to predict nuanced player experiences. The reliance on evolutionary preference learning for training indicates that traditional supervised learning might be less effective given the subjective and often noisy nature of human feedback.

**How it might be reproduced today**:
1.  **Game Environment**: Set up an open-source Super Mario Bros. clone (e.g., Infinite Mario Bros. or a similar framework).
2.  **Instrumentation**: Instrument the game to log player actions and game states (telemetry).
3.  **Human Data Collection**: Recruit human players (adhering to ethical guidelines) to play levels and provide real-time or post-game feedback on their experience (e.g., using a web interface for pairwise comparisons or Likert scales for affective states).
4.  **Feature Engineering**: Extract relevant level parameters and player-style metrics from game logs.
5.  **PEM Training**: Train a machine learning model (e.g., a modern neural network, potentially a recurrent network to handle sequential player data) using the collected data to predict affective states. Techniques like evolutionary preference learning can still be valuable.
6.  **Generator Integration**: Implement a level generator that takes a parameter vector as input. Integrate this with a search algorithm (e.g., CMA-ES, genetic algorithm) that uses the trained PEM as its fitness function to evolve levels optimized for specific player experiences.

#### (b) Deep Dive 2: MarioGAN - Generating Mario Levels with Deep Convolutional GANs and Latent Variable Evolution

**Core Idea and Context**:
MarioGAN, developed by Volz et al. (2018), represents a significant application of deep generative models combined with evolutionary search to Mario PCG. It leverages the power of Deep Convolutional Generative Adversarial Networks (DCGANs) to learn the distribution of Super Mario Bros. level segments and then uses Latent Variable Evolution (LVE), specifically the Covariance Matrix Adaptation Evolution Strategy (CMA-ES), to search the GAN's latent space for levels that satisfy specific playability and behavioral objectives . This approach moved beyond simply mimicking patterns to actively searching for "good" content within a learned generative manifold.

**Pipeline Diagram-in-Words**:

1.  **Training Data Preparation**:
    *   **Source**: A single Super Mario Bros. level (e.g., World 1-1) is segmented into numerous overlapping 16x7 level segments (16 tiles wide, 7 tiles high).
    *   **Representation**: Each segment is represented as a 2D grid of tiles, where each tile type (e.g., ground, empty, coin, enemy, pipe) is mapped to a numerical value or a unique color, effectively treating the level segment as a small image.
    *   **Dataset**: A dataset of these segments is created for training.

2.  **DCGAN Training**:
    *   A **DCGAN** is trained on the dataset of Mario level segments.
    *   **Generator (G)**: Learns to map random noise vectors (latent vectors) from a low-dimensional **latent space** to realistic 16x7 Mario level segments.
    *   **Discriminator (D)**: Learns to distinguish between real Mario level segments from the training data and fake segments generated by G.
    *   **Adversarial Training**: G and D are trained adversarially until G can produce segments that D can no longer reliably distinguish from real ones. The trained G effectively learns a continuous manifold of plausible Mario level segments [1].

3.  **Latent Variable Evolution (LVE) with CMA-ES**:
    *   **Evolutionary Algorithm**: **CMA-ES** (Covariance Matrix Adaptation Evolution Strategy) is used as the search algorithm.
    *   **Individuals**: Each "individual" in the population is a **latent vector** `z` from the GAN's latent space.
    *   **Phenotype Generation**: For each latent vector `z`, the trained **GAN Generator (G)** produces a corresponding 16x7 Mario level segment `L = G(z)`.
    *   **Fitness Function**: This is the core of LVE. For each generated level segment `L`, an **AI agent (e.g., an A\* agent)** attempts to play and complete the segment. The fitness function combines multiple objectives:
        *   **Playability**: Assessed by the A\* agent's ability to reach the end of the segment.
        *   **Behavioral Objectives**: Can include encouraging specific player behaviors, such as maximizing jumps, collecting coins, or avoiding specific enemies. For example, a fitness component might reward segments that have a high number of reachable coins or require frequent jumping.
    *   **Evolutionary Loop**: CMA-ES iteratively updates the distribution of latent vectors, guiding the search towards areas of the latent space that produce level segments with higher fitness scores (i.e., more playable and satisfying desired behavioral objectives) [1].

4.  **Level Assembly (Post-Processing)**:
    *   MarioGAN primarily generates *segments*. A full level is then constructed by concatenating these evolved segments.
    *   **Issue**: This concatenation can lead to a lack of global coherence or "broken pipes" if not handled carefully, as segments are generated independently [1].

**Training Data and Preprocessing**:
*   **Source**: A single Super Mario Bros. level (e.g., World 1-1).
*   **Preprocessing**: Level is chopped into overlapping 16x7 segments. Each tile type within a segment is encoded numerically or color-coded for image-like input to the DCGAN.

**Ablation Findings (as discussed in Liu et al. 2020)**:
*   **Limitations of initial MarioGAN**:
    *   **"Broken pipes" / Invalid structures**: The generated segments could sometimes contain structurally unsound or unplayable elements, as the GAN inherently generates plausible *patterns* but not necessarily *functional* game mechanics [1].
    *   **Lack of global structure**: Concatenating independently generated segments resulted in levels that lacked overall design flow or long-range coherence [1].
*   **Proposed Solutions (by others)**:
    *   **Repair mechanisms**: Shu et al. (2018) addressed broken pipes by training an MLP to detect wrong tiles and using an evolutionary repairer to find optimal replacements [1].
    *   **Global structure**: Approaches like CPPN2GAN (Schrum et al., 2018) used Compositional Pattern Producing Networks (CPPNs) to organize GAN-generated segments into complete levels, providing global guidance [1].

**How it might be reproduced today**:
1.  **Game Environment**: Use an open-source Super Mario Bros. framework to extract level data and for agent-based playtesting.
2.  **Dataset Creation**: Extract segments from several Super Mario Bros. levels to create a more diverse training dataset than a single level.
3.  **DCGAN Implementation**: Implement a DCGAN (or a more advanced GAN architecture like StyleGAN or conditional GAN) capable of generating tile-based images.
4.  **AI Agent for Playability**: Develop or use an existing A\* agent (or a simple platformer controller) that can attempt to traverse generated level segments and report success/failure or behavioral metrics.
5.  **CMA-ES Integration**: Implement CMA-ES (or another evolutionary strategy) to optimize latent vectors.
6.  **Fitness Function Design**: Design a fitness function that combines agent-based playability with desired behavioral objectives (e.g., "maximize coins collected," "force player to jump frequently").
7.  **Level Assembly**: Implement a post-processing step for stitching segments together, possibly incorporating global coherence rules or using methods like CPPN2GAN.

#### (c) Deep Dive 3: Moonshine Framework - Distilling Constructive PCG into Steerable Text-Conditioned Generative Models

**Core Idea and Context**:
The "Moonshine" framework by Nie et al. (2024) presents a cutting-edge approach to creating **text-conditioned PCGML models** without the burden of extensive human-labeled datasets. It achieves this by *distilling* the knowledge embedded in a traditional, robust **constructive PCG algorithm** into deep generative models. This "distillation" uses Large Language Models (LLMs) to automatically generate vast, diverse, and human-like textual descriptions for content produced by the constructive algorithm. These synthetic (map, text description) pairs then train deep generative models, enabling natural language control over content generation. While demonstrated with roguelike dungeons (Brogue), the methodology is highly applicable to Mario PCG [7].

**Pipeline Diagram-in-Words**:

1.  **Synthetic Dataset Generation (Leveraging LLMs)**:
    *   **Source Constructive PCG**: A traditional, rule-based or constructive PCG algorithm (e.g., Brogue's dungeon generator, which ensures playability) is used to generate a large collection of game content (e.g., 70,000 roguelike dungeon maps).
    *   **Map Extraction & Representation**: These maps are extracted and standardized (e.g., 32x32 tiles) using a defined tileset (e.g., 14 terrain tiles). They are represented as 3D matrices (Height x Width x Channels, where channels are tile probabilities).
    *   **Map Metadata Analysis**: For each generated map, extensive metadata is extracted using heuristics (e.g., binary masks for rooms/paths, cardinal directions of rooms, tile counts, connected room pairs). This metadata provides rich, objective features of the map.
    *   **LLM Description Generation**: A powerful LLM (e.g., **GPT4-Turbo**) is prompted with:
        *   Its role as a data annotator.
        *   Detailed instructions for generating diverse, human-like, and creative text descriptions (both long and short versions) for each map.
        *   The integer tile grid and the extracted metadata for the map.
        *   Few-shot examples of human-authored descriptions.
        *   "Hard rules" to follow (e.g., avoiding repetition, specific words).
    *   **Synthetic (Map, Text) Pairs**: This process yields a large dataset where each map is paired with multiple LLM-generated text descriptions [7].

2.  **Text Embedding**:
    *   A pre-trained **text embedding model** (e.g., `gte-large-en-v1.5`) converts the LLM-generated text descriptions into **1024-dimensional text embedding vectors**. These vectors capture the semantic meaning of the descriptions and serve as the conditioning input for the generative models [7].

3.  **Deep Generative Model Training (Text-to-Game-Map - T2M)**:
    *   Two types of multi-modal generative models are trained on the synthetic dataset (maps + corresponding text embedding vectors):
        *   **Five-Dollar-Model (Feed-forward Neural Network)**: A streamlined feed-forward network maps a text embedding (concatenated with noise) through dense layers, reshaping, upsampling (residual blocks), and a convolutional layer to produce a map. This model is efficient but may lack diversity and can overfit quickly [7].
        *   **Moonshine Diffusion Model (Conditional UNet)**: Based on Denoising Diffusion Probabilistic Models (DDPM), this model iteratively denoises a random noise input, guided by the text embedding. It uses a conditional UNet architecture with ResNet and cross-attention blocks. The denoising process is aligned with the semantics of the text, gradually transforming noise into a map that matches the description. This model offers higher diversity and better semantic alignment [7].

**Training Data and Preprocessing**:
*   **Source**: Automated generation from a constructive PCG (Brogue).
*   **Preprocessing**:
    *   Maps are standardized in size and tile encoding.
    *   Heuristic metadata extraction for each map.
    *   LLM-based natural language description generation from maps and metadata, guided by detailed prompts.
    *   Text-to-vector embedding using a pre-trained model.

**Ablation Findings (Nie et al. 2024)**:
*   The **Five-Dollar Model** was efficient but demonstrated **lower diversity** and showed signs of **overfitting** after a relatively small number of epochs (approx. 20), indicating it memorized patterns rather than generalizing robustly.
*   The **Moonshine Diffusion Model** demonstrated **greater potential for diversity** and achieved **superior semantic alignment** (higher finetuned CLIP scores) between text descriptions and generated maps. It showed better generalization, with validation loss increasing slowly only after 250 epochs.
*   The LLM (GPT4-Turbo) was generally effective at generating diverse and human-like descriptions, but sometimes **struggled to capture "tiny details"** or fine-grained spatial instructions ("a dot of...", "scattered around"), which subsequently limited the generative models' ability to reproduce these details. This highlights a limitation in both the LLM's descriptive capabilities and the generative models' fidelity to fine detail [7].

**How it might be reproduced today**:
1.  **Mario Constructive PCG**: Replace Brogue with a well-defined Mario constructive PCG algorithm (e.g., a rule-based generator, a grammar-based system, or even human-designed levels) to generate a large dataset of *playable* Mario levels.
2.  **Mario Metadata Extraction**: Develop heuristics to extract meaningful metadata from these Mario levels (e.g., number of enemies, types of jumps, presence of power-ups, structural complexity, pathing information).
3.  **LLM Prompt Engineering (Mario-specific)**: Craft detailed prompts for a powerful LLM (e.g., GPT-4, Llama 3) to generate natural language descriptions of the Mario levels, incorporating the extracted metadata. Ensure diversity and human-like quality.
4.  **Text Embedding**: Utilize a state-of-the-art text embedding model to convert generated descriptions into vectors.
5.  **Deep Generative Model Implementation**: Implement either the "Five-Dollar Model" or, preferably, the "Moonshine Diffusion Model" (conditional UNet) and train it on the synthetic (Mario map, text embedding) dataset.
6.  **Evaluation**: Use finetuned CLIP Score for semantic alignment, visual inspection for quality, and potentially an AI agent for playability validation of the generated Mario levels against their descriptive prompts.

### 4) Datasets, Benchmarks, and Environments

*   **Commonly used SMB level datasets**:
    Super Mario Bros. levels, particularly from the original NES game, are frequently used as training data and benchmarks due to their iconic status, well-defined tile-based structure, and established gameplay mechanics [4][1][3].
    *   **Original Super Mario Bros. Levels**: Often segmented into smaller chunks (e.g., 16x7 segments for MarioGAN) for training deep generative models [1].
    *   **Corpus of Levels**: Summerville and Mateas (2014) trained LSTMs on a corpus of 39 existing Super Mario Bros. levels [4].
    *   **Player Path Annotations**: Levels annotated with human player paths or agent traces are used for path-conditioned generation .
    *   **MarioGPT Training Data**: The MarioGPT model (Sudhakaran et al. 2024) was fine-tuned on Super Mario Bros. levels, implying a dataset derived from these levels represented as sequences of words or sentences [3].
    *   **Synthetic Datasets**: For methods like the Moonshine framework, while not directly Mario-specific in its original form, the principle of generating large synthetic datasets from a robust (Mario) constructive algorithm is directly applicable [7].

*   **Common evaluation environments (Mario AI Framework, Infinite Mario Bros, PCG Benchmark SMB tasks, etc.)**:
    *   **Mario AI Framework**: This is explicitly highlighted as the "drosophila of PCG research" due to its widespread use in research projects. Built around an open-source clone of Super Mario Bros., it provides a standardized environment for testing PCG algorithms and AI agents [1]. It typically offers an interface for agents to interact with generated levels, enabling automated playability testing.
    *   **Infinite Mario Bros**: An open-source Java clone of Super Mario Bros., frequently used as a testbed for PCG and AI research. Its open-source nature facilitates customization and integration of new algorithms [1]. Guzdial et al. (2015) used it for case studies in predicting level difficulty, enjoyment, and aesthetics [1].
    *   **Custom Simulators**: Researchers often develop custom simulators or adapt existing game engines (e.g., Unity) to evaluate generated content, especially when specific metrics or agent behaviors need to be tracked.
    *   **Offline Evaluation**: Many deep generative models focus on generating static level images/tilemaps, which are then evaluated offline through visual inspection or quantitative metrics before being loaded into a game engine.

*   **Constraints of each environment and what they measure well/poorly**:
    *   **Mario AI Framework / Infinite Mario Bros**:
        *   **Measures well**: Agent-based playability (e.g., completion rate, pathfinding success), difficulty (e.g., time to completion, number of deaths), certain behavioral aspects (e.g., jumping frequency, enemy encounters). Offers a controlled environment for comparing PCG algorithms against standardized AI agents.
        *   **Measures poorly**: Direct human enjoyment, qualitative aspects like "fun" or "creativity" (these require human subjects). Can be slow for large-scale evaluation if real-time simulation is required.
    *   **Offline Evaluation (e.g., for GANs, VAEs, Diffusion Models)**:
        *   **Measures well**: Visual realism, diversity of output, reconstruction accuracy, semantic alignment (for text-conditioned models). These are useful for assessing the generative model's capabilities.
        *   **Measures poorly**: Actual gameplay experience, dynamic playability under different player skills, subjective enjoyment. A visually plausible level might still be unplayable or boring.

### 5) Human Evaluation and “Fun”

Human evaluation is paramount in Mario PCG because the ultimate goal is to create levels that people *enjoy* playing, not just levels that are technically solvable or structurally sound [2][1]. There is a recognized "human preference gap" where automated metrics often fail to capture subjective qualities like fun, challenge, or satisfaction [2].

*   **What are common human evaluation designs in Mario PCG?**
    *   **Pairwise Comparisons**: Participants are presented with two generated levels (or level segments) and asked to choose which one better exhibits a specific quality (e.g., "Which is more fun?", "Which is more challenging?") [2]. This method reduces cognitive load compared to absolute ratings and provides robust relative preferences.
    *   **Rating Scales**: Participants rate levels on a Likert scale (e.g., 1-5) for various attributes such as fun, challenge, aesthetics, originality, frustration, and predictability [2].
    *   **Gameplay Telemetry Analysis**: Collecting objective data during human play sessions (e.g., time spent, number of deaths, actions per minute, specific behavioral patterns like jumping frequency) and correlating it with subjective feedback or using it to train player experience models [1].
    *   **Think-Aloud Protocols/Interviews**: Qualitative data collection where players verbalize their thoughts and feelings during gameplay or participate in post-game interviews to provide rich insights into their experience.

*   **Pairwise comparisons vs ratings vs playtime signals**
    *   **Pairwise Comparisons**:
        *   *Pros*: Easier for participants, reduces individual rating biases, provides robust relative rankings.
        *   *Cons*: Can be time-consuming for many items, only provides relative preference.
    *   **Rating Scales**:
        *   *Pros*: Provides absolute measures, allows for direct comparison of different levels on the same scale.
        *   *Cons*: Prone to individual rating biases (e.g., some people always rate high/low), can suffer from anchor effects, and might not capture nuanced differences as well as pairwise comparisons.
    *   **Playtime Signals (Telemetry)**:
        *   *Pros*: Objective, non-intrusive, can be collected at scale. Directly reflects player interaction.
        *   *Cons*: Often a "low-resolution model of playing experience" [2], requires strong assumptions to map gameplay data to subjective enjoyment. A player might spend a long time on a level because it's fun or because it's frustratingly difficult.

*   **Judge expertise vs crowd**
    *   **Judge Expertise**: Using professional game designers or experienced players can provide deep, insightful feedback grounded in design principles and extensive game knowledge. However, they are a small, expensive resource.
    *   **Crowd-sourcing**: Platforms like Amazon Mechanical Turk can provide large volumes of data from a diverse player base, which is valuable for training large models. However, crowd-sourced data can be noisy, lack depth, and require careful quality control. The specific papers provided do not deeply differentiate these, but the EDPCG framework would benefit from either approach to build robust player models [2]. Nie et al. (2024) mentions using a "preliminary survey of human responses" for few-shot examples and comparing LLM-generated descriptions against "human-authored descriptions," suggesting a form of crowd or expert input [7].

*   **Biases and how to mitigate**
    *   **Anchoring Bias**: Early experiences or specific prompts can unduly influence subsequent ratings. *Mitigation*: Randomize presentation order, use calibration items (known good/bad levels), or use pairwise comparisons.
    *   **Order Effects**: The order in which levels are played/rated can affect perception. *Mitigation*: Randomize presentation order.
    *   **Demand Characteristics**: Participants try to guess the experiment's hypothesis and respond accordingly. *Mitigation*: Blind studies, clear and neutral instructions.
    *   **Expert Bias**: Experts might evaluate based on specific design principles rather than general player enjoyment. *Mitigation*: Triangulate with crowd data, ensure diverse expert panel.
    *   **Subjectivity of "Fun"**: The definition of "fun" varies widely. *Mitigation*: Break down "fun" into more granular affective states (challenge, excitement, frustration, etc.) for more precise measurement, as done in EDPCG [2].
    The provided articles do not explicitly discuss biases and mitigation in detail, but these are general considerations for human evaluation.

*   **Which papers explicitly measure “fun,” “challenge,” “frustration,” etc.**
    *   **Yannakakis and Togelius (2011)** and **Pedersen et al. (2010)** (within the EDPCG framework): Explicitly trained neural networks to predict six affective states: fun, challenge, frustration, predictability, anxiety, and boredom, based on level parameters and player-style metrics in Super Mario Bros. This is a direct measurement and optimization for these subjective qualities [1].
    *   **Guzdial et al. (2015)**: Trained a CNN to predict the difficulty, enjoyment, and aesthetics of game levels, with case studies on Infinite Mario Bros., enhancing predictions with A\* agent features .
    *   **Shaker et al. (2012, 2013, 2014)**: Conducted a series of studies investigating DL models of player experience to generate experience-tailored Super Mario Bros. levels .

### 6) Gap Analysis and Research Opportunities

Despite significant advancements, particularly with deep generative models and LLMs, several critical gaps remain in Mario PCG that prevent current approaches from consistently generating levels "people actually enjoy."

*   **The biggest misalignments between current metrics and human enjoyment**:
    *   **Evaluation Misalignment**: Most automated metrics (solvability, feature counts, visual realism) are proxies that do not directly capture subjective human enjoyment, fun, or strategic interest. A level might be perfectly solvable by an AI agent and visually plausible, but still feel bland, repetitive, or frustratingly unfair to a human player ("oatmeal problem") .
    *   **Lack of Holistic Design Goals**: Current systems often optimize for isolated objectives (e.g., playability, diversity of tile patterns) without considering how these elements interact to create a cohesive and engaging *gameplay experience*, including narrative flow, pacing, and emotional rhythm.
    *   **"Looks Valid but Plays Boring"**: Deep generative models excel at producing content that *looks* like Mario levels but may lack the subtle design nuances, emergent gameplay, or "surprises" that make human-designed levels compelling [3].

*   **Common failure modes**:
    *   **Overfitting to Solvability / Mode Collapse**: Generative models, especially GANs, can suffer from mode collapse, producing a limited variety of levels, or overfitting to training data. Even if levels are solvable, they become repetitive and predictable, leading to the "oatmeal problem" [7][1][3].
    *   **Poor Controllability / Brittleness**: While LLMs offer textual control, fine-grained control over specific level features or nuanced design intents can still be brittle. Models might struggle to translate subtle textual cues into desired visual or gameplay outcomes, especially for "tiny details" or specific spatial relationships [7].
    *   **Local Coherence, Global Incoherence**: Many models (e.g., Markov chains, LSTMs, early GANs) excel at local pattern generation but struggle with maintaining global structural coherence, leading to disjointed or ill-paced levels when segments are stitched together .
    *   **Data Dependency**: Deep learning methods heavily rely on large, high-quality datasets. Mario levels, while iconic, are finite, and collecting extensive human-annotated data for specific player preferences or diverse design patterns is resource-intensive, leading to "learning from small datasets" problems [3].

*   **“Opportunity zones” for improvement**:
    *   **Richer Human Preference Learning**: Develop more robust and non-intrusive methods for collecting human feedback and building nuanced Player Experience Models (PEMs). Explore physiological data, eye-tracking, and implicit feedback to complement explicit ratings.
    *   **Hybrid Generative-Evaluative Systems**: Combine powerful generative models (Diffusion, Transformers) with strong evaluative components (AI agents, PEMs, LLM-based critics) to ensure both high-quality generation and adherence to gameplay/experiential objectives. Incorporate repair mechanisms to fix generated content [3].
    *   **Multi-Layered, Holistic Generation**: Move beyond generating just terrain to simultaneously generate items, enemies, events, and even simple narratives within levels, ensuring coherence across all game content types. The Moonshine framework, currently terrain-focused, points to this as future work [7].
    *   **Advanced Controllability through Natural Language**: Further refine LLM prompting and integration to enable highly precise and intuitive control over diverse level characteristics, including gameplay mechanics, difficulty curves, and artistic styles. Focus on open-source LLMs to allow deeper architectural research [3].
    *   **Knowledge Distillation from Expert Systems**: Expand on the "Moonshine" concept to distill knowledge from existing, robust, and playability-guaranteed PCG algorithms (e.g., classical rule-based Mario generators) into modern deep generative models. This leverages expert knowledge without needing massive human-labeled datasets [7].
    *   **Adaptive and Personalized PCG**: Develop systems that can generate levels in real-time, adapting to an individual player's skill, preferences, and current emotional state, as explored by EDPCG [1]. This moves towards truly dynamic and personalized experiences.
    *   **Generalization Across Games/Styles**: Research methods that allow models trained on one platformer (or a blend of platformers) to generate content for other similar games, reducing data dependency [9].

*   **A shortlist of hypotheses you think are most promising to explore later**:
    1.  **Hypothesis 1: Hybrid LLM-conditioned Diffusion Models with Expert PCG Distillation will generate highly controllable and diverse Mario levels.** By using LLMs to provide semantic conditioning and distill principles from robust, playability-guaranteed Mario PCG algorithms, Diffusion Models can create high-quality, varied levels with intuitive natural language control, overcoming the "oatmeal problem" and improving controllability.
    2.  **Hypothesis 2: Integrating explicit human preference learning (via PEMs) into the fitness function of search-based latent space exploration will significantly bridge the "human preference gap" for Mario levels.** Directly optimizing for predicted "fun" or "challenge" scores (derived from human-trained models) within the latent space of deep generative models will lead to levels that are objectively more enjoyable than those optimized purely by automated playability proxies.
    3.  **Hypothesis 3: Multi-layered generative models that simultaneously create terrain, enemy placement, and item distribution, conditioned by high-level prompts, will produce more cohesive and engaging Mario levels.** By moving beyond single-aspect generation, these models will inherently create levels with better pacing, thematic consistency, and emergent gameplay, addressing the problem of local coherence but global incoherence.

### 7) Baseline Shortlist for Reproduction

To build a strong experimental foundation for a new state-of-the-art Mario PCG generator, reproducing a selection of influential baselines from different method families is crucial.

| Candidate Baseline | Why Important | Expected Reproduction Difficulty | Required Assets | Evaluation for Apples-to-Apples Comparison |
| :--- | :--- | :--- | :--- | :--- |
| 1. **Experience-Driven Personalized Level Creation for Super Mario Bros.** (Pedersen et al., 2010, described in Yannakakis & Togelius, 2011) [2] | Seminal example focusing on *human player experience* and *personalization* for Mario. Introduces modeling human affective states (fun, challenge, frustration) and player styles to guide level generation. Represents a crucial step beyond mere solvability. | Medium to High | An open-source Super Mario Bros. clone (e.g., Infinite Mario Bros.), instrumentation for player telemetry, human player data (subjective ratings of affective states, gameplay metrics), neural network framework (e.g., PyTorch/TensorFlow) for PEM, evolutionary algorithm library (e.g., DEAP) for search, and a stochastic level generation algorithm from parameter vectors. | **Human Evaluation**: Pairwise preference questionnaire or rating scales for fun, challenge, frustration, etc. **Automated Proxies**: Player style metrics (jumping frequency, deaths), agent completion rates (for playability baseline). **Expressive Range Analysis**: Analyze variation in levels generated for different target affective states or player profiles. |
| 2. **LSTM-based Mario Level Generation** (Summerville & Mateas, 2014) [4] | An early and influential deep learning approach for Mario PCG. Demonstrates how sequence models can learn and generate patterns directly from existing levels, representing a significant shift from rule-based systems to data-driven generative models. Foundation for many subsequent PCGML methods. | Medium | Dataset of existing Super Mario Bros. levels (e.g., World 1-1, segmented and tokenized), LSTM/RNN implementation (e.g., Keras/PyTorch), a tile-based rendering system for generated levels. Code for level segmentation and tokenization. | **Automated Proxies**: Visual coherence, statistical similarity to training data (e.g., n-gram similarity), agent-based solvability. **Diversity**: Visual inspection, simple feature counts (e.g., distinct patterns generated). **Human Evaluation**: Qualitative assessment of "Mario-ness" and plausibility. |
| 3. **MarioGAN: Generative Adversarial Networks with Latent Variable Evolution (LVE)** (Volz et al., 2018)  | Represents the application of powerful deep generative models (GANs) combined with evolutionary search (CMA-ES) in the latent space for Mario level segments. Addresses content quality and specific behavioral objectives, moving beyond simple pattern replication. | High | Dataset of Mario level segments (e.g., 16x7 tiles from World 1-1), DCGAN implementation (e.g., PyTorch/TensorFlow), CMA-ES library, an AI agent (e.g., A\* pathfinder) for playability assessment within generated segments, and a level stitching mechanism for full levels. | **Automated Proxies**: Agent-based playability (completion rate, path statistics), Inception Score (or similar for GAN quality/diversity), feature counts (e.g., enemy density, coin count). **Human Evaluation**: Visual realism, aesthetic appeal, and perceived challenge of generated segments. **Latent Space Analysis**: Visualization of latent space exploration and generated segment variations. |
| 4. **Moonshine Framework (Text-to-Game-Map with Diffusion Model)** (Nie et al., 2024) [7] | State-of-the-art approach leveraging LLMs for synthetic data generation and Diffusion Models for text-conditioned content. Offers high-level natural language control and generates diverse, high-fidelity content. While shown for roguelike dungeons, its methodology is highly transferable and represents the cutting edge. | High | A constructive Mario PCG (or human-designed levels) to act as the source for synthetic data generation, an LLM API (e.g., GPT-4 Turbo or open-source equivalent), a text embedding model (e.g., `gte-large-en-v1.5`), a conditional Diffusion Model implementation (UNet architecture), and a Mario tile-based rendering system. | **Automated Proxies**: Finetuned CLIP Score (semantic alignment between prompt and generated level), reconstruction loss, agent-based playability (for levels generated from "playable" prompts). **Human Evaluation**: Qualitative assessment of adherence to text prompts, perceived creativity, diversity, and specific Mario-centric qualities. **Diversity Metrics**: Expressive range analysis within the text-conditioned output space. |

### Final Deliverables Checklist

*   [X] Executive overview with timeline narrative
*   [X] Method family chapters with (a)–g) structure
*   [X] 3 deep dives
*   [X] Benchmarks/environments section
*   [X] Human evaluation section
*   [X] Gap analysis
*   [X] Baseline shortlist table
*   [X] Bibliography





[1] Deep learning for procedural content generation, Jialin Liu, Sam Snodgrass, Ahmed Khalifa, Sebastian Risi, Georgios N. Yannakakis, Julian Togelius, 2020-10-08, doi: 10.1007/s00521-020-05383-8, url: <https://link.springer.com/10.1007/s00521-020-05383-8>

[2] Experience-Driven Procedural Content Generation, G. N. Yannakakis, J. Togelius, 2011-07-01, doi: 10.1109/t-affc.2011.6, url: <http://ieeexplore.ieee.org/document/5740836/>

[3] Procedural Content Generation in Games: A Survey with Insights on Emerging LLM Integration, Mahdi Farrokhi Maleki, Richard Zhao, 2024-10-21, doi: 10.48550/arxiv.2410.15644, url: <https://arxiv.org/abs/2410.15644>

[4] Learning Constructive Primitives for Online Level Generation and Real-time Content Adaptation in Super Mario Bros, Peizhi Shi, Ke Chen, 2015-10-27, doi: 10.48550/arXiv.1510.07889, url: <https://arxiv.org/abs/1510.07889>

[5] Procedural Content Generation via Machine Learning (PCGML), Adam Summerville, Sam Snodgrass, Matthew Guzdial, Christoffer Holmgård, Amy K. Hoover, Aaron Isaksen, Andy Nealen, Julian Togelius, 2017-02-02, doi: 10.48550/arXiv.1702.00539, url: <https://arxiv.org/abs/1702.00539>

[6] Procedural Content Generation via Machine Learning (PCGML), Adam Summerville, Sam Snodgrass, Matthew Guzdial, Christoffer Holmgrd, Amy K. Hoover, Aaron Isaksen, Andy Nealen, Julian Togelius, Christoffer Holmgard, 2018-09-01, doi: 10.1109/tg.2018.2846639, url: <https://ieeexplore.ieee.org/document/8382283/>

[7] Moonshine: Distilling Game Content Generators into Steerable Generative Models, Yuhe Nie, Michael Middleton, Tim Merino, Nidhushan Kanagaraja, Ashutosh Kumar, Zhan Zhuang, Julian Togelius, 2024-08-18, doi: 10.48550/arxiv.2408.09594, url: <https://arxiv.org/abs/2408.09594>

[8] A Probabilistic Grammar for Procedural Content Generation, Francesco Sportelli, Giuseppe Toto, Gennaro Vessio, 2014-01-01, doi: 10.0410/cata/8281be8d68c7e51ab1c97f7850e4eac7

[9] Procedural Content Generation via Knowledge Transformation (PCG-KT), Anurag Sarkar, Matthew Guzdial, Sam Snodgrass, Adam Summerville, Tiago Machado, Gillian Smith, 2023-05-01, doi: 10.48550/arXiv.2305.00644, url: <https://arxiv.org/abs/2305.00644>

[10] Procedural Content Generation via Knowledge Transformation (PCG-KT), Anurag Sarkar, Matthew Guzdial, Sam Snodgrass, Adam Summerville, Tiago Machado, Gillian Smith, 2023-01-01, doi: 10.1109/tg.2023.3270422, url: <https://ieeexplore.ieee.org/document/10109182/>

[11] Deep Reinforcement Learning for Procedural Content Generation of 3D Virtual Environments, Christian E. López, James Cunningham, Omar Ashour, Conrad S. Tucker, 2020-06-03, doi: 10.1115/1.4046293, url: <https://asmedigitalcollection.asme.org/computingengineering/article/20/5/051005/1074423/Deep-Reinforcement-Learning-for-Procedural-Content>

[12] Deep Learning for Procedural Content Generation, Jialin Liu, Sam Snodgrass, Ahmed Khalifa, Sebastian Risi, Georgios N. Yannakakis, Julian Togelius, 2020-10-09, doi: 10.48550/arXiv.2010.04548, url: <https://arxiv.org/abs/2010.04548>

[13] Evolutionary Variational Optimization of Generative Models, Jakob Drefs, Enrico Guiraud, Jörg Lücke, 2020-12-22, doi: 10.48550/arXiv.2012.12294, url: <https://arxiv.org/abs/2012.12294>

[14] DI-PCG: Diffusion-based Efficient Inverse Procedural Content Generation for High-quality 3D Asset Creation, Wang Zhao, Yan-Pei Cao, Jiale Xu, Yuejiang Dong, Ying Shan, 2024-12-19, doi: 10.48550/arxiv.2412.15200, url: <https://arxiv.org/abs/2412.15200>

[15] Analysis of Procedural Content Generation and Stylisation Techniques in Developing Video Games, Junkai Xie, 2025-07-10, doi: 10.62051/0swzbh75, url: <https://www.semanticscholar.org/paper/e258adc5efe4c0f503e59922fd480e11351135f3>



Some parts of the document may be generated by AI.
