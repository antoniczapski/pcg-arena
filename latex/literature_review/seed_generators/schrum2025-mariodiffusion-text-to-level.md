

## Page 1

Text-to-Level Diffusion Models With Various Text Encoders for Super Mario Bros
Jacob Schrum, Olivia Kilday, Emilio Salas, Bess Hagan, Reid Williams
Southwestern University
Georgetown, TX, USA
{schrum2,kildayl,salas2,haganb,williamsr}@southwestern.edu
Abstract
Recent research shows how diffusion models can uncondi-
tionally generate tile-based game levels, but use of diffusion
models for text-to-level generation is underexplored. There
are practical considerations for creating a usable model: cap-
tion/level pairs are needed, as is a text embedding model, and
a way of generating entire playable levels, rather than indi-
vidual scenes. We present strategies to automatically assign
descriptive captions to an existing dataset, and train diffusion
models using both pretrained text encoders and simple trans-
former models trained from scratch. Captions are automati-
cally assigned to generated scenes so that the degree of over-
lap between input and output captions can be compared. We
also assess the diversity and playability of the resulting level
scenes. Results are compared with an unconditional diffusion
model and a generative adversarial network, as well as the
text-to-level approaches Five-Dollar Model and MarioGPT.
Notably, the best diffusion model uses a simple transformer
model for text embedding, and takes less time to train than
diffusion models employing more complex text encoders, in-
dicating that reliance on larger language models is not neces-
sary. We also present a GUI allowing designers to construct
long levels from model-generated scenes.
Introduction
Modern generative AI models use natural language input to
create outputs in various modalities, including text, image,
sound, and video. These technologies have also been applied
to Procedural Content Generation (PCG), “the algorithmic
creation of game content with limited or indirect user input”
(Shaker, Togelius, and Nelson 2016). The use of generative
AI classifies these methods as PCG via Machine Learning
(PCGML) (Summerville et al. 2018).
Many models have been used to generate levels for Su-
per Mario Bros. and other tile-based games, including Long
Short-Term Memory networks (Summerville and Mateas
2016), Generative Adversarial Networks (GANs) (Volz et al.
2018), Variational Autoencoders (VAEs) (Thakkar et al.
2019), Large Language Models (LLMs) (Sudhakaran et al.
2023), the Five-Dollar Model (FDM) (Merino et al. 2023),
and diffusion models (Lee and Simo-Serra 2023). LLMs
and FDM are text-guided, whereas diffusion models can be
Copyright © 2025, Association for the Advancement of Artificial
Intelligence (www.aaai.org). All rights reserved.
trained unconditionally or with text guidance. Although the
use of text guidance in diffusion models is common in popu-
lar models like Stable Diffusion (Rombach et al. 2022), text-
guidance seems underexplored in the realm of tile-based
game level generation, which is the focus of this paper.
Though it is no surprise that diffusion models can be used
for this purpose, there are still many practical considerations
in training a working model, including procuring a dataset of
adequately descriptive captions, selecting a text embedding
model to pair with diffusion, and creating levels of the de-
sired size with the finished model. These issues are explored
in this paper. Specifically, our contributions are:
1. A method for automatically assigning captions to Mario
level scenes that could be generalized to other domains
given sufficient expert knowledge.
2. A method of assessing the quality of text-conditioned
generation that depends on the ability to automatically
assign captions to scenes.
3. A demonstration of how to use various types of text
embedding models, both pretrained and trained from
scratch, in a text-to-level diffusion pipeline.
4. A comparison of various text embedding approaches in
terms of adherence to input prompts, training time, di-
versity, and playability, which ultimately concludes that
a simple transformer model with a limited vocabulary re-
sults in the best diffusion models.
5. A mixed-initiative GUI that can be used to combine
model-generated scenes into larger levels.
Related Work
Many generative PCGML models exist. Relevant work is
split into unconditional models (no language input) and text
conditional models (using natural language).
Unconditional Models
Early work in PCGML used models like Long Short-Term
Memory networks (Summerville and Mateas 2016) to gen-
erate Mario levels. A survey of other early PCGML ap-
proaches came out in 2018 (Summerville et al. 2018)
That
same
year,
Generative
Adversarial
Networks
(GANs) (Goodfellow et al. 2014) for level generation were
introduced (Volz et al. 2018). This work also applied latent
arXiv:2507.00184v2  [cs.LG]  15 Aug 2025


## Page 2

variable evolution (Bontrager et al. 2018) to find scenes with
desired properties for Mario. Use of GANs for level genera-
tion was quickly expanded upon. GANs were combined with
Graph Grammars (Gutierrez and Schrum 2020) and interac-
tive evolution (Schrum et al. 2020) to generate Zelda lev-
els. Compositional Pattern Producing Networks were used
to combine GAN-generated level scenes into global patterns
(Schrum, Volz, and Risi 2020; Schrum et al. 2023). Mixed
Integer Programming was used to repair levels discovered
by latent quality diversity evolution (Fontaine et al. 2021).
The ability to generate samples from a single input was ex-
plored in both Mario (Awiszus, Schubert, and Rosenhahn
2020) and Minecraft (Awiszus, Schubert, and Rosenhahn
2021). Levels for multiple games were generated by a single
GAN trained to induce a common latent space on data from
multiple games (Kumaran, Mott, and Lester 2020).
The concept of searching a latent space to generate
levels was also explored with Variational Auto-Encoders
(VAEs) (Kingma and Welling 2014). The earliest applica-
tion of this was to Lode Runner (Thakkar et al. 2019). Later
work showed how to blend concepts across multiple games
(Sarkar, Yang, and Cooper 2020), and used VAEs for latent
quality diversity evolution (Sarkar and Cooper 2021).
Recently, diffusion models (Yang et al. 2023) have risen
to prominence. They generate content via an iterative de-
noising process using a convolutional UNet. Diffusion mod-
els predict the presence of noise in a noisy image, so that
said noise can be removed to produce a clean image. Trained
models start with pure noise and derive quality output from
it. A popular example is Stable Diffusion (Rombach et al.
2022), which adds text conditioning to the UNet and com-
bines it with a VAE so that diffusion is performed in a com-
pressed latent space rather than at the scale of the full image.
Stable Diffusion was the basis of research in the game
Doom showing how diffusion models can function as semi-
playable game engines (Valevski et al. 2024). The model
was trained to predict the next screen frame conditioned on
actions taken by a Reinforcement Learning agent (actions
replaced text embeddings). A similar approach was used to
simulate playing Super Mario Bros (Virtuals Protocol 2024).
Though impressive, these models try to reproduce the
game experience rather than generate new content, but there
are recent examples of generating levels with diffusion. Un-
conditional diffusion models can indeed generate convinc-
ing Mario level scenes when trained on scenes from the orig-
inal game (Lee and Simo-Serra 2023). Dai et al. (2024) took
individual Mario/Minecraft levels and used an unconditional
diffusion model to generate new levels at different scales that
share the distribution of elements from that one sample.
These methods produce playable levels, but lack control
from text guidance. This is why evolution has often been
combined with unconditional models to produce desired re-
sults, but defining a fitness function is generally more chal-
lenging than describing what is desired, so the next section
describes PCGML approaches guided by text inputs.
Text-Conditional Models
Despite the frequent association of diffusion models with
text guidance (e.g. Stable Diffusion), there is not much work
applying text conditioning to diffusion models for level gen-
eration. An exception is recent work on Text-to-game-Map
(T2M) models trained as part of the Moonshine system (Nie
et al. 2025), though the primary focus of Moonshine is the
generation of synthetic captions by an LLM for the sake of
training T2M models. The diffusion model from Moonshine
relies on a model which we refer to as GTE below, as it is
one approach to text embedding that we apply.
Text-to-Level approaches not based on diffusion also ap-
pear in the literature. Another model in the Moonshine pa-
per is the Five-Dollar Model (FDM) (Merino et al. 2023),
a feed-forward model whose name emphasizes its minimal
computational requirements. Previous FDM results indicate
it is useful despite its simplicity, but it struggles with over-
fitting and lack of diversity in outputs.
Level generation with variants of the Large Language
Model (LLM) GPT2 from OpenAI (Radford et al. 2019)
has been demonstrated in both Sokoban (Todd et al. 2023)
and Super Mario Bros (Sudhakaran et al. 2023). We com-
pare against this publicly available MarioGPT model below,
though the complexity of the text prompts it understands is
less ambitious than what our models are capable of.
Methods
We outline how training scenes are collected and com-
bined with generated captions before training text embed-
ding models, and then text-to-level diffusion models.
Training Data
Full levels are from Super Mario Bros. and the Japanese Su-
per Mario Bros. 2, a.k.a. The Lost Levels, which was not
initially released outside of Japan. This data comes from
the Video Game Level Corpus (VGLC) (Summerville et al.
2016), a repository with data for several games. Despite be-
ing widely used (Volz et al. 2018; Sudhakaran et al. 2023;
Lee and Simo-Serra 2023), the data has numerous errors
and omissions, so we use our own manually cleaned ver-
sion that is closer to data from the real games1, and adds
back some missing levels. However, we retain the limitation
of representing enemies with a single symbol interpreted as
a Goomba. We thus have 13 tile types.
As in previous works (Volz et al. 2018; Lee and Simo-
Serra 2023), characters for each tile correspond to inte-
gers that are one-hot encoded. This approach has proven
sufficient for us and others, though vector-based block/tile
embeddings have also been used (Awiszus, Schubert, and
Rosenhahn 2021; Dai et al. 2024). Such an approach could
be useful, but is not explored in this paper.
To extract data, a window slides over each level one tile
at a time. Mario levels are 14 tiles high, but because the ar-
chitectural components of our diffusion model are easier to
define when input sizes are powers of 2, we pad the tops of
levels to create 16 × 16 samples.
Creating descriptive captions for each scene is more com-
plicated. The Moonshine system (Nie et al. 2025) mentioned
previously uses LLMs to create suitable captions for level
data, but we use a deterministic approach. Concepts from
1https://github.com/schrum2/TheVGLC


## Page 3

Mario scenes are manually defined, and scenes are scanned
for the presence and quantity of these concepts, resulting in
up to one phrase ending in a period for each concept. The
full list of concepts and how they are defined is here:
• Floor: Blocks on the bottom row. Can have gaps, or be a
void with small floor chunks.
• Ceiling: Blocks in fourth row filling at least half of the
row. Can have gaps.
• Pipe: Four correctly arranged tiles of a pipe with neck
tiles extended to a solid base or the bottom of the screen.
• Upside down pipe: Pipe with opening at the bottom and
neck that extends to a solid top or the top of the screen.
• Coin Line: Adjacent coins in the same row.
• Coin: Coin tiles. Includes coins in lines.
• Cannon: Cannon tiles.
• Question Block: Both types of question block tiles.
• Enemy: Enemy tiles.
• Platform: Adjacent solid tiles in the same row, with the
rows above and below being empty/passable.
• Tower: Collection of contiguous blocks with a width less
than three and a height of at least three.
• Ascending Staircase: Solid tiles with empty space above
where height increases by one for each move to the right.
Sequence is at least three columns wide.
• Descending Staircase: Like ascending staircase, but
height decreases by one while moving right.
• Rectangular Cluster: Flood-filled rectangular cluster of
contiguous solid blocks. Flood fill excludes previously
identified structures.
• Irregular Cluster: Remaining flood-filled clusters of at
least three contiguous blocks not captured earlier.
• Loose Block: Solid blocks not captured earlier.
Most concepts include a quantity: “one”, “two”, “a few”
(3-4), “several” (5-9), or “many” (10 or more). The floor
concept distinguishes between “full floor” and one with
some number of gaps. If over half of the floor is missing,
it is a “giant gap” with some number of “chunks of floor”,
though some levels have no floor. Similarly, a ceiling is ei-
ther “full” or has some number of gaps.
This captioning style is the regular approach. How-
ever, we also consider absence captions, in which every
concept missing from a scene is explicitly mentioned, as in
“no floor.” The absence captions always have the same
number of phrases, whereas the number in regular cap-
tions varies. Examples of each captioning approach are in
Figure 1a. To encourage flexibility in using the models, the
order of the phrases in training captions is randomized.
We can also assign captions to artificial scenes output by
our models, which is useful for assessing model controlla-
bility later. When assigning captions to model output, two
additional concepts are potentially present:
• Broken Pipes: Portions of a pipe that lack one of the four
required tiles, or place them inappropriately.
• Broken Cannons: When a cannon support tile appears
without a cannon tile on top.
These concepts are never present in training data.
(a) Real Scene
(b) Generated Scene
Figure 1: Real and Generated Level Scenes. (a) A scene from
the data. Its captions are: regular: “full floor. one enemy.
a few question blocks. one platform. one pipe.” absence:
“full floor. no ceiling. one enemy. a few question blocks. no
cannons. no coins. no coin lines. one platform. no ascend-
ing staircases. no descending staircases. one pipe. no upside
down pipes. no towers. no rectangular block clusters. no ir-
regular block clusters. no loose blocks.” negative: “ceil-
ing. cannon. coin. coin line. ascending staircase. descending
staircase. upside down pipe. tower. rectangular block cluster.
irregular block cluster. loose block.” (b) Model-generated
scene. Input prompt: “floor with one gap. a few platforms.
a few enemies. a few coins. one coin line. a few towers. one
ascending staircase. a few question blocks.” Actual caption:
“full floor. two enemies. one ascending staircase. two ques-
tion blocks.” Resulting caption adherence score: 0.478.
Text Embedding Models
The text-conditional models in Related Work depend on
pretrained language models to embed text input for the
level generator. Leveraging existing models allows for open-
ended text input. However, game environments are con-
strained, so a large vocabulary is not necessary. Therefore,
we train a simple model from scratch on limited vocabulary.
The simple architecture we use is a standard transformer
encoder that learns token embeddings of length 128. Full
details are in the appendix, but we allow multiple trans-
former encoder layers with multi-headed self-attention. Dur-
ing training, the model is given a sequence of token IDs,
and encodes them with an embedding layer. These embed-
dings are combined with sinusoidal positional encodings
and passed through the transformer layers where the atten-
tion mechanism enriches the embedded representations with
surrounding context. For the sake of training, these embed-
dings are passed through a final linear layer that outputs log-
its for each token at each position. Masked Language Mod-
eling is used during training, so we refer to this model as
MLM. This means that some input tokens are probabilistically
replaced with a special MASK token, but the model must
predict the correct tokens from surrounding context. The re-
sult is token embeddings that capture semantic information
about their context in sentences from the training data.
MLM is a small model trained on a small dataset with
a small vocabulary, so it trains quickly and is effective
at modeling the restricted grammar in our captions. How-


## Page 4

ever, MLM cannot tolerate tokens not present in its training
data. In contrast, pretrained language models have been used
in previous text-to-level systems, and can accept arbitrary
tokens outside our limited vocabulary. The original FDM
paper (Merino et al. 2023) used the sentence transformer
multi-qa-MiniLM-L6-cos-v1 (MiniLM). MiniLM
maps whole sentences to vectors of length 384, and was
designed for semantic search. Later research with Moon-
shine (Nie et al. 2025) combined FDM and a diffusion model
with gte-large-en-v1.5 (GTE) (Zhang et al. 2024).
GTE embeds entire documents into vectors of length 1024.
Although these models allow arbitrary tokens, such tokens
have little meaning in Mario, and even familiar tokens are
used differently in our captions than in natural language.
Therefore, further fine-tuning of these sentence transform-
ers could be useful, but this is left for future work.
An alternative approach that is explored takes advantage
of the form of our captions: collections of period-separated
phrases. The default approach embeds each caption as a
single vector, but these phrases can be embedded indi-
vidually to create multiple vectors to provide to the diffu-
sion model. Both approaches are applied in our experiments.
Diffusion Model
The diffusion model is a conditional UNet with 13 in/out
channels: one per tile type. It has three convolutional down-
sampling stages and three up-sampling stages. Each contains
residual blocks with SiLU activations and skip connections
to preserve spatial information and avoid disappearing gra-
dients, as well as cross-attention to allow text-embedding
input from the language models described in the previous
section. The 13 channels project to 128 channels, then 256,
then 512 at the bottleneck before reversing the sequence. An
unconditional model can be easily made by removing the
cross-attention, and is done for the sake of comparison with
an approach similar to that of Lee and Simo-Serra (2023).
We use classifier-free guidance, meaning the model is
trained to handle both conditional and unconditional inputs,
allowing stronger guidance at inference by interpolating be-
tween the two. Specifically, the text conditional model is
trained on each sample using both text embeddings and an
empty embedding vector. Effectively doubling the samples
increases training time in comparison with an unconditional
model. We can use regular or absence captions, but
there is also a third option. Instead of indicating the absence
of items in the caption, we can train with distinct negative
prompts. Because all possible concepts are known, we can
take each regular caption and make a separate negative
prompt listing all concepts that are absent. Now for each
sample, a third copy is paired with the negative prompt for
negative guidance. This negative caption approach takes
even longer to train since it triples the number of samples.
An example scene with all captions is in Figure 1a.
The diffusion model is given noisy one-hot encoded level
scenes as input, and tries to predict the noise that would need
to be removed to get the original input. The loss function is
a weighted sum of mean squared error (MSE) and categori-
cal cross-entropy (reconstruction loss), as in Lee and Simo-
Serra (2023). Detailed diffusion diagram in appendix.
Experiments
We train numerous models, and evaluate them with various
metrics. All models were trained on different lab machines
sharing the same hardware: Alienware, 13th Gen Intel®
Core™i9-13900F with 24 cores at base speed of 2.0GHz,
32 GB RAM, NVIDIA GeForce RTX 4060 with 8 GB ded-
icated VRAM and 15.9 GB shared VRAM. These are rea-
sonably powerful gaming PCs. Detailed parameter settings
and additional results are available in an appendix at https:
//people.southwestern.edu/∼schrum2/mario.html and source
code for recreating our results along with selected models
are available at https://github.com/schrum2/MarioDiffusion.
Dataset Preparation
We use a 90/5/5-split of the 7,687 samples from the two
Mario games to get training, validation, and test sets of sizes
6,918, 384, and 385. Care is taken to assure that all three
datasets contain representation of all possible concepts. For
training both text and diffusion models, data is augmented
via random shuffling of phrases within captions. Validation
data is used during training to determine the best model
to keep, and test data is used for evaluation after training.
We also make a set of 100 randomly generated captions not
present in the original data for further testing. Each contains
random phrases for 1 to 10 randomly selected topics.
Training Text Embedding Models
We train a separate MLM text encoder for each diffu-
sion model that uses one. Models using regular and
absence captions are trained with those caption types,
though MLM models for negative captions also use
regular data. Each model is trained for 300 epochs us-
ing AdamW with cross-entropy loss, but the lowest valida-
tion loss is logged every epoch, and the model with the best
validation loss is kept as the final model.
Training Text-Conditioned Diffusion Models
For each text embedding approach and caption style, we
train as many models as practical given compute costs.
We train models with different random seeds for each
caption style: 10 MLM, 10 MiniLM-single, 5 MiniLM
-multiple, 5 GTE-single, and 1 GTE-multiple.
Models are trained with AdamW for 500 epochs using a
cosine learning rate schedule and a warm-up period. To pre-
vent overfitting, the caption adherence score defined later in
Equation 1 is computed every 20 epochs across all valida-
tion captions, so the final model is whichever one had the
best average c-score. The average c-score is a better mea-
sure of model performance than the usual validation loss.
Comparison Models
For comparison, we train several other models. We train 30
unconditional diffusion models for 500 epochs in a manner
similar to Lee and Simo-Serra (2023). Since there are no
captions, best model is determined by the lowest validation
loss. We also train 30 Wasserstein GANs (WGANs) follow-
ing the methodology of Volz et al. (2018), meaning we train
for 5,000 epochs and the final model is from the final epoch.


## Page 5

Five-Dollar Models (FDMs) (Merino et al. 2023) are
trained using MiniLM and GTE as embedding models with
regular and absence captions (30 models per combi-
nation). As input, FDM takes a sentence embedding vector
and a noise vector of length 5. As a text-conditioned model,
FDM checks caption adherence score on validation data ev-
ery 10 epochs to determine the best final model. However,
our experience confirms the observation from previous work
that FDM is prone to overfitting, so it is only trained for
100 epochs. Although the caption adherence scores for FDM
show a general upward trend (with occasional dips), valida-
tion loss increases after an initial dip early in training.
We also compare against MarioGPT’s publicly available
model (Sudhakaran et al. 2023), but do not train our own
version. MarioGPT’s repertoire of training captions is com-
paratively limited, based on only 96 combinations (barring
the use of arbitrary integer quantities). We use each caption
to generate a level 128 blocks long and slice each into 8
scenes, from which 100 scenes are sampled.
Measuring Performance
Caption Adherence Score
We focus on the ability of
text-to-level models to produce scenes matching their input
prompts. As indicated earlier, we can automatically assign
captions to any level scene, including output from trained
models. Output captions can be compared to their corre-
sponding input prompts to define a caption score (c-score):
c-score(p, c) =
P
t∈T match(phrase(t, p), phrase(t, c))
|T|
(1)
match(pt, ct) =









1.0
for pt = ct
1.0 −|qu(pt)−qu(ct)|
|Q|−1
for co(pt) ∧co(ct)
0.1
for pt ̸= ∅∧ct ̸= ∅
−1.0
otherwise
(2)
p is a prompt. c is a caption describing the scene produced
from p. T is the set of caption concepts for Mario levels.
phrase(t, s) returns the phrase in s associated with concept
t, or ∅if there is no such phrase or it starts with “no” (pos-
sible for absence captions). co(st) is for countable, and
indicates whether st describes a quantity (phrases like “full
floor” do not). qu(st) returns an integer that orders quanti-
ties: “one” = 0 up to “many” = 4. Q is the set of quantities.
So, match(pt, ct) takes two phrases about the same con-
cept, and returns 1.0 if they are identical (first case), a value
from 0.0 to 1.0 if there is a partial match (second and third
cases), and -1.0 if one phrase indicates the concept is com-
pletely absent, but the other does not. If both phrases indicate
that some quantity of the concept is present, then smaller dif-
ferences in quantities result in higher results. The third case
returns 0.1 when one phrase has a quantity and the other
does not, which only happens when comparing a full floor
or ceiling to one with some amount of empty space.
The c-score(p, c) calculation is simply the average
match(pt, ct) score across all topics, which means it is
scaled from the range -1.0 to 1.0. An example comparison
and resulting c-score are in Figure 1b.
End Time and Best Time
A model’s training time is also
relevant. We define End Time as the time required to com-
plete the final epoch, and Best Time as the time required to
reach the checkpoint with the best validation performance.
Best Time is relevant since early stopping could hopefully
end training shortly after a model reaches its best perfor-
mance. Note that times for MLM diffusion models include the
additional training time for the actual MLM text encoders.
Average Minimum Edit Distance
This metric measures
the variety of levels within a set. Levels are compared in
terms of edit distance. The average minimum edit distance
AMEDself across a set of level scenes S is
AMEDself(S) =
P
s∈S argminx∈(S−{s})dist(s, x)
|S|
(3)
A high AMEDself score means most levels are very dif-
ferent from each other. A low score means most levels are
similar to other levels in the set. As a set of limited possibil-
ities grows, closer neighbors are more likely to be found, so
comparison of sets with equal sizes is important for fairness.
Average minimum edit distance can also be defined with
respect to real game data to define AMEDreal:
AMEDreal(S) =
P
s∈S argminx∈Rdist(s, x)
|S|
(4)
R is the set of real game samples. High AMEDreal scores
indicate large differences between generated and real levels.
Solvability
A level scene is considered solvable if Robin
Baumgarten’s A* agent (Togelius, Karakovskiy, and Baum-
garten 2010) can beat it, though this widely used agent is
not perfect (ˇSosvald et al. 2021), and we have observed un-
usual failure cases. Furthermore, it is not always the agent’s
fault that a scene cannot be beaten. Although complete levels
are beatable, slicing them into 16 × 16 samples sometimes
results in the loss of a platform or other element that is re-
quired to traverse the remainder of the scene. Only 7,160 of
the 7,687 samples are solvable, approximately 93%.
Level Integrity
In model output, tiles for pipes and can-
nons are sometimes arranged incorrectly. The broken pipe
issue was first recognized when generating Mario levels with
GANs (Volz et al. 2018). There are trivial ways to repair bro-
ken features or change the data encoding so that they cannot
appear (Schrum, Volz, and Risi 2020), but forcing the mod-
els to learn how to build such structures provides us another
way to assess them. Therefore, the percentage of generated
scenes with broken pipes and cannons is reported.
Results
Caption Adherence Score
Caption adherence across the
test set prompts from real game scenes is in Figure 2.
Most models earn scores above 0.9 within 500 epochs.


## Page 6

0
100
200
300
400
500
Epoch
0.0
0.2
0.4
0.6
0.8
1.0
Caption Score
MLM-regular
MiniLM-single-regular
MiniLM-multiple-regular
GTE-single-regular
GTE-multiple-regular
FDM-MiniLM-regular
FDM-GTE-regular
(a) regular
0
100
200
300
400
500
Epoch
0.0
0.2
0.4
0.6
0.8
1.0
Caption Score
MLM-absence
MiniLM-single-absence
MiniLM-multiple-absence
GTE-single-absence
GTE-multiple-absence
FDM-MiniLM-absence
FDM-GTE-absence
(b) absence
0
100
200
300
400
500
Epoch
0.0
0.2
0.4
0.6
0.8
1.0
Caption Score
MLM-negative
MiniLM-single-negative
MiniLM-multiple-negative
GTE-single-negative
GTE-multiple-negative
(c) negative
Figure 2: Average Caption Adherence Score by Epoch on Real Game Test Set Captions. The number of runs being averaged
over varies by model type, though GTE-multiple data are based on a single run each. When there is more than one run,
95% confidence intervals are shown, though they are often extremely narrow. Recall that FDM models are trained for a shorter
period due to their overfitting problem. (a) regular models are all good, though MLM peaks faster. FDM starts high but lags
behind. (b) absence results are more varied, with GTE-single and MiniLM-single performing poorly, and MLM once
again on top. FDM results are flatter. (c) negative results are also varied, with MLM once again on top and poor performance
from MiniLM-multiple and GTE-multiple. FDM does not train with negative captions.
0
100
200
300
400
500
Epoch
0.2
0.1
0.0
0.1
0.2
0.3
0.4
Caption Score
MLM-regular
MiniLM-single-regular
MiniLM-multiple-regular
GTE-single-regular
GTE-multiple-regular
FDM-MiniLM-regular
FDM-GTE-regular
(a) regular
0
100
200
300
400
500
Epoch
0.2
0.1
0.0
0.1
0.2
0.3
0.4
Caption Score
MLM-absence
MiniLM-single-absence
MiniLM-multiple-absence
GTE-single-absence
GTE-multiple-absence
FDM-MiniLM-absence
FDM-GTE-absence
(b) absence
0
100
200
300
400
500
Epoch
0.2
0.1
0.0
0.1
0.2
0.3
0.4
Caption Score
MLM-negative
MiniLM-single-negative
MiniLM-multiple-negative
GTE-single-negative
GTE-multiple-negative
(c) negative
Figure 3: Average Caption Adherence Score by Epoch on Random Captions. The 95% confidence intervals are more evident
here. (a) regular models have the highest scores. MLM is the best among them. FDM performance plummets quickly and
GTE-multiple is erratic. (b) absence data mostly has worse scores, though GTE-multiple has a spike before dipping
to meet the other models. Only MiniLM-single is exceptionally low. FDM models maintain performance better in this case.
(c) negative performance is the worst, though MLM is the best in this group. FDM does not train with negative captions.
Among text-conditioned diffusion models, the only excep-
tions are MiniLM-single-absence, GTE-single
-absence, MiniLM-multiple-negative, and GTE
-multiple-negative. FDM models start high, but get
stuck around 0.6 to 0.7 depending on the specific model.
Results across all real data are qualitatively similar (ap-
pendix). In contrast, models have difficulty with random
captions (Figure 3). The highest score is under 0.5, and
is achieved by MLM-regular. Figure 1b shows an ex-
ample scene generated by MLM-regular. Early in train-
ing, GTE-multiple-regular and GTE-multiple
-absence reach the maximum score achieved by MLM
-regular before dropping down. Overfitting by FDM is
evident, as performance peaks and then drops within about
30 epochs. The worst scores are from MiniLM-single
-absence, MiniLM-multiple-negative, and GTE
-multiple-negative. The way some scores drop indi-
cate that random captions may have served better to deter-
mine the best final model than validation captions.
End Time and Best Time
Figure 4a shows average End
Time and Best Time for each model. The text-conditioned
diffusion models with the shortest training times are
MiniLM-single-regular,
MiniLM-single
-absence, MLM-regular, and MLM-absence with
times from 12.58 to 14.1 hours. However, MiniLM’s
c-scores on random captions were worse than MLM, so the
small time difference is not worth the performance drop.
In terms of Best Time, the same models are fastest,
but
in
different
order:
MiniLM-single-regular,
MLM-regular, MLM-absence, and MiniLM-single
-absence. Times range from 11.44 to 12.51 hours. For
these models, the best epoch came slightly before the fi-
nal epoch. GTE-multiple-negative is the only model
where this difference was huge: 126.3 vs. 73.97 hours.
In general, negative captions take more time for lit-
tle gain. Although some GTE models were comparable to
MLM in terms of caption score, they take longer to train, even
in terms of Best Time. Pretrained sentence transformers that


## Page 7

0
50
100
Hours to Train
Unconditional
WGAN
FDM-GTE-absence
FDM-GTE-regular
FDM-MiniLM-absence
FDM-MiniLM-regular
GTE-multiple-negative
GTE-multiple-absence
GTE-multiple-regular
GTE-single-negative
GTE-single-absence
GTE-single-regular
MiniLM-multiple-negative
MiniLM-multiple-absence
MiniLM-multiple-regular
MiniLM-single-negative
MiniLM-single-absence
MiniLM-single-regular
MLM-negative
MLM-absence
MLM-regular
MLM Model
End Time
Best Time
(a) Average End Times and Best Times
0
5
10
15
20
25
30
Edit Distance
MarioGPT
Unconditional
WGAN
FDM-GTE-absence
FDM-GTE-regular
FDM-MiniLM-absence
FDM-MiniLM-regular
GTE-multiple-negative
GTE-multiple-absence
GTE-multiple-regular
GTE-single-negative
GTE-single-absence
GTE-single-regular
MiniLM-multiple-negative
MiniLM-multiple-absence
MiniLM-multiple-regular
MiniLM-single-negative
MiniLM-single-absence
MiniLM-single-regular
MLM-negative
MLM-absence
MLM-regular
Real data
real (full)
real (100)
random
unconditional
(b) AMEDself on Model Outputs
0
5
10
15
20
25
Edit Distance
MarioGPT
Unconditional
WGAN
FDM-GTE-absence
FDM-GTE-regular
FDM-MiniLM-absence
FDM-MiniLM-regular
GTE-multiple-negative
GTE-multiple-absence
GTE-multiple-regular
GTE-single-negative
GTE-single-absence
GTE-single-regular
MiniLM-multiple-negative
MiniLM-multiple-absence
MiniLM-multiple-regular
MiniLM-single-negative
MiniLM-single-absence
MiniLM-single-regular
MLM-negative
MLM-absence
MLM-regular
real (full)
real (100)
random
unconditional
(c) AMEDreal on Model Outputs
Figure 4: Bars have 95% confidence intervals when multiple models were trained. (a) Time to train the text encoder for MLM
diffusion models is shown in red on the left, but is barely visible. Best Time is not shown for WGAN or FDM. (b) AMEDself
compares the diversity of model-generated scenes. real (full) is generated from all real data prompts. real (100) is from a
selection of 100 real prompts. random prompts are distinct from real prompts. unconditional scenes had no prompts. Diversity
for Real data is also shown, and data from MarioGPT. WGAN and Unconditional cannot produce scenes from prompts. FDM
has no unconditional scenes. (c) AMEDreal compares model-generated scenes in terms of their distinctness from the real data.
use multiple phrase embeddings take longer to train than
their single embedding counterparts.
The models that train the quickest are unconditional dif-
fusion, WGAN, and FDM. However, WGAN and uncon-
ditional diffusion offer no text guidance, and FDM perfor-
mance is much worse, so the extra speed is of little benefit.
Average Minimum Edit Distance
To compare the diver-
sity of generated levels, four sets of scenes are created by
most models: scenes from the full set of real game scene
captions, 100 samples from this set, scenes from random
captions not in the original data, and unconditionally gener-
ated scenes. Except for real (full) data, these sets each con-
tain 100 scenes to allow fair comparison. WGAN and un-
conditional diffusion cannot generate scenes from captions,
so they only have unconditional samples. FDM can techni-
cally create unconditional samples from an empty embed-
ding vector, but it was not intended to, and the results are so
terrible that we do not include them. MarioGPT is a special
case, since its scenes were not generated unconditionally, but
also were not generated by our captions. We compare against
100 size 16×16 scenes from MarioGPT as described earlier.
Figure 4b shows AMEDself scores. In general, real (full)
is small because comparing against more scenes makes
it more likely to find a similar scene. This is why real
(100) was needed for fairness, and is always higher. Across
text-conditioned diffusion models, real (full) is around
6 tiles, and real (100) is around 22 tiles, except for
GTE-multiple-negative and MiniLM-multiple
-negative around 19 tiles. These two models also had
poor caption adherence scores. For reference, Real data
shows that AMEDself is 10.4077 tiles on the full set of game
data and 20.87 tiles in the 100 sample case. The collection
of all real game data shows more diversity than what models
produce using all real game captions, but the diversity across
the evenly spaced set of 100 samples is about the same.
For random captions, diversity varies more but is gen-
erally higher than for real captions, though there are ex-
ceptions: MLM-absence and MLM-negative. Some
models with lower caption adherence have higher diver-
sity from random captions; poor level structure can re-
sult in high edit distances, since tiles will be in weird
places. Unconditional samples are generally less diverse
than caption-generated samples, the only exception be-
ing GTE-multiple-negative. WGAN and uncondi-
tional diffusion have comparable scores to the unconditional
samples from text-conditioned diffusion models. FDM’s
AMEDself scores are extremely low in all categories. Mar-
ioGPT’s score is around 25, which is higher than real (100)
for all models but lower than the random score of most.
Figure 4c compares AMEDreal results. Samples from ran-
dom captions have high distances, but distances from real
captions are much smaller, with unconditional samples usu-
ally between. real (full) and real (100) are generally closer
to each other, around 3-5 tiles, though some FDM results
are higher. In other words, for captions seen during training,
models often create nearly identical scenes, which is proba-
bly for the best, but it means that alternate scenes that share
the caption are not generated. This is a limitation in how
well models generalize. Thankfully, high random scores in-
dicate that generation of novel scenes is possible, though be-
ing too novel caries the risk of being disorganized, as occurs
with WGAN results. WGAN samples have higher AMEDreal
scores because they struggle to fit the data. In contrast,
samples from unconditional diffusion have AMEDreal scores
similar to unconditional samples from text-conditioned dif-
fusion models. FDM is once again an anomaly, since its ram-


## Page 8

0.0
0.2
0.4
0.6
0.8
1.0
Percent Beatable Levels
MarioGPT
Unconditional
WGAN
FDM-GTE-absence
FDM-GTE-regular
FDM-MiniLM-absence
FDM-MiniLM-regular
GTE-multiple-negative
GTE-multiple-absence
GTE-multiple-regular
GTE-single-negative
GTE-single-absence
GTE-single-regular
MiniLM-multiple-negative
MiniLM-multiple-absence
MiniLM-multiple-regular
MiniLM-single-negative
MiniLM-single-absence
MiniLM-single-regular
MLM-negative
MLM-absence
MLM-regular
unconditional
random
real (100)
(a) A* Solvability on Model Outputs
0
10
20
30
40
50
Percent Broken/Total Pipe Scenes
MarioGPT
Unconditional
WGAN
FDM-GTE-absence
FDM-GTE-regular
FDM-MiniLM-absence
FDM-MiniLM-regular
GTE-multiple-negative
GTE-multiple-absence
GTE-multiple-regular
GTE-single-negative
GTE-single-absence
GTE-single-regular
MiniLM-multiple-negative
MiniLM-multiple-absence
MiniLM-multiple-regular
MiniLM-single-negative
MiniLM-single-absence
MiniLM-single-regular
MLM-negative
MLM-absence
MLM-regular
real (full)
real (100)
random
unconditional
(b) Percent Scenes With Broken Pipes
0
5
10
15
Percent Broken/Total Cannon Scenes
MarioGPT
Unconditional
WGAN
FDM-GTE-absence
FDM-GTE-regular
FDM-MiniLM-absence
FDM-MiniLM-regular
GTE-multiple-negative
GTE-multiple-absence
GTE-multiple-regular
GTE-single-negative
GTE-single-absence
GTE-single-regular
MiniLM-multiple-negative
MiniLM-multiple-absence
MiniLM-multiple-regular
MiniLM-single-negative
MiniLM-single-absence
MiniLM-single-regular
MLM-negative
MLM-absence
MLM-regular
real (full)
real (100)
random
unconditional
(c) Percent Scenes With Broken Cannons
Figure 5: (a) A* results show the percentage of beatable scenes. Only one model and 100 scenes of each type are used, so there
are no error bars. (b) For each dataset, colored bars with 95% confidence intervals show the percentage of scenes that contain
a broken pipe. The gray bar extending from each bar represents the scenes with pipes of any kind: regular, broken, or upside
down. Producing few broken pipes is more impressive if valid pipes are also generated, as indicated by larger gray regions.
Most models produce few broken pipes, but more with random captions. FDM-regular models produce more broken pipes
than FDM-absence. WGAN produces many broken pipes. (c) Broken cannon data is presented similarly. Many datasets have
no broken cannons, though cannons in general are rarer than pipes.
dom scores are much lower. MarioGPT’s scores are higher
than most, though the highest random scores of certain dif-
fusion models are more novel.
Solvability
Figure 5a shows the percentage of beatable
scenes from each model. Since simulation takes time, we
only apply A* to 100 samples from real captions per one
model of each type as opposed to all model outputs across all
real captions. Even the worst, GTE-multiple-absence
with random captions, produces 72% beatable scenes. FDM
results from real captions are between 74-77%. The high-
est score is a tie at 97% between MarioGPT and MiniLM
-single-regular’s random caption samples. Most dif-
fusion models have scores between 82% and 94%.
Level Integrity
Figure 5b shows the percentage of gen-
erated scenes that contain one or more broken pipes and the
percentage of scenes with any kind of pipe. For datasets with
100 samples, the percentage is also the count. Most mod-
els produce few scenes with broken pipes using real cap-
tions, but many using random captions. Captions produce
many valid pipes too. FDM creates more broken pipes with
regular captions than absence captions. MarioGPT has
5 broken pipe scenes, which is more than diffusion mod-
els on real captions, though less than diffusion models on
random captions. WGAN produces many broken pipes, but
unconditional scenes from diffusion models have almost no
broken pipes, though they have fewer valid pipes as well.
Figure 5c shows similar results for broken cannons. Can-
nons are rarer, and broken ones rarer still, though more
broken cannons are associated with random captions and
WGAN. Unconditional samples have almost no broken can-
nons, but very few valid ones either.
Figure 6: Interactive Level Building Interface. Phrases are
selected from the right which create a caption in the upper-
left. Then samples can be generated which appear in the cen-
ter column. These can be added to a level in the lower-left
which can be played by a human or A* agent.
Larger Levels
Although the diffusion models are trained on 16 × 16 sam-
ples, the output size can be any value during inference, mak-
ing it possible to generate levels of arbitrary length. How-
ever, there are two problems. First, input prompts are cali-
brated for smaller scenes, so it is not clear what one should
expect from larger scenes, or how to assess them. Secondly,
longer levels seem to often be unbeatable due to levels hav-
ing massive gaps that cannot be jumped over.
It may be possible to address these issues with a dataset
consisting of longer levels, but confirming this is a task for
future work. In the meantime, human designers can still ben-
efit from tools we have designed by incorporating diffusion


## Page 9

models into a mixed-initiative system with a GUI for build-
ing complete levels from diffusion-generated scenes. The
interface (Figure 6) supplies checkboxes for valid phrases
organized by topic (floor, coins, etc.) so that creating de-
scriptive captions is easy to do without worrying about
spelling or the use of unknown vocabulary. Once a caption
is constructed, level scenes can be generated with a chosen
model. Parameters like the random seed, number of sam-
ples, number of inference steps, guidance scale, and scene
width can be set. Generated scenes have automatically gen-
erated captions that are color-coded to visually indicate dif-
ferences/similarities to the user-supplied prompt. Caption
adherence score is also displayed. Individual scenes can be
combined into a larger level. Scenes are added to the end
of the level by default, but they can be moved or deleted
by the user. Both constructed levels and individual scenes
can be tested via human play or with A*. Finally, ASCII
text versions of constructed levels can be saved for future
use. Examples of longer composed levels are in the online
appendix, as is a video demonstrating how to use the GUI:
https://people.southwestern.edu/∼schrum2/mario.html
Co-creative level design systems have been explored in
the academic literature before (Larsson, Font, and Alvarez
2022), including for Mario (Guzdial, Liao, and Riedl 2018;
Schrum et al. 2020). Evolutionary computation and various
types of AI models are common in such work, but the ability
to mix and match components produced from text prompts
is new, and opens up possibilities for numerous human sub-
ject studies. Experimental verification of the benefits of such
a system is still needed, but the authors found it easy to cre-
ate scenes of different sizes and combine them into fun and
interesting levels of arbitrary length. The generation of mul-
tiple scenes per caption along with the ability to change the
random seed and guidance scale make it easier to find scenes
that match a desired caption, and users may also be serendip-
itously inspired by scenes they create, even when they do not
match the input caption. We hope to study the experiences
of users interacting with this system in future work.
Limitations
Our approach to diffusion-based PCGML requires a suf-
ficiently sized dataset of level scenes and enough expert
knowledge and programming skill to assign adequate cap-
tions to such scenes algorithmically. However, we believe
this is a modest barrier and are actively expanding our re-
search to other games. Although we used NVIDIA GPUs,
they were not excessively expensive; a decent gaming PC
is able to train our models. Long levels are less likely to
be beatable, but our GUI provides an effective way to make
beatable long levels with slight additional effort.
Discussion and Conclusion
It was surprising that a small and basic transformer archi-
tecture with little training on a small dataset with limited
vocabulary produced the best results when combined with
our diffusion model. It was also disappointing that attempts
to enhance the approach had little effect or a detrimental ef-
fect. Models take longer to train with negative prompts,
and are not better. The absence captions are more com-
plicated, but offer no benefit. MiniLM and GTE are more
powerful and general language models, but do not produce
definitively better results, which is especially damning in
the case of GTE, whose models take much longer to train.
We thought multiple sentence embeddings could provide
richer context for diffusion, but they simply increased train-
ing time. Of course, it is not bad that a simpler model can be
so effective, though we wonder if other pretrained language
models or alternative architectures might be better.
There must be some way to break the average caption
score barrier of 0.5 on random captions. In fairness, some
of the random captions are very unusual. Actual captions
in the dataset include “two ascending staircases.” and “two
question blocks. two enemies. two cannons.” These captions
do not mention a floor. Although levels without floors exist,
such levels tend to have many platforms to support entities
like cannons and enemies.
We tested larger UNet architectures in our preliminary
experiments, but they only seemed to increase training
time with no clear benefit. We admit that a more system-
atic exploration of different architectures and hyperparam-
eters could lead to improvements. However, we suspect the
biggest limitation is the training data, but part of that prob-
lem could be solved with our automatic captioning system.
Although our model may not always produce scenes with
desired captions, it can produce scenes with captions that do
not exist in the dataset. If such scenes were to be automati-
cally captioned and added to the training dataset, it may be
possible to gradually accumulate enough scenes to get near
complete coverage of the space of captions. Our results sug-
gest that once a caption is in the dataset, our model would
have no trouble generating a scene that matches it.
MarioGPT does well in several metrics, though our best
diffusion models are comparable or superior in certain in-
stances. However, it is unclear what the best comparison
is: real, random, or unconditional. As stated above, our dif-
fusion models do well with captions they’ve seen during
training; MarioGPT’s limited caption options makes it less
likely to see an unfamiliar caption. It would be interesting to
compare diffusion with simpler captions, or MarioGPT with
more complex captions.
For now, we conclude, having presented a method to make
captions for Mario level scenes which allows for the training
of a transformer text encoder and diffusion model that can
make realistic Mario scenes, which can be combined into
larger levels using our GUI.
Acknowledgments
This paper was initially drafted without AI, but ChatGPT
was later used to improve clarity/concision. We thank donors
to Southwestern University’s SURF program for support.
References
Awiszus, M.; Schubert, F.; and Rosenhahn, B. 2020. TOAD-
GAN: Coherent Style Level Generation from a Single Ex-
ample. In Artificial Intelligence and Interactive Digital En-
tertainment. AAAI.


## Page 10

Awiszus, M.; Schubert, F.; and Rosenhahn, B. 2021. World-
GAN: a Generative Model for Minecraft Worlds. In Confer-
ence on Games, 1–8. IEEE.
Bontrager, P.; Lin, W.; Togelius, J.; and Risi, S. 2018. Deep
Interactive Evolution. In European Conference on the Ap-
plications of Evolutionary Computation (EvoApplications).
Dai, S.; Zhu, X.; Li, N.; Dai, T.; and Wang, Z. 2024. Proce-
dural Level Generation with Diffusion Models from a Single
Example. Proceedings of the AAAI Conference on Artificial
Intelligence, 38(9): 10021–10029.
Fontaine, M.; Hsu, Y.-C.; Zhang, Y.; and Nikolaidis, S. 2021.
On the Importance of Environments for Human-Robot Coor-
dination. In Proceedings of Robotics: Science and Systems.
Goodfellow, I.; Pouget-Abadie, J.; Mirza, M.; Xu, B.;
Warde-Farley, D.; Ozair, S.; Courville, A.; and Bengio, Y.
2014. Generative Adversarial Nets. In Neural Information
Processing Systems, 2672–2680.
Gutierrez, J.; and Schrum, J. 2020. Generative Adversarial
Network Rooms in Generative Graph Grammar Dungeons
for The Legend of Zelda. In Congress on Evolutionary Com-
putation. IEEE.
Guzdial, M.; Liao, N.; and Riedl, M. 2018.
Co-Creative
Level Design via Machine Learning. In Proceedings of the
Experimental AI in Games (EXAG) Workshop at AIIDE.
Kingma, D. P.; and Welling, M. 2014. Auto-Encoding Varia-
tional Bayes. In International Conference on Learning Rep-
resentations.
Kumaran, V.; Mott, B. W.; and Lester, J. C. 2020. Generat-
ing Game Levels for Multiple Distinct Games with a Com-
mon Latent Space. In Artificial Intelligence and Interactive
Digital Entertainment. AAAI.
Larsson, T.; Font, J.; and Alvarez, A. 2022. Towards AI as
a Creative Colleague in Game Level Design. In Artificial
Intelligence and Interactive Digital Entertainment. AAAI.
Lee, H. J.; and Simo-Serra, E. 2023. Using Unconditional
Diffusion Models in Level Generation for Super Mario Bros.
In International Conference on Machine Vision and Applica-
tions, 1–5.
Merino, T.; Negri, R.; Rajesh, D.; Charity, M.; and Togelius,
J. 2023. The Five-Dollar Model: Generating Game Maps
and Sprites From Sentence Embeddings. In Artificial Intel-
ligence and Interactive Digital Entertainment. AAAI.
Nie, Y.; Middleton, M.; Merino, T.; Kanagaraja, N.; Kumar,
A.; Zhuang, Z.; and Togelius, J. 2025.
Moonshine: Dis-
tilling Game Content Generators into Steerable Generative
Models. Proceedings of the AAAI Conference on Artificial
Intelligence, 39(13): 14344–14351.
Radford, A.; Wu, J.; Child, R.; Luan, D.; Amodei, D.; and
Sutskever, I. 2019. Language models are unsupervised mul-
titask learners. OpenAI Blog.
Rombach, R.; Blattmann, A.; Lorenz, D.; Esser, P.; and Om-
mer, B. 2022. High-Resolution Image Synthesis with Latent
Diffusion Models . In Computer Vision and Pattern Recog-
nition, 10674–10685. IEEE.
Sarkar, A.; and Cooper, S. 2021. Generating and Blending
Game Levels via Quality-Diversity in the Latent Space of a
Variational Autoencoder. In Proceedings of the Foundations
of Digital Games.
Sarkar, A.; Yang, Z.; and Cooper, S. 2020. Conditional Level
Generation and Game Blending. In Proceedings of the Ex-
perimental AI in Games (EXAG) Workshop at AIIDE.
Schrum, J.; Capps, B.; Steckel, K.; Volz, V.; and Risi, S.
2023. Hybrid Encoding for Generating Large Scale Game
Level Patterns With Local Variations. IEEE Transactions on
Games, 15(1): 46–55.
Schrum, J.; Gutierrez, J.; Volz, V.; Liu, J.; Lucas, S.; and
Risi, S. 2020. Interactive Evolution and Exploration Within
Latent Level-Design Space of Generative Adversarial Net-
works. In Genetic and Evolutionary Computation Confer-
ence. ACM.
Schrum, J.; Volz, V.; and Risi, S. 2020.
CPPN2GAN:
Combining Compositional Pattern Producing Networks and
GANs for Large-scale Pattern Generation. In Genetic and
Evolutionary Computation Conference. ACM.
Shaker, N.; Togelius, J.; and Nelson, M. J. 2016. Procedural
Content Generation in Games. Springer.
Sudhakaran, S.; Gonz´alez-Duque, M.; Freiberger, M.;
Glanois, C.; Najarro, E.; and Risi, S. 2023.
MarioGPT:
Open-Ended Text2Level Generation Through Large Lan-
guage Models. In Neural Information Processing Systems.
Summerville, A.; and Mateas, M. 2016. Super Mario as a
String: Platformer Level Generation via LSTMs. In 1st In-
ternational Joint Conference of DiGRA and FDG.
Summerville, A.; Snodgrass, S.; Guzdial, M.; Holmg˚ard, C.;
Hoover, A. K.; Isaksen, A.; Nealen, A.; and Togelius, J.
2018. Procedural Content Generation via Machine Learning
(PCGML). IEEE Transactions on Games, 10(3): 257–270.
Summerville, A. J.; Snodgrass, S.; Mateas, M.; and
Onta˜n´on, S. 2016. The VGLC: The Video Game Level Cor-
pus. In Procedural Content Generation in Games. ACM.
Thakkar, S.; Cao, C.; Wang, L.; Choi, T. J.; and Togelius, J.
2019. Autoencoder and Evolutionary Algorithm for Level
Generation in Lode Runner. In Conference on Games, 1–4.
IEEE.
Todd, G.; Earle, S.; Nasir, M. U.; Green, M. C.; and To-
gelius, J. 2023. Level Generation Through Large Language
Models. In Foundations of Digital Games. ACM.
Togelius, J.; Karakovskiy, S.; and Baumgarten, R. 2010. The
2009 Mario AI Competition.
Congress on Evolutionary
Computation, 1–8.
Valevski, D.; Leviathan, Y.; Arar, M.; and Fruchter, S.
2024.
Diffusion Models Are Real-Time Game Engines.
arXiv:2408.14837.
Virtuals Protocol. 2024. Video Game Generation: A Practi-
cal Study Using Mario. Preprint.
Volz, V.; Schrum, J.; Liu, J.; Lucas, S. M.; Smith, A. M.; and
Risi, S. 2018. Evolving Mario Levels in the Latent Space of
a Deep Convolutional Generative Adversarial Network. In
Genetic and Evolutionary Computation Conference. ACM.
ˇSosvald, D.; T¨opfer, M.; Holan, J.; ˇCern´y, V.; and Gemrot, J.
2021. Super Mario A-Star Agent Revisited. In International


## Page 11

Conference on Tools with Artificial Intelligence, 1008–1012.
IEEE.
Yang, L.; Zhang, Z.; Song, Y.; Hong, S.; Xu, R.; Zhao, Y.;
Zhang, W.; Cui, B.; and Yang, M.-H. 2023. Diffusion Mod-
els: A Comprehensive Survey of Methods and Applications.
ACM Computing Surveys, 56(4).
Zhang, X.; Zhang, Y.; Long, D.; Xie, W.; Dai, Z.; Tang, J.;
Lin, H.; Yang, B.; Xie, P.; Huang, F.; Zhang, M.; Li, W.; and
Zhang, M. 2024. mGTE: Generalized Long-Context Text
Representation and Reranking Models for Multilingual Text
Retrieval. In Empirical Methods in Natural Language Pro-
cessing: Industry Track, 1393–1412. Association for Com-
putational Linguistics.


## Page 12

Table 1: Tile types in Mario levels. Symbol characters come
from the VGLC. Identity values are used for one-hot encod-
ing. Visualizations are used by the Mario AI framework.
Tile type
Symbol
Identity
Visualization
Empty/Sky (passable)
-
0
Top-left pipe
<
1
Top-right pipe
>
2
Full question block
?
3
Cannon top
B
4
Enemy
E
5
Empty question block
Q
6
Breakable
S
7
Solid/Ground
X
8
Left pipe
[
9
Right pipe
]
10
Cannon support
b
11
Coin
o
12
Appendix
Additional hyperparameter settings and results that are only
in the arXiv pre-print.
Dataset Details
Our cleaned version of the VGLC and our captioning ap-
proach resulted in data with the following properties:
• Number of Super Mario Bros. levels: 20
• Number of Super Mario Bros. 2 levels: 22
• Total 16 × 16 samples across both games: 7,687
• Vocabulary size for regular captions: 47
• Vocabulary size for absence captions: 48
• Training samples: 6918
• Validation samples: 384
• Test samples: 385
The tiles available in Mario levels are in Table 1.
Text Encoder Details
These details are relevant to our MLM model:
• Token embedding size: 128
• Number of transformer encoder layers: 4
• Number of attention heads: 8
• Dimension of hidden layer: 256
• Probability of [MASK] token during MLM training: 0.15
• Training optimizer: AdamW
• Training epochs: 300
• Loss function: Cross Entropy Loss
• Learning rate: Starts at 0.00005
• Minimum learning rate: 0.000001
• Learning rate schedule: ReduceLROnPlateau
• Training batch size 16
Diffusion Model Details
These details are relevant to our diffusion models:
• Base dimension of the UNet: 128
• Number of residual blocks for downsampling: 2
• UNet encoder (down) channels: 13, 128, 256, 512
• UNet decoder (up) channels: 512, 256, 128, 13
• Number of attention heads: 8
• Noise schedule: DDPM with a linear beta schedule
• Noise betas: 0.0001 to 0.02
• Noise schedule time steps: up to 1000
• Training optimizer: AdamW
• AdamW weight decay: 0.01
• AdamW beta values: 0.9 and 0.999
• Gradient accumulation steps: 1
• Learning rate schedule: cosine
• Learning rate warm-up period: 25 epochs
• Top learning rate: 0.0001
• Guidance scale during inference: 7.5
• Inference steps: 30
The loss function for the diffusion model is the same one
used by Lee and Simo-Serra (2023):
Ltotal = LMSE + λLrec
(5)
LMSE = 1
N
N
X
i=1
∥ˆϵi −ϵi∥2
(6)
Lrec = −1
N
N
X
i=1
H
X
h=1
W
X
w=1
log Pθ(Oi,h,w|xi,h,w)
(7)
where λ = 0.001 is the weight on the reconstruction loss, N
is the batch size, ˆϵi is the model’s predicted noise for sample
i, ϵi is the true noise, H and W are the height and width of
16, Oi,h,w is the ground truth for the tile at position (h, w)
in sample i, xi,h,w is the generated tile at position (h, w)
in sample i, so Pθ(Oi,h,w|xi,h,w) is the probability of the
original block given the generated block according to the
diffusion model with parameters θ.
Figure 7 depicts the complete diffusion pipeline for train-
ing and inference.
Five-Dollar Model Details
These details are relevant to our Five-Dollar Models:
• Number of residual blocks: 3
• Number of convolutional filters: 128
• Kernel size: 7, but 3 for final layer
• Noise vector size: 5
• Training epochs: 100
• Loss function: Negative Log Likelihood Loss
• Training optimizer: AdamW
• Learning rate: 0.001


## Page 13

0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
1111111111111111
1111111111111111
1111111111111111
1111111111111111
0000000000000000
1111111111111111
1111111111111111
1111111111111111
1111111111111111
1111111111111111
1111111111011111
1111010111111111
1101010101110111
0101010101110101
0101010101010101
0000000000000000
----------------
----------------
----------------
----------------
SSSSSSSSSSSSSSSS
----------------
----------------
----------------
----------------
----------------
----------S-----
----X-X---------
--X-X-X-X---X---
X-X-X-X-X---X-X-
X-X-X-X-X-E-X-X-
XXXXXXXXXXXXXXXX
0000000000000000
0000000000000000
0000000000000000
0000000000000000
7777777777777777
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000700000
0000808000000000
0080808080008000
8080808080008080
8080808080508080
8888888888888888
Integer Encoding
One-Hot Encoding
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
1111111111111111
1111111111111111
1111111111111111
1111111111111111
0000000000000000
1111111111111111
1111111111111111
1111111111111111
1111111111111111
1111111111111111
1111111111011111
1111010111111111
1101010101110111
0101010101110101
0101010101010101
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
Convolutional Layer
Downsizing
Downsizing
Downsizing
Bottleneck
Convolutional Layer
Upsizing
Upsizing
Upsizing
Residual Connections
 Add Noise Based on Scheduler
Input to Diffusion Model
Output Noise Pattern
full floor. full ceiling. 
one enemy. several towers. 
several loose blocks.
Generate Caption
One of Several Possible
Embedding Models:
MLM, MiniLM, or GTE
Prompt Embedding
Embed Prompt as Vector(s)
Cross Attention
-
Subtract Diffusion Generated Noise From Original Noisy Input
0000000000000000
0000000000000000
0000000000000000
0000000000000000
7777777777777777
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000000000
0000000000700000
0000808000000000
0080808080008000
8080808080008080
8080808080508080
8888888888888888
Argmax
----------------
----------------
----------------
----------------
SSSSSSSSSSSSSSSS
----------------
----------------
----------------
----------------
----------------
----------S-----
----X-X---------
--X-X-X-X---X---
X-X-X-X-X---X-X-
X-X-X-X-X-E-X-X-
XXXXXXXXXXXXXXXX
Decode to Tiles
(Input Replaced 
With Random Noise 
During Inference)
(Final Decoding 
Only Happens 
During Inference)
Timestep Embedding
DDPM Noise
Scheduler
MSE Loss
Reconstruction Loss
MSE Compares Added Noise to Predicted Noise
Reconstruction Loss Compares Original Scene to Generated Scene
(Denoised Output Unlikely To 
Actually Consist of Only 0's and 1's,
But is Depicted This Way For Convenience)
Train Model Based On
Combined Loss
+
Tokenize
Figure 7: Diffusion Training and Inference Pipeline. Our training set is integer-encoded, but was derived from the ASCII data
in the VGLC. Each scene is associated with an automatically generated caption. The scenes are one-hot encoded before noise
is added according to a DDPM scheduler. The noisy input enters the diffusion model, while its cross-attention blocks access a
hidden state based on both a timestep embedding from DDPM and a prompt embedding from whichever text model is being
used. The output of the model is a noise prediction which is directly compared to the known amount of added noise to complete
the Mean Squared Error. The predicted noise is also removed from the noisy input to approximate the one-hot encoded training
data, which is then integer-encoded via argmax for comparison to the original training sample. This is how the reconstruction
loss is calculated. Both losses are combined to train the model.
0
100
200
300
400
500
Epoch
0.0
0.2
0.4
0.6
0.8
1.0
Caption Score
MLM-regular
MiniLM-single-regular
MiniLM-multiple-regular
GTE-single-regular
GTE-multiple-regular
FDM-MiniLM-regular
FDM-GTE-regular
(a) regular
0
100
200
300
400
500
Epoch
0.0
0.2
0.4
0.6
0.8
1.0
Caption Score
MLM-absence
MiniLM-single-absence
MiniLM-multiple-absence
GTE-single-absence
GTE-multiple-absence
FDM-MiniLM-absence
FDM-GTE-absence
(b) absence
0
100
200
300
400
500
Epoch
0.0
0.2
0.4
0.6
0.8
1.0
Caption Score
MLM-negative
MiniLM-single-negative
MiniLM-multiple-negative
GTE-single-negative
GTE-multiple-negative
(c) negative
Figure 8: Average Caption Adherence Score by Epoch on All Real Game Captions. Results are qualitatively similar to those in
Figure 2. (a) regular caption results. (b) absence caption results. (c) negative caption results.
Additional Performance Metrics and Results
Results dealing with these performance metrics could not fit
into the main text of the paper.
Caption Adherence on Full Dataset
When applied to the
set of all captions from the original games (Figure 8), the
caption adherence score is qualitatively similar to the results
from just the test set data, as demonstrated earlier (Figure 2).
End Time and Best Time on Logarithmic Scale
Most
execution times are small, but a few larger values skew the
presentation in Figure 4a. The same data from that figure is
depicted in Figure 9 using a logarithmic scale.
Caption Order Tolerance
We want to give users the flex-
ibility to provide caption phrases in whatever order they
prefer. Semantically, a caption is equivalent to any caption
that is a permutation of its phrases. We can take a caption
and sample some number of its permutations, send each one
through a text-to-level model, and average the c-scores:
tolerance(P) =
P
(p,c)∈P c-score(p, c)
|P|
(8)
P is a set of pairs (p, c), where p is a prompt and c is the
caption on the level a model produces using p. Values of p
are distinct permutations of the same input prompt.
Prompts can contain many phrases, so averaging across all
permutations would be computationally expensive. Instead,
we sample up to 5 distinct random permutations per prompt.
Caption order tolerance results are in Figure 10.
Making Larger Levels
Tables 2, 3, and 4 show different examples of using the in-
teractive GUI to create longer levels.


## Page 14

Table 2: Long Level Generated One Scene At a Time (16 wide). Using MLM-regular0 (https://huggingface.co/schrum2/
MarioDiffusion-MLM-regular0), the GUI was used to generate 16 × 16 scenes with the designated prompts. The segments
were then combined into a single playable level. The caption adherence score of each scene is shown beneath it.
full floor. one
platform. two
enemies. one
pipe. a few
coins.
floor with one
gap. a few
enemies. a few
pipes. one
tower.
floor with
several gaps.
two platforms.
one rectangular
block cluster. a
few enemies.
many coins.
one tower. one
ascending
staircase.
floor with
several gaps.
one rectangular
block cluster.
one irregular
block cluster.
several
enemies. many
coins. one
tower. one
ascending
staircase. one
descending
staircase. two
question
blocks.
a few
platforms.
several
enemies. one
question block.
two loose
blocks.
giant gap with
one chunk of
floor. a few
platforms. one
rectangular
block cluster.
two enemies.
one pipe. a few
coins. a few
loose blocks.
giant gap with
one chunk of
floor. a few
platforms. a
few enemies. a
few coins. one
coin line. one
question block.
a few loose
blocks.
floor with one
gap. one
ascending
staircase.
0.888889
0.875
0.347222
0.458333
0.972222
0.722222
0.819444
1.0
100
101
102
Hours to Train
Unconditional
WGAN
FDM-GTE-absence
FDM-GTE-regular
FDM-MiniLM-absence
FDM-MiniLM-regular
GTE-multiple-negative
GTE-multiple-absence
GTE-multiple-regular
GTE-single-negative
GTE-single-absence
GTE-single-regular
MiniLM-multiple-negative
MiniLM-multiple-absence
MiniLM-multiple-regular
MiniLM-single-negative
MiniLM-single-absence
MiniLM-single-regular
MLM-negative
MLM-absence
MLM-regular
MLM Model
End Time
Best Time
Figure 9: Average End Times and Best Times on Log Scale.
0.00
0.25
0.50
0.75
1.00
Caption Order Tolerance Score
FDM-GTE-absence
FDM-GTE-regular
FDM-MiniLM-absence
FDM-MiniLM-regular
GTE-multiple-negative
GTE-multiple-absence
GTE-multiple-regular
GTE-single-negative
GTE-single-absence
GTE-single-regular
MiniLM-multiple-negative
MiniLM-multiple-absence
MiniLM-multiple-regular
MiniLM-single-negative
MiniLM-single-absence
MiniLM-single-regular
MLM-negative
MLM-absence
MLM-regular
Figure 10: Caption Order Tolerance. Shows how models
handle different phrase orderings in captions of real game
scenes. One model of each type is considered with scores
for each caption in the test set. Most models do well, ex-
cept MiniLM-single-absence, MiniLM-multiple
-negative, GTE-multiple-negative, and FDM.


## Page 15

Table 3: Long Level Generated One Scene At a Time (32 wide). Using MLM-regular0 (https://huggingface.co/schrum2/
MarioDiffusion-MLM-regular0), the GUI was used to generate 32 × 16 scenes with the designated prompts. The segments
were then combined into a single playable level. Each segment of width 32 has its own caption adherence score, but the result
of splitting each segment into two scenes of width 16 and averaging those caption adherence scores is also shown. It is generally
harder to control the output and to interpret the meaning of the caption adherence scores when the width increases.
full floor. full ceiling. one
enemy. many coins. one coin
line. several towers.
floor with two gaps. ceiling
with two gaps. one rectangular
block cluster. one irregular
block cluster. a few enemies.
two pipes. many coins.
giant gap with several chunks
of floor. ceiling with one gap.
two irregular block clusters.
one enemy. one upside down
pipe. many coins.
floor with two gaps. ceiling
with one gap. one platform.
two cannons. a few question
blocks.
0.63888889
0.56111111
0.38055556
0.75
AVG: 0.56944444
AVG: 0.46388889
AVG: 0.33888889
AVG: 0.69027778
Table 4: Long Level Generated One Scene At a Time (64 wide). Using MLM-regular0 (https://huggingface.co/schrum2/
MarioDiffusion-MLM-regular0), the GUI was used to generate 64 × 16 scenes with the designated prompts. The segments
were then combined into a single playable level. Each segment of width 64 has its own caption adherence score, but the result
of splitting each segment into four scenes of width 16 and averaging those caption adherence scores is also shown. Note that it
is not necessary for level widths to be multiples of 16, nor is it necessary for all segments in a level to have the same width.
floor with several gaps. a few platforms. one rectangular block
cluster. one irregular block cluster. a few enemies. a few coin
lines. many coins. one ascending staircase. a few loose blocks.
floor with two gaps. ceiling with one gap. several platforms. a
few rectangular block clusters. one irregular block cluster. a
few enemies. two pipes. one coin line. two coins. one cannon.
several question blocks. several loose blocks.
0.638889
0.458333
AVG: 0.479167
AVG: 0.280556


## Page 16

Table 5: Example scenes generated by models trained with regular captions. Each of these models is available on Hugging Face
(Details here: https://github.com/schrum2/MarioDiffusion/blob/main/MODELS.md). The first row shows the prompt used to
generate the scene. The first five columns are real captions from the test set, and the next five are from the random test set of
captions not present in the original data. Beneath each image is the resulting caption adherence score. These images are also
available online: https://people.southwestern.edu/∼schrum2/mario.html.
full floor.
one enemy.
a few
question
blocks. one
platform.
one pipe.
floor with
one gap. one
descending
staircase.
one pipe.
one
irregular
block
cluster.
full floor.
full ceiling.
one enemy.
one coin.
one
irregular
block
cluster. a
few towers.
a few loose
blocks.
floor with
one gap. a
few
enemies.
one cannon.
one tower.
full floor. a
few
enemies. a
few
question
blocks. one
platform.
one upside
down pipe.
two loose
blocks.
a few coin
lines. one
irregular
block
cluster. a
few
enemies.
several
coins. two
ascending
staircases.
one
question
block. one
rectangular
block
cluster. two
cannons.
floor with
several
gaps. two
pipes. two
enemies.
one
descending
staircase.
two towers.
two upside
down pipes.
full floor.
one
descending
staircase.
one loose
block. a few
upside down
pipes. full
ceiling. two
coins. one
enemy.
several
platforms.
two
rectangular
block
clusters. one
pipe. a few
upside down
pipes.
floor with
several
gaps. one
tower.
MLM-regular0
0.88888889
1.0
1.0
0.97222222
1.0
0.26388889 0.51388889 0.35277778
0.625
0.97222222
MiniLM-single-regular0
0.98611111
1.0
1.0
0.95833333
0.75
0.48611111 0.38888889 0.13055556
0.5
0.98611111
MiniLM-multiple-regular0
1.0
1.0
1.0
1.0
0.76388889 0.02777778 0.40277778 0.22777778
0.375
0.97222222
GTE-single-regular0
0.98611111
1.0
1.0
1.0
1.0
0.27777778 0.31944444 0.38055556
0.5
0.98611111
GTE-multiple-regular0
0.88888889
1.0
1.0
1.0
0.76388889 0.38888889 −0.0138889
0.375
0.33333333 0.98611111


## Page 17

Table 6: Example scenes generated by models trained with absence captions. Each of these models is available on Hugging Face
(Details here: https://github.com/schrum2/MarioDiffusion/blob/main/MODELS.md). The first row shows the regular prompt
that the actual input prompt is based on. Phrases for absent concepts are added automatically. The first five columns are real
captions from the test set, and the next five are from the random test set of captions not present in the original data. Beneath
each image is the resulting caption adherence score. These images are also available online: https://people.southwestern.edu/
∼schrum2/mario.html.
full floor.
one enemy.
a few
question
blocks. one
platform.
one pipe.
floor with
one gap. one
descending
staircase.
one pipe.
one
irregular
block
cluster.
full floor.
full ceiling.
one enemy.
one coin.
one
irregular
block
cluster. a
few towers.
a few loose
blocks.
floor with
one gap. a
few
enemies.
one cannon.
one tower.
full floor. a
few
enemies. a
few
question
blocks. one
platform.
one upside
down pipe.
two loose
blocks.
a few coin
lines. one
irregular
block
cluster. a
few
enemies.
several
coins. two
ascending
staircases.
one
question
block. one
rectangular
block
cluster. two
cannons.
floor with
several
gaps. two
pipes. two
enemies.
one
descending
staircase.
two towers.
two upside
down pipes.
full floor.
one
descending
staircase.
one loose
block. a few
upside down
pipes. full
ceiling. two
coins. one
enemy.
several
platforms.
two
rectangular
block
clusters. one
pipe. a few
upside down
pipes.
floor with
several
gaps. one
tower.
MLM-absence0
1.0
1.0
1.0
0.95833333 0.76388889 −0.2222222 0.43055556 0.15833333 0.11111111
0.75
MiniLM-single-absence0
0.73611111 0.22222222 0.30555556 0.77777778 0.80555556 −0.1388889 0.26388889 0.20833333 0.20833333
0.625
MiniLM-multiple-absence0
1.0
1.0
1.0
0.97222222 0.98611111 0.26388889 0.51388889
0.5
0.30555556 0.98611111
GTE-single-absence0
0.86111111 0.66666667
0.625
0.88888889 0.65277778 0.15277778 0.27777778 0.44444444 0.52777778 0.98611111
GTE-multiple-absence0
0.66666667
1.0
1.0
1.0
0.63888889 0.09722222 0.26388889 0.56111111 0.73611111 0.98611111


## Page 18

Table 7: Example scenes generated by models trained with negative captions. Each of these models is available on Hugging Face
(Details here: https://github.com/schrum2/MarioDiffusion/blob/main/MODELS.md). The first row shows the regular prompt.
Phrases for absent concepts automatically create the corresponding negative prompt. The first five columns are real captions
from the test set, and the next five are from the random test set of captions not present in the original data. Beneath each image
is the resulting caption adherence score. These images are also available online: https://people.southwestern.edu/∼schrum2/
mario.html.
full floor.
one enemy.
a few
question
blocks. one
platform.
one pipe.
floor with
one gap. one
descending
staircase.
one pipe.
one
irregular
block
cluster.
full floor.
full ceiling.
one enemy.
one coin.
one
irregular
block
cluster. a
few towers.
a few loose
blocks.
floor with
one gap. a
few
enemies.
one cannon.
one tower.
full floor. a
few
enemies. a
few
question
blocks. one
platform.
one upside
down pipe.
two loose
blocks.
a few coin
lines. one
irregular
block
cluster. a
few
enemies.
several
coins. two
ascending
staircases.
one
question
block. one
rectangular
block
cluster. two
cannons.
floor with
several
gaps. two
pipes. two
enemies.
one
descending
staircase.
two towers.
two upside
down pipes.
full floor.
one
descending
staircase.
one loose
block. a few
upside down
pipes. full
ceiling. two
coins. one
enemy.
several
platforms.
two
rectangular
block
clusters. one
pipe. a few
upside down
pipes.
floor with
several
gaps. one
tower.
MLM-negative0
0.86111111 0.63888889 0.68611111
1.0
0.75
−0.0138889 0.30555556 0.33888889 0.30555556 0.97222222
MiniLM-single-negative0
0.95833333
0.875
0.92222222 0.86111111 0.73611111 −0.0416667 0.56944444 0.31666667 0.47222222 0.63888889
MiniLM-multiple-negative0
0.97222222 0.63888889 0.93055556 0.83333333 0.76388889 −0.0416667 0.30555556 0.06944444 0.27777778 0.65277778
GTE-single-negative0
0.95833333 0.63888889 0.93611111 0.94444444 0.98611111 0.38888889 0.06944444 0.30555556 0.19444444 0.95833333
GTE-multiple-negative0
0.95833333 0.76388889
0.875
0.86111111 0.73611111 −0.2361111 0.40277778 0.30277778 0.38888889 0.65277778
