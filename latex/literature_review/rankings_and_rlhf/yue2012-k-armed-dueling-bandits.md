# The K-Armed Dueling Bandits Problem

**Yue, Broder, Kleinberg, & Joachims (2012)**

---


## Page 1

Journal of Computer and System Sciences 78 (2012) 1538–1556
Contents lists available at SciVerse ScienceDirect
Journal of Computer and System Sciences
www.elsevier.com/locate/jcss
The K-armed dueling bandits problem
Yisong Yue a,∗, Josef Broder b, Robert Kleinberg c, Thorsten Joachims c
a H. John Heinz III College, Carnegie Mellon University, Pittsburgh, PA 15213, United States
b Center for Applied Mathematics, Cornell University, Ithaca, NY 14853, United States
c Department of Computer Science, Cornell University, Ithaca, NY 14853, United States
a r t i c l e
i n f o
a b s t r a c t
Article history:
Received 28 March 2010
Received in revised form 31 January 2011
Accepted 22 December 2011
Available online 21 January 2012
Keywords:
Online learning
Multi-armed bandits
Preference elicitation
We study a partial-information online-learning problem where actions are restricted to
noisy comparisons between pairs of strategies (also known as bandits). In contrast to
conventional approaches that require the absolute reward of the chosen strategy to be
quantiﬁable and observable, our setting assumes only that (noisy) binary feedback about
the relative reward of two chosen strategies is available. This type of relative feedback is
particularly appropriate in applications where absolute rewards have no natural scale or are
diﬃcult to measure (e.g., user-perceived quality of a set of retrieval results, taste of food,
product attractiveness), but where pairwise comparisons are easy to make. We propose
a novel regret formulation in this setting, as well as present an algorithm that achieves
information-theoretically optimal regret bounds (up to a constant factor).
© 2012 Elsevier Inc. All rights reserved.
1. Introduction
In partial information online learning problems (also known as bandit problems) [27], an algorithm must choose, in each
of T consecutive iterations, one of K possible bandits (strategies). For conventional bandit problems, in every iteration, each
bandit receives a real-valued payoff in [0, 1], initially unknown to the algorithm. The algorithm then chooses one bandit and
receives (and thus observes) the associated payoff. No other payoffs are observed. The goal then is to maximize the total
payoff (i.e., the sum of payoffs over all iterations).
The conventional setting assumes that observations perfectly reﬂect (or are unbiased estimates of) the received payoffs.
In many applications, however, such observations may be unavailable or unreliable. Consider, for example, applications in
sensory testing or information retrieval, where the payoff is the goodness of taste or the user-perceived quality of a retrieval
result. While it is diﬃcult to elicit payoffs on an absolute scale in such applications, one can reliably obtain relative judg-
ments of payoff (i.e. “A tastes better than B”, or “ranking A is better than ranking B”). In fact, user behavior can often be
modeled as maximizing payoff, so that such relative comparison statements can be derived from observable user behavior.
For example, to elicit whether a search-engine user prefers ranking r1 over r2 for a given query, Radlinski et al. [26] showed
how to present an interleaved ranking of r1 and r2 so that clicks indicate which of the two is preferred by the user. This
ready availability of pairwise comparison feedback in applications where absolute payoffs are diﬃcult to observe motivates
our learning framework.
Given a collection of K bandits (also referred to as arms, actions or strategies), we wish to ﬁnd a sequence of noisy
comparisons that has low regret. We call this the K -armed Dueling Bandits Problem, which can also be viewed as a regret-
minimization version of the classical problem of ﬁnding the maximum element of a set using noisy comparisons [14]. This
paper extends results originally published in [28] with a more thorough and reﬁned theoretical analysis.
* Corresponding author.
E-mail addresses: yisongyue@cmu.edu (Y. Yue), jbroder@cam.cornell.edu (J. Broder), rdk@cs.cornell.edu (R. Kleinberg), tj@cs.cornell.edu (T. Joachims).
0022-0000/$ – see front matter © 2012 Elsevier Inc. All rights reserved.
doi:10.1016/j.jcss.2011.12.028

## Page 2

Y. Yue et al. / Journal of Computer and System Sciences 78 (2012) 1538–1556
1539
A canonical application example of the dueling bandits problem is an intranet-search system that is installed for a
new customer. Among K built-in retrieval functions, the search engine needs to select the one that provides the best
results on this collection, with pairwise feedback coming from clicks in the interleaved rankings [26]. Since the search
engine incurs regret whenever it presents the results from a suboptimal retrieval function, it aims to eﬃciently identify and
eliminate suboptimal retrieval functions in order to maximize user satisfaction. More generally, the dueling bandits problem
arises naturally in many applications where a system must adapt interactively to speciﬁc user bases, and where pairwise
comparisons are easier to elicit than absolute payoffs.
One important issue is formulating an appropriate notion of regret. Since we are concerned with maximizing user util-
ity (or satisfaction), but utility is not directly quantiﬁable in our pairwise-comparison model, a natural question to ask is
whether users, at each iteration, would have preferred another bandit over the ones chosen by our algorithm. This leads
directly to our regret formulation (described in Section 3), which measures regret based on the (initially unknown) proba-
bility that the best bandit b∗would win a comparison with the chosen bandits at each iteration. One can alternatively view
this as the fraction of users who would have preferred b∗over the bandits chosen by our algorithm.
Our solution follows an “explore then exploit” approach, where we will bound expected regret by the regret incurred
while running the exploration algorithm. We will present an exploration algorithm in Section 4, which we call Interleaved
Filter. Interleaved Filter incurs regret that matches (up to constant factors) the information-theoretic optimum in expectation,
and is within a logarithmic factor with high probability. We will prove the matching lower bound in Section 10.
An interesting feature of our Interleaved Filter algorithms is that, unlike previous search algorithms based on noisy
comparisons, e.g., [14], the number of experiments devoted to each bandit during the exploration phase is highly non-
uniform: of the K bandits, there is a small subset of bandits (O(log K) of them) who each participate in O(K) comparisons,
while the remaining bandits only participate in O(log K) comparisons in expectation. In Section 10 we provide insight about
why existing methods suffer high regret in our setting.
2. Related work
Regret-minimizing algorithms for multi-armed bandit problems and their generalizations have been intensively studied
for many years, both in the stochastic [20] and non-stochastic [3] cases. The vast literature on this topic includes algorithms
whose regret is within a constant factor of the information-theoretic lower bound in both the stochastic case [2] and the
non-stochastic case [1]. Our use of upper conﬁdence bounds in designing algorithms for the dueling bandits problem is
preﬁgured by their use in the multi-armed bandit algorithms that appear in [6,2,20].
Upper conﬁdence bounds are also central to the design of multi-armed bandit problems in the PAC setting [12,24],
where the algorithm’s objective is to identify an arm that is ε-optimal with probability at least 1 −δ. Our work adopts
a very different feedback model (pairwise comparisons rather than direct observation of payoffs) and a different objective
(regret minimization rather than the PAC objective), but there are clear similarities between our proposed algorithms and
the Successive Elimination and Median Elimination algorithms developed for the PAC setting in [12]. There are also some
clear differences between the algorithms: these are discussed in Section 11.
The diﬃculty of the dueling bandits problem stems from the fact that the algorithm has no way of directly observing
the costs of the actions it chooses. It is an example of a partial monitoring problem, a class of regret-minimization problems
deﬁned in [9], in which an algorithm (the “forecaster”) chooses actions and then observes feedback signals that depend on
the actions chosen by the forecaster and by an unseen opponent (the “environment”). This pair of actions also determines
a loss, which is not revealed to the forecaster but is used in deﬁning the forecaster’s regret. Under the crucial assumption
that the feedback matrix has high enough rank that its row space spans the row space of the loss matrix (which is required
in order to allow for a Hannan consistent forecaster) the results of [9] show that there is a forecaster whose regret is
bounded by O(T 2/3) against a non-stochastic (adversarial) environment, and that there exist partial monitoring problems
for which this bound cannot be improved. Our dueling bandits problem is a special case of the partial monitoring problem.
In particular, our environment is stochastic rather than adversarial, and thus our regret bound exhibits much better (i.e.,
logarithmic) dependence on T .
Banditized online learning problems based on absolute rewards (of individual actions) have been previously studied in
the context of web advertising [25,22]. In that setting, clear explicit feedback is available in the form of (expected) revenue.
We study settings where such absolute measures are unavailable or unreliable.
Our work is also closely related to the literature on computing with noisy comparison operations [4,8,14,18], in partic-
ular the design of tournaments to identify the maximum element in an ordered set, given access to noisy comparators. All
of these papers assume unit cost per comparison, whereas we charge a different cost for each comparison depending on
the pair of elements being compared. In the unit-cost-per-comparison model, and assuming that every comparison has ϵ
probability of error regardless of the pair of elements being compared, Feige et al. [14] presented sequential and parallel
algorithms that achieve the information-theoretically optimal expected cost (up to constant factors) for many basic prob-
lems such as sorting, searching, and selecting the maximum. The upper bound for noisy binary search has been improved
in a recent paper [8] that achieves the information-theoretic optimum up to a 1 + o(1) factor. When the probability of
error depends on the pair of elements being compared (as in our dueling bandits problem), Adler et al. [4] and Karp and
Kleinberg [18] present algorithms that achieve the information-theoretic optimum (up to constant factors) for the problem
of selecting the maximum and for binary search, respectively. Our results can be seen as extending this line of work to the

## Page 3

1540
Y. Yue et al. / Journal of Computer and System Sciences 78 (2012) 1538–1556
setting of regret minimization. It is worth noting that the most eﬃcient algorithms for selecting the maximum in the model
of noisy comparisons with unit cost per comparison [4,14] are not suitable in the regret minimization setting considered
here, because they devote undue effort to comparing elements that are far from the maximum. This point is discussed
further in Section 11.
Yue and Joachims [29] simultaneously studied a continuous version of the dueling bandits problem, where bandits (e.g.,
retrieval functions) are characterized using a compact and convex parameter space. For that setting, they proposed a gradient
descent algorithm which achieves sublinear regret (with respect to the time horizon). In many applications, it may be
infeasible or undesirable to interactively explore such a large space of bandits. For instance, in intranet search one might
reasonably “cover” the space of plausible retrieval functions with a small number of hand-crafted retrieval functions. In such
cases, selecting the best of K well-engineered solutions would be much more eﬃcient than searching a possibly huge space
of real-valued parameters.
Learning based on pairwise comparisons is well studied in the (off-line) supervised learning setting called learning to
rank. Typically, a preference function is ﬁrst learned using a set of i.i.d. training examples, and subsequent predictions are
made to minimize the number of mis-ranked pairs (e.g., [10]). Most prior work assume access to a training set with absolute
labels (e.g., of relevance or utility) on individual examples, with pairwise preferences generated using pairs of inputs with
labels from different ordinal classes (e.g., [5,7,13,15,17,21]). In the case where there are exactly two label classes, this
becomes the so-called bipartite ranking problem [5,7], which is a more general version of learning to optimize ROC-Area
[15,17,21].
3. The dueling bandits problem
We propose a new online optimization problem, called the K -armed Dueling Bandits Problem, where the goal is to ﬁnd
the best among K bandits B = {b1,...,bK }. Each iteration comprises a noisy comparison (a duel) between two bandits
(possibly the same bandit with itself). We assume that the outcomes of these noisy comparisons are independent random
variables and that the probability of b winning a comparison with b′ is stationary over time. We write this probability as
P(b > b′) = ϵ(b,b′) + 1/2, where ϵ(b,b′) ∈(−1/2, 1/2) is a measure of the distinguishability between b and b′. Note that
ϵ(b,b′) = −ϵ(b′,b) and ϵ(b,b) = 0. We assume that there exists a total ordering on B such that b ≻b′ implies ϵ(b,b′) > 0.
We will also use the notation ϵi, j ≡ϵ(bi,b j).
Let (b(t)
1 ,b(t)
2 ) be the bandits chosen at iteration t, and let b∗be the overall best bandit. We deﬁne strong regret based
on comparing the chosen bandits with b∗,
RT =
T

t=1
max
ϵ

b∗,b(t)
1

,ϵ

b∗,b(t)
2

,
(1)
where T is the time horizon. We also deﬁne weak regret,
˜RT =
T

t=1
min
ϵ

b∗,b(t)
1

,ϵ

b∗,b(t)
2

,
(2)
which only compares ˆb against the better of b(t)
1
and b(t)
2 . One can regard regret as the fraction of users who would have
preferred the best bandit over the chosen ones in each iteration.1 More precisely, it corresponds to the fraction of users
who prefer the best bandit to the worse of the pair of bandits chosen, in the case of strong regret, or to the better of the
two bandits chosen, in the case of weak regret. Note that our results are immediately applicable to any notion of regret that
is a linear combination of weak and strong regret, e.g.
1
2
ϵ

b∗,b(t)
1

+ ϵ

b∗,b(t)
2

.
We will present algorithms which achieve identical regret bounds for both notions of regret (up to constant factors) by
assuming a property called stochastic triangle inequality, which is described in the next section.
3.1. Modeling assumptions
We impose additional structure to the probabilistic comparisons. First, we assume strong stochastic transitivity, which
requires that any triplet of bandits bi ≻b j ≻bk satisﬁes
ϵi,k ⩾max{ϵi, j,ϵ j,k}.
(3)
This assumption places a monotonicity or internal consistency constraint on possible probability values.
1 In the search setting, users experience an interleaving, or mixing, of results from both retrieval functions to be compared.

## Page 4

Y. Yue et al. / Journal of Computer and System Sciences 78 (2012) 1538–1556
1541
Algorithm 1 Explore then exploit solution.
1: Input: T , B = {b1,...,bK }, EXPLORE
2: (ˆb, ˆT) ←EXPLORE(T,B)
3: for t = ˆT + 1,..., T do
4:
compare ˆb and ˆb
5: end for
We also assume stochastic triangle inequality, which requires any triplet of bandits bi ≻b j ≻bk to satisfy
ϵi,k ⩽ϵi, j + ϵ j,k.
(4)
Stochastic triangle inequality captures the condition that the probability of a bandit winning (or losing) a comparison will
exhibit diminishing returns as it becomes increasingly superior (or inferior) to the competing bandit.2
We brieﬂy describe two common generative models which satisfy these two assumptions. The ﬁrst is the logistic or
Bradley–Terry model, where each bandit bi is assigned a positive real value μi. Probabilistic comparisons are made using
P(bi > b j) =
μi
μi + μ j
.
The second is a Gaussian model, where each bandit is associated with a random variable Xi that has a Gaussian distribution
with mean μi and variance 1. Probabilistic comparisons are made using
P(bi > b j) = P(Xi −X j > 0),
where Xi −X j ∼N(μi −μ j, 2). It is straightforward to check that both models satisfy strong stochastic transitivity and
stochastic triangle inequality. We will describe and justify a more general family of probabilistic models in Appendix A.
4. Algorithm and main results
Our solution, which is described in Algorithm 1, follows an “explore then exploit” approach. For a given time horizon T
and a set of K bandits B = {b1,...,bK }, an exploration algorithm (denoted generically as EXPLORE) is used to ﬁnd the best
bandit b∗. EXPLORE returns both its solution ˆb as well as the total number of iterations ˆT for which it ran (it is possible
that ˆT > T ). Should ˆT < T , we enter an exploit phase by repeatedly choosing (b(t)
1 ,b(t)
2 ) = (ˆb, ˆb), which incurs no additional
regret assuming EXPLORE correctly found the best bandit (ˆb = b∗). In the case where ˆT > T , then the regret incurred from
running EXPLORE still bounds our regret formulations (which only measure regret up to T ), so our analysis in this section
will still hold.3
Our exploration algorithm, which we call Interleaved Filter (IF), is described in Algorithm 2. We will show that IF
correctly return the best bandit with probability at least 1 −1/T . Correspondingly, a suboptimal bandit is returned with
probability at most 1/T , in which case we assume maximal regret O(T). We can thus bound the expected regret by
E[RT ] ⩽

1 −1
T

E
	
RIF
T

+ 1
T O(T)
= O

E
	
RIF
T

+ 1

(5)
where RIF
T denotes the regret incurred from running Interleaved Filter. Thus the regret bound depends entirely on the regret
incurred by IF. We will show that IF achieves an expected regret bound which matches the information-theoretic lower
bound (up to constant factors) presented in Section 10, and also matches with high probability4 the lower bound up to a
log factor.
Interleaved Filter maintains a candidate bandit ˆb and simulates simultaneously comparing ˆb with all other remaining
bandits via round robin scheduling (i.e., interleaving). Any bandit that is empirically inferior to ˆb with 1 −δ conﬁdence is
removed (we will describe later how to choose δ). When some bandit b′ is empirically superior to ˆb with 1 −δ conﬁdence,
then ˆb is removed and b′ becomes the new candidate ˆb ←b′. Afterwards, all empirically inferior bandits (even if lacking
1 −δ conﬁdence) are removed (called pruning – see lines 16–18 in Algorithm 2). This process repeats until only one bandit
remains. Assuming IF has not made any mistakes, then it will return the best bandit ˆb = b∗.
Terminology. We use the term “bandit” (or “action” or “arm”) to refer to an element of the strategy set B. Interleaved
Filter makes a “mistake” if it draws a false conclusion regarding a pair of bandits. A mistake occurs when an inferior bandit
2 Our analysis also applies for a relaxed version where ϵi,k ⩽λ(ϵi, j + ϵ j,k) for ﬁnite λ > 1.
3 In practice, we can terminate EXPLORE after it has run for T time steps, in which case the incurred regret is strictly less than running EXPLORE to
completion.
4 We will say that a sequence of random variables XT,K is O( f (T, K)) with high probability if for any suﬃciently large d, there exists m depending only
on d such that P(XT,K ⩾mf (T, K)) ⩽(T K)−d for all suﬃciently large T, K.

## Page 5

1542
Y. Yue et al. / Journal of Computer and System Sciences 78 (2012) 1538–1556
Algorithm 2 Interleaved Filter (IF).
1: Input: T , B = {b1,...,bK }
2: δ ←1/(T K 2)
3: Choose ˆb ∈B randomly
4: W ←{b1,...,bK } \ {ˆb}
5: ∀b ∈W , maintain estimate ˆP ˆb,b of P(ˆb > b) according to (6)
6: ∀b ∈W , maintain 1 −δ conﬁdence interval ˆC ˆb,b of ˆP ˆb,b according to (7), (8)
7: while W ̸= ∅do
8:
for b ∈W do
9:
compare ˆb and b
10:
update ˆP ˆb,b, ˆC ˆb,b
11:
end for
12:
while ∃b ∈W s.t. ( ˆP ˆb,b > 1/2 ∧1/2 /∈ˆC ˆb,b) do
13:
W ←W \ {b}
//ˆb declared winner against b
14:
end while
15:
if ∃b′ ∈W s.t. ( ˆP ˆb,b′ < 1/2 ∧1/2 /∈ˆC ˆb,b′) then
16:
while ∃b ∈W s.t. ˆP ˆb,b > 1/2 do
17:
W ←W \ {b}
//pruning
18:
end while
19:
ˆb ←b′,
W ←W \ {b′}
//b′ declared winner against ˆb (new round)
20:
∀b ∈W , reset ˆP ˆb,b and ˆC ˆb,b
21:
end if
22: end while
23: ˆT ←Total Comparisons Made
24: return (ˆb, ˆT)
is determined with 1 −δ conﬁdence to be the superior one. We call the elimination step in lines 16–18 of Algorithm 2
“pruning”. We deﬁne a “match” to be all the comparisons Interleaved Filter makes between two bandits, and a “round” to
be all the matches played by one candidate ˆb. We always refer to log x as the natural log, ln x, whenever the distinction is
necessary.
In our analysis, we assume without loss of generality that the bandits in B are indexed in preferential order b1 ≻··· ≻bK .
We ﬁrst state our main result.
Theorem 1. Running Algorithm 1 with B = {b1,...,bK }, time horizon T (T ⩾K), and IF incurs expected regret (both weak and
strong) bounded by
E[RT ] = O

E
	
RIF
T


= O
 K
ϵ1,2
log T

.
Theorem 1 follows immediately from combining Lemma 1 and Lemma 3 below. Note that ϵ1,2 = P(b1 > b2) −1/2 is the
distinguishability between the two best bandits. Due to strong stochastic transitivity, ϵ1,2 lower bounds the distinguishability
between the best bandit and any other bandit.
Analysis approach. Our analysis follows three phases. We ﬁrst bound the regret incurred for any match. Then we show that
the probability of IF making a mistake is at most 1/T . We ﬁnally bound the matches played by IF to arrive at our ﬁnal
regret bounds. The behavior of Interleaved Filter can be summarized by the following three lemmas, which we will prove
in Section 7, Section 8, and Section 9, respectively.
Lemma 1. The probability that IF makes a mistake resulting in the elimination of the best bandit b1 is at most 1/T .
Lemma 2. Assuming IF is mistake-free, then, with high probability,
RIF
T = O
 K log K
ϵ1,2
log T

for both strong and weak regret.
Lemma 3. Assuming IF is mistake-free, then
E
	
RIF
T

= O
 K
ϵ1,2
log T

for both strong and weak regret.

## Page 6

Y. Yue et al. / Journal of Computer and System Sciences 78 (2012) 1538–1556
1543
5. Conﬁdence intervals
In a match between bi and b j, Interleaved Filter (IF) maintains a number
ˆPi, j =
# bi wins
# comparisons,
(6)
which is the empirical estimate of P(bi > b j) after t comparisons.5 For ease of notation, we drop the subscripts (bi,b j), and
use ˆPt, which emphasizes the dependence on the number of comparisons. IF also maintains a conﬁdence interval
ˆCt = ( ˆPt −ct, ˆPt + ct),
(7)
where
ct =

4 log(1/δ)/t.
(8)
We justify the construction of these conﬁdence intervals in the following lemma.
Lemma 4. For δ = 1/(T K 2), the number of comparisons in a match between bi and b j is with high probability at most
O
 1
ϵ2
i, j
log(T K)

.
Moreover, the probability that the inferior bandit is declared the winner at some time t ⩽T is at most δ.
Proof. First we argue that the probability of the inferior bandit being declared the winner is at most δ. Note that by the
stopping condition of the match, if IF mistakenly declares the inferior bandit the winner at time t, then we must have
1/2 + ϵi, j /∈ˆCt (note that ϵi, j can be either positive or negative). By the deﬁnition of ˆCt and the fact that E[ ˆPt] = 1/2 + ϵi, j,
we have P(1/2 + ϵi, j /∈ˆCt) = P(| ˆPt −E[ ˆPt]| ⩾ct). It follows from Hoeffding’s inequality [16] that the probability of making
a mistake at time t is bounded above by
P
 ˆPt −E[ ˆPt]
 ⩾ct

⩽2 exp

−2tc2
t

= 2 exp

−8 log(1/δ)

= 2δ8 =
2
T 8K 16 .
Now an application of the union bound shows that the probability of making a mistake at any time t ⩽T is bounded above
by
P

T
t=1
{1/2 + ϵi, j /∈ˆCt}

⩽
2T
T 8K 16 ⩽
1
T K 2 = δ,
provided that K ⩾2, which is the desired result.
We now show that the number of comparisons n in a match between bi and b j is O(log(T K)/ϵ2
i, j) with high probability.
Speciﬁcally, we will show that for any d ⩾1, there exists an m depending only on d such that
P

n ⩾m
ϵ2
i, j
log(T K)

⩽(T K)−d
for all T, K suﬃciently large. By the stopping condition of the match, if at any time t we have ˆPt −ct > 1/2, then the match
terminates. It follows that for any time t, if n > t, then ˆPt −ct ⩽1/2, and so
P(n > t) ⩽P( ˆPt −ct ⩽1/2).
To bound this probability, assume without loss of generality that ϵi, j > 0, and note that since E[ ˆPt] = 1/2 + ϵi, j, we have
P( ˆPt −ct ⩽1/2) = P( ˆPt −1/2 −ϵi, j ⩽ct −ϵi, j) = P

E[ ˆPt] −ˆPt ⩾ϵi, j −ct

.
For any m ⩾8 and t ⩾⌈2m log(T K 2)/ϵ2
i, j⌉, we have ct ⩽ϵi, j/2, and so applying Hoeffding’s inequality for this m and t
shows
P

E[ ˆPt] −ˆPt ⩾ϵi, j −ct

⩽P
 ˆPt −E[ ˆPt]
 ⩾ϵi, j/2

⩽2 exp

−tϵ2
i, j/2

.
Since t ⩾2m log(T K 2)/ϵ2
i, j by assumption, we have tϵ2
i, j/2 ⩾m log(T K 2), and so
5 In other words, ˆPi, j is the fraction of these t comparisons in which bi was the winner.

## Page 7

1544
Y. Yue et al. / Journal of Computer and System Sciences 78 (2012) 1538–1556
2 exp

−tϵ2
i, j/2

⩽2 exp

−m log

T K 2
=
2
T mK 2m ⩽(T K)−m
for T ⩾1 and K ⩾2, which proves the claim.
2
6. Regret per match
We now bound the accumulated regret (both weak and strong) of each match.
Lemma 5. Assuming b1 has not been removed and T ⩾K , then with high probability the accumulated weak regret and also strong
regret from any match is at most
O
 1
ϵ1,2
log T

.
Proof. Suppose the candidate bandit ˆb = b j is playing a match against bi. Since all matches within a round are played
simultaneously, then by Lemma 4, any match played by b j contains at most
O
 1
ϵ2
1, j
log(T K)

= O
 1
ϵ2
1,2
log(T K)

comparisons, where the inequality follows from strong stochastic transitivity. Note that min{ϵ1, j,ϵ1,i} ⩽ϵ1, j. Then the accu-
mulated weak regret (2) is bounded by
ϵ1, jO
 1
ϵ2
1, j
log(T K)

= O
 1
ϵ1, j
log(T K)

= O
 1
ϵ1,2
log(T K)

= O
 1
ϵ1,2
log T

(9)
where (9) holds since log(T K) ⩽log(T 2) = 2 log T . We now bound the accumulated strong regret (1) by leveraging stochastic
triangle inequality. Each comparison incurs max{ϵ1, j,ϵ1,i} regret. We now consider three cases.
Case 1. Suppose bi ≻b j. Then max{ϵ1, j,ϵ1,i} = ϵ1, j, and the accumulated strong regret of the match is bounded by
ϵ1, jO
 1
ϵ2
1, j
log(T K)

= O
 1
ϵ1,2
log(T K)

.
Case 2. Suppose b j ≻bi and ϵ j,i ⩽ϵ1, j. Then
max{ϵ1, j + ϵ1,i} = ϵ1,i
⩽ϵ1, j + ϵ j,i
⩽2ϵ1, j
and the accumulated strong regret is bounded by
2ϵ1, jO
 1
ϵ2
1, j
log(T K)

= O
 1
ϵ1, j
log(T K)

= O
 1
ϵ1,2
log(T K)

.
Case 3. Suppose b j ≻bi and ϵ j,i > ϵ1, j. Then we can also use Lemma 4 to bound with high probability the number of
comparisons by
O
 1
ϵ2
j,i
log(T K)

.
The accumulated strong regret is then bounded by

## Page 8

Y. Yue et al. / Journal of Computer and System Sciences 78 (2012) 1538–1556
1545
2ϵ j,iO
 1
ϵ2
j,i
log(T K)

= O
 1
ϵ j,i
log(T K)

= O
 1
ϵ1, j
log(T K)

= O
 1
ϵ1,2
log(T K)

.
Like in the analysis for weak regret (9), we ﬁnally note that
O
 1
ϵ1,2
log(T K)

= O
 1
ϵ1,2
log T

.
2
7. Mistake bound
We now prove Lemma 1, which bounds the probability that IF makes a mistake by 1/T . It suﬃces to consider the
following two cases: (A) an inferior bandit defeats the candidate, and (B) a superior bandit was removed during the pruning
step (lines 16–18 in Algorithm 2). Case (A) is relatively straightforward to prove, and our analysis focuses primarily on
Case (B) in this section.
Lemma 6. For all triples of bandits b,b′, ˆb such that b ≻b′, the probability that IF eliminates b in a pruning step in which b′ wins a
match against the incumbent bandit ˆb (i.e. ˆP ˆb,b′ < 1/2) while b is found to be empirically inferior to ˆb (i.e. ˆP ˆb,b > 1/2) is at most δ.
Proof. Let X1, X2,... denote an inﬁnite sequence of i.i.d. Bernoulli random variables with E[Xi] = P(ˆb ≻b′), and let
Y1, Y2,... denote an inﬁnite sequence of i.i.d. Bernoulli random variables with E[Yi] = P(ˆb ≻b). We couple the outcomes
of the comparisons performed by the algorithm to the sequences (Xi), (Yi) in the obvious way: Xi (resp. Yi) represents the
outcome of the ith comparison between ˆb and b′ (resp. ˆb and b) if the algorithm performs at least i comparisons of that
pair of bandits; otherwise Xi (resp. Yi) does not correspond to any comparison observed by the algorithm.
If b is eliminated by IF in a pruning step at the end of a match consisting of n comparisons between b′ and the
incumbent ˆb, then X1,..., Xn represent the outcomes of the n matches between ˆb and b′ in that round, and Y1,..., Yn
represent the outcomes of the n matches between ˆb and b in that round. From the deﬁnition of conﬁdence intervals in IF
we know that X1 +···+ Xn < n/2−

4n log(1/δ), whereas the deﬁnition of the pruning step implies that Y1 +···+Yn > n/2.
Thus, if we deﬁne Zi = Yi −Xi for i = 1, 2,..., then we have
Z1 + ··· + Zn >

4n log(1/δ).
(10)
To complete the proof of the lemma, we will show the probability that there exists an n satisfying (10) is at most δT .
The random variables (Zi)∞
i=1 are i.i.d. and satisfy |Zi| ⩽1. Furthermore, our assumption that b ≻b′ together with strong
stochastic transitivity implies that
E[Zi] = P(ˆb ≻b) −P
ˆb ≻b′
⩽0.
By Hoeffding’s inequality, for every n the probability that n
i=1 Zi exceeds

4n log(1/δ) is at most exp(−8n log(1/δ)/
(4n)) = δ2. Taking the union bound over n = 1, 2,..., T , we ﬁnd that the probability that there exists an n satisfying (10) is
at most δ2T ⩽δ, as claimed.
2
Proof of Lemma 1. By Lemma 4, for every i the probability that b1 is eliminated in a match against bi is at most δ. A union
bound over all i implies that the probability of b1 being eliminated by directly losing a match to some other bandit is at
most δ(K −1). On the other hand, by Lemma 6, for all i, j the probability that b1 is eliminated in a pruning step resulting
from a match in which bi defeats b j is at most δ. A union bound over all i, j implies that the probability of b1 being
eliminated in a pruning step is at most δ(K −1)2. Summing these two bounds, the probability that IF makes a mistake
resulting in the elimination of b1 is at most δ[(K −1) + (K −1)2] < δK 2 = 1/T.
2
8. High probability exploration bound
In this section, we prove Lemma 2, which claims that mistake-free executions of IF satisfy
RIF
T = O
 K log K
ϵ1,2
log T


## Page 9

1546
Y. Yue et al. / Journal of Computer and System Sciences 78 (2012) 1538–1556
Fig. 1. An illustrative example of a sequence of candidate bandits. The incumbent candidate in each round is shaded in grey.
with high probability. This is within a log factor of the information-theoretic lower bound described in Section 10. The
analysis relies on proving that the number of candidate bandits selected by IF (i.e. the number of rounds) is O(log K) with
high probability.
We can model the sequence of candidate bandits as a random walk. Fig. 1 contains an illustrative example. Let b j denote
the incumbent candidate, and let pi denote the probability that bi will be the incumbent in the following round. Due to
strong stochastic transitivity, we know that p j−1 ⩽··· ⩽p1. We will see that the “worst case” scenario is the case where all
stochastic preferences are equal, i.e. ϵ j,k = ϵ. In this case, we have p j−1 = ··· = p1 = 1/( j −1) (assuming no mistakes are
made). This setting can be captured in the following Random Walk Model.
Deﬁnition 1 (Random Walk Model). Deﬁne a random walk graph with K nodes labeled b1,...,bK (these will correspond to
the similarly named bandits). Each node b j ( j > 1) transitions to bi for j > i ⩾1 with probability 1/( j −1), or in other
words b j transitions to b1,...,b j−1 with uniform probability. The ﬁnal node b1 is an absorbing node.
It is clear to see that a path in the Random Walk Model corresponds to a sequence of candidate bandits taken by IF in
an instance of the dueling bandits problem where ϵ1, j = ϵ2, j = ··· = ϵ j−1, j for all j > 1 (and no mistakes are made). Thus,
the path length of the random walk is exactly to the number of rounds in IF in that case. We will use the Random Walk
Model to bound the number of rounds in mistake-free executions of IF.
Proposition 1. Either IF makes a mistake, or else the number of rounds in the execution of IF is stochastically dominated by the path
length of a random walk in the Random Walk Model. In other words, if S and ˜S are random variables corresponding to the number of
rounds in IF and the Random Walk Model, respectively, then
∀x:
P(S ⩾x) ⩽P(˜S ⩾x).
As a consequence, any bound on the path length of the random walk also upper bounds the number of rounds in mistake-free executions
of IF.
Proposition 1 follows directly from Lemma 14 in Appendix B. This allows us to concentrate our analysis on the (simpler)
upper bound setting of the Random Walk Model. We will prove that the random walk in the Random Walk Model requires
O(log K) steps with high probability. Let Xi (1 ⩽i < K ) be an indicator random variable corresponding to whether a random
walk starting at bK visits bi in the Random Walk Model. We ﬁrst analyze the marginal probability of each P(Xi = 1), and
also show that X1,..., XK−1 are mutually independent.
Lemma 7. Let Xi be as deﬁned above with 1 ⩽i < K . Then
P(Xi = 1) = 1
i ,
and furthermore, for all W ⊆{X1,..., XK−1}, we can write P(W ) ≡P(
i∈W Xi) as
P(W ) =

Xi∈W
P(Xi),
(11)
meaning X1,..., XK−1 are mutually independent.
Proof. We can rewrite (11) as
P(W ) =

Xi∈W
P(Xi | Wi),
where Wi = {X j ∈W | j > i}.

## Page 10

Y. Yue et al. / Journal of Computer and System Sciences 78 (2012) 1538–1556
1547
We ﬁrst consider W = {X1,..., XK−1}. For the factor on Xi, denote with j the smallest index in Wi with X j = 1 in the
condition. Then
P(Xi = 1 | Xi+1,..., XK−1) = P(Xi = 1 | Xi+1 = 0, ..., X j−1 = 0, X j = 1) = 1
i ,
(12)
since, conditioned on Xi+1 = 0, ..., X j−1 = 0, X j = 1, the random walk must move to one of the ﬁrst i nodes with uniform
probability. Since (12) holds for all j > i, this implies P(Xi = 1) = 1
i . So we can conclude
P(X1,..., XK−1) =
K−1

i=1
P(Xi).
Now consider arbitrary W . We use 
W c to indicate summing over the joint states of all Xi variables not in W . We can
write P(W ) as
P(W ) =

W c
P(X1,..., XK−1)
=

W c
K−1

i=1
P(Xi)
=

Xi∈W
P(Xi)
 
W c

Xi∈W c
P(Xi)

=

Xi∈W
P(Xi).
This proves mutual independence (11).
2
We can express the number of steps taken by a random walk from bK to b1 in the Random Walk Model as
S K = 1 +
K−1

i=1
Xi.
(13)
Lemma 7 implies that
E[S K ] = 1 +
K−1

i=1
E[Xi] = 1 + H K−1 ≈log K,
where Hi is the harmonic sum. We now show that S K = O(log K) with high probability. We ﬁrst remark that one can
easily prove P(Xi = 1) ⩽1/i without using the Random Walk Model, if one deﬁnes the probabilities of the random walk of
candidates using the actual stochastic preferences ϵi, j. However, we also require that each Xi be independent of the others
in order to prove a high probability bound on S K .
Lemma 8. Assuming IF is mistake-free, then it runs for O(log K) rounds with high probability.
Proof. Due to Proposition 1, it suﬃces to analyze the distribution of path lengths in the Random Walk Model. It thus
suﬃces to show that for any d suﬃciently large, there exists an m depending only on d such that
∀K ⩾1:
P(S K > m log K) ⩽1
K d ,
(14)
for S K as deﬁned in (13). From Lemma 7, we know that the random variables X1,..., XK−1 in S K are mutually independent.
Then using the Chernoff bound [23], we know that for any m > 1,
P

S K > m(1 + H K−1)

⩽
em−1
mm
1+H K−1
⩽
em−1
mm
1+log K
= (eK)m−1−m logm
(15)
(15) is true since

## Page 11

1548
Y. Yue et al. / Journal of Computer and System Sciences 78 (2012) 1538–1556
log K ⩽H K−1 < log K + 1
for all K ⩾1. We require this bound to be at most 1/K d, or
(eK)m−1−m logm ⩽K −d.
The above inequality is satisﬁed by m ⩾d for d ⩾e. The Chernoff bound applies for all K ⩾0. So for any d ⩾e, we can
choose m = d to satisfy (14).
2
Corollary 1. Assuming IF is mistake-free, then it plays O(K log K) matches with high probability.
Proof. The result immediately follows from Lemma 8 by noting that IF plays at most O(K) matches in each round.
2
Proof of Lemma 2. The result immediately follows from combining Lemma 5 and Corollary 1.
2
9. Expected Regret Bound
In Section 9, we showed a high probability regret bound that is withing a log factor of the information-theoretic lower
bound described in Section 10. We now prove Lemma 3, which claims that mistake-free executions of IF satisfy
E
	
RIF
T

= O
 K
ϵ1,2
log T

,
which matches the information-theoretic lower bound up to constant factors.
Lemma 9. Assuming IF is mistake-free, then it plays O(K) matches in expectation.
Proof. Let B j denote a random variable counting the number of matches played by b j when it is not the incumbent (to
avoid double-counting). We can write B j as
B j = A j + G j,
where A j indicates the number of matches played by b j against bi for i > j (when the incumbent was inferior to b j), and
G j indicates the number of matches played by b j against bi for i < j (when the incumbent was superior to b j). We can
thus bound the expected number of matches played via
K−1

j=1
E[B j] =
K−1

j=1
E[A j] + E[G j].
(16)
By Lemma 7 and leveraging the Random Walk Model deﬁned in Section 8, we can write E[A j] as
E[A j] ⩽1 +
K−1

i= j+1
1
i = 1 + H K−1 −Hi,
where Hi is the harmonic sum.
We now analyze E[G j]. We assume the worst case that b j does not lose a match (with 1 −δ conﬁdence) to any superior
incumbent bi before the match concludes (bi is defeated) unless bi = b1. We can thus bound E[G j] using the probability
that b j is pruned at the conclusion of each round. Let E j,t denote the event that b j is pruned after the tth round in which
the incumbent bandit is superior to b j, conditioned on not being pruned in the ﬁrst t −1 such rounds. Deﬁne G j,t to
indicate the number of matches beyond the ﬁrst t −1 played by b j against a superior incumbent, conditioned on playing at
least t −1 such matches. We can write E[G j,t] as
E[G j,t] = 1 + P

Ec
j,t

E[G j,t+1],
and thus
E[G j] ⩽E[G j,1] ⩽1 + P

Ec
j,1

E[G j,2].
(17)
We know that P(Ec
j,t) ⩽1/2 for all j ̸= 1 and t. From Lemma 8, we know that E[G j,t] ⩽O(K log K) and is thus ﬁnite. Hence,
we can bound (17) by the inﬁnite geometric series 1 + 1/2 + 1/4 + ··· = 2.

## Page 12

Y. Yue et al. / Journal of Computer and System Sciences 78 (2012) 1538–1556
1549
We can thus write (16) as
K−1

j=1
E[A j] + E[G j] ⩽
K−1

j=1
(1 + H K−1 −H j) + 2(K −1)
=
K−1

j=1

1 +
K−1

i= j+1
1
i

+ 2(K −1)
=
K−1

j=1
( j −1)1
j + 3(K −1) = O(K).
2
Proof of Lemma 3. The proof follows immediately from combining Lemma 5 and Lemma 9.
2
10. Lower bounds
We now show that the bound in Theorem 1 is information theoretically optimal up to constant factors. The proof is
similar to the lower bound proof for the standard stochastic multi-armed bandit problem. However, since we make a number
of assumptions not present in the standard case (such as a total ordering of B), we present a simple self-contained lower
bound argument, rather than a reduction from the standard case.
Theorem 2. For any ﬁxed ϵ > 0 and any algorithm φ for the dueling bandits problem, there exists a problem instance such that
Rφ
T = Ω
 K
ϵ log T

,
where ϵ = minb̸=b∗P(b∗> b).
Here is a heuristic explanation of why we might suspect the theorem to be true. Rather than consider the general
problem of identifying the best of K bandits, suppose we are given a bandit b, and asked to determine with probability
at least 1 −1/T whether b is the best bandit. (Intuitively, the regret incurred by the optimal algorithm for this decision
problem should be a lower bound on the regret incurred by the optimal algorithm for the general problem.) We have seen
that, given two bandits bi and b j with P(bi > b j) = 1/2 + ϵ, we can identify the better bandit with probability at least
1 −1/T after O(log T/ϵ2) comparisons. If this is in fact the minimum number of comparisons required, then we would
suspect that any algorithm for the above decision problem that is uniformly good over all problem instances must perform
Ω(log T/ϵ2) comparisons involving each inferior bandit. We will see in Lemma 10 that this is in fact the case, and we begin
by constructing the appropriate problem instance.
Fix ϵ > 0 and deﬁne the following family of problem instances. In instance j, let b j be the best bandit, and order the
remaining bandits by their indices. That is, in instance j, we have b j ≻bk for all k ̸= j, and for i,k ̸= j, we have bi ≻bk
whenever i < k. Given this ordering, deﬁne the winning probabilities by P(bi > bk) = 1/2 + ϵ whenever bi ≻bk. Note that
this construction yields a valid problem instance, i.e. one that satisﬁes (3), (4).
Let q j be the distribution on T -step histories induced by a given algorithm φ under instance j, and let n j,T be the
number of comparisons involving bandit b j scheduled by φ up to time T. Using these instances, we prove Lemma 10, from
which Theorem 2 follows.
Lemma 10. Let φ be an algorithm for the dueling bandits problem such that
Rφ
T = o

T a
(18)
for all a > 0. Then for all j,
Eq1[n j,T ] = Ω
log T
ϵ2

.
Lemma 10 formalizes the intuition given above, in that any algorithm whose regret is o(T a) over all problem instances
must make Ω(log T/ϵ2) comparisons involving each inferior bandit, in expectation. The proof is motivated by Lemma 5
of [19].
Proof of Lemma 10. Fix an algorithm φ satisfying assumption (18), and ﬁx 0 < a < 1/2. Deﬁne the event E j = {n j,T <
log(T)/ϵ2}, and let J = { j: q1(E j) < 1/3}. For each j ∈J, we have by Markov’s inequality that

## Page 13

1550
Y. Yue et al. / Journal of Computer and System Sciences 78 (2012) 1538–1556
Eq1[n j,T ] ⩾q1

Ec
j

log(T)/ϵ2
= Ω
log T
ϵ2

,
so it remains to show that Eq1[n j,T ] = Ω(log T/ϵ2) for each j /∈J. For any j, we know that under q j, the algorithm φ
incurs regret ϵ for every comparison involving a bandit b ̸= b j. This fact together with the assumption (18) on φ implies
that Eq j[T −n j,T ] = o((T a)/ϵ). Using this fact, we have by Markov’s inequality that
q j(E j) = q j

T −n j,T > T −log(T)/ϵ2
⩽
Eq j[T −n j,T ]
T −log(T)/ϵ2 = o

T a−1
,
where the last equality follows from simpliﬁcation and the fact that ϵ is a ﬁxed constant which does not depend on T.
Choosing T suﬃciently large shows that q j(E j) < 1/3 for each j (and in particular, that 1 ∈J by construction). Now by
Lemma 6.3 of [18], we have that for any event E and distributions p,q with p(E) ⩾1/3 and q(E) < 1/3,
KL(p;q) ⩾1
3 ln

1
3q(E)

−1
e .
For each j /∈J, we may apply this lemma with q1, q j, and the event E j, to show
KL(q1;q j) ⩾1
3 ln

1
3o(T a−1)

−1
e
= Ω(log T).
(19)
On the other hand, by the chain rule for KL-divergence [11], we have
KL(q1;q j) ⩽Eq1[n j,T ] KL(1/2 + ϵ; 1/2 −ϵ)
⩽16ϵ2Eq1[n j,T ],
(20)
where we use the shorthand KL(1/2 + ϵ; 1/2 −ϵ) to denote the KL-divergence between two Bernoulli distributions with
parameters 1/2+ϵ and 1/2−ϵ, respectively. The ﬁrst inequality follows from the fact that if a comparison does not involve
bandit b j, then the distribution on the outcome of that comparison will be the same under distributions q1 and q j. To see
this, recall that by construction, under distribution q1, the bandits are ordered by their indices, so that for any two bandits
bi and bk, q1(bi > bk) = 1/2 + ϵ if and only if i < k. On the other hand, under distribution q j, bandit b j is the best bandit,
with all other bandits ordered by their indices, and so by construction, for any i,k ̸= j, we have q j(bi > bk) = 1/2 +ϵ if and
only if i < k. Thus, any comparison that does not involve bandit b j will have the same distribution on its outcome under q1
and q j.
The second inequality follows from a standard result on the KL-divergence between two Bernoulli distributions. Combin-
ing (19) and (20) shows that Eq1[n j,T ] = Ω(log T/ϵ2) for each j /∈J, which proves the lemma.
2
Proof of Theorem 2. Let φ be any algorithm for the dueling bandits problem. If φ does not satisfy the hypothesis of
Lemma 10, the theorem holds trivially. Otherwise, on the problem instance speciﬁed by q1, φ incurs regret at least ϵ
every time it plays a match involving b j ̸= b1. It follows from Lemma 10 that
Rφ
T ⩾

j̸=1
ϵEq1[n j,T ] = Ω
 K
ϵ log T

.
2
11. Discussion of related work
Algorithms for ﬁnding maximal elements in a noisy information model are discussed in [14]. That paper describes a
tournament-style algorithm that returns the best of K elements with probability 1 −δ in O(K log(1/δ)/ϵ2) comparisons,
where ϵ is the minimum margin of victory of one element over an inferior one. This is achieved by arranging the elements
in a binary tree and running a series of mini-tournaments, in which a parent and its two children compete until a winner
can be identiﬁed with high conﬁdence. Winning nodes are promoted to the parent position, and lower levels of the tree are
pruned to reduce the total number of comparisons. The maximal element eventually reaches the root of the tree with high
probability.
Such a tournament could incur very high regret in our framework. Consider a mini-tournament involving three subop-
timal but barely distinguishable elements (e.g. P(b∗> bi, j,k) ≈1, but P(bi > b j) = 1/2 + γ for γ ≪1). This tournament
would require Ω(1/γ 2) comparisons to determine the best element, but each comparison would contribute Ω(1) to the
total regret. Since γ can be arbitrarily small compared to ϵ∗= ϵ1,2, this yields a regret bound that can be arbitrarily worse
than the above lower bound. In general, algorithms that achieve low regret in our model must avoid such situations, and

## Page 14

Y. Yue et al. / Journal of Computer and System Sciences 78 (2012) 1538–1556
1551
must discard suboptimal bandits after as few comparisons as possible. This heuristic motivates the interleaved structure of
Interleaved Filter, which allows for good control over the number of matches involving suboptimal bandits.
As mentioned in Section 2, there are striking similarities between Interleaved Filter and the Successive Elimination
algorithm [12] for multi-armed bandit problems in the PAC setting, and there are also some key differences. The most
obvious difference is the fact that Interleaved Filter maintains an “incumbent” arm in each round that participates in many
more samples than the other arms, which is motivated by the need to eliminate highly suboptimal arms quickly in the
regret minimization setting. The Successive Elimination algorithm, on the other hand, samples every bandit arm uniformly
in every round. It would be interesting to see if a similar algorithm could also achieve optimal regret in the dueling bandits
regret minimization setting.
12. Conclusion
We have proposed a novel framework for partial information online learning in which feedback is derived from pairwise
comparisons, rather than absolute measures of utility. We have deﬁned a natural notion of regret for this problem, and
designed an algorithm that is information theoretically optimal for this performance measure. Our results extend previous
work on computing in noisy information models, and are motivated by practical considerations from information retrieval
applications. Future directions include ﬁnding other reasonable notions of regret in this framework (e.g., via contextualiza-
tion [22]), and designing algorithms that achieve low-regret when the set of bandits is very large (a special case of this is
addressed in [29]).
Acknowledgments
The work is funded by NSF Awards IIS-0812091 and IIS-0905467. The ﬁrst author is also supported by a Microsoft
Research Graduate Fellowship and a Yahoo! Key Scientiﬁc Challenges Award. The third author is supported by NSF Awards
CCF-0643934 and AF-0910940, an Alfred P. Sloan Foundation Fellowship, and a Microsoft Research New Faculty Fellowship.
Appendix A. Satisfying modeling assumptions
The following lemma describes a general family of probabilistic comparison models and proves that strong stochastic
transitivity and stochastic triangle inequality are both satisﬁed by this family of models. Note that both the logistic and
Gaussian models described in Section 3.1 are contained within this family of models.
Lemma 11. Let each bandit bi ∈{b1 ...bK } be associated with a distinct real value μi such that bi ≻b j ⇔μi > μ j, and that outcomes
from comparing two bandits are determined by
P(bi > b j) = σ(μi −μ j),
for some transfer function σ . Let σ satisfy the following properties:
• σ is monotonically increasing.
• σ(−∞) = 0.
• σ(∞) = 1.
• σ(x) = 1 −σ(−x) (rotation symmetric).
• σ(x) has a single inﬂection point at σ(0) = 1/2.
Then these probabilistic comparisons satisfy strong stochastic transitivity and stochastic triangle inequality.
Proof. We begin by noting that these properties essentially mean that σ behaves like a symmetric cumulative distribution
function with a single inﬂection point at σ(0) = 1/2 (i.e., σ is an “S-shaped” curve).
For any triplet of bandits bi ≻b j ≻bk, we know that μi > μ j > μk. To show strong stochastic transitivity, we ﬁrst note
that σ is monotonically increasing. Thus we know that σ(μi −μk) ⩾σ(μi −μ j) and σ(μi −μk) ⩾σ(μ j −μk), which
implies that
ϵi,k = σ(μi −μk) −1
2
⩾max

σ(μi −μ j) −1
2,σ(μ j −μk) −1
2

= max{ϵi, j,ϵ j,k}.

## Page 15

1552
Y. Yue et al. / Journal of Computer and System Sciences 78 (2012) 1538–1556
Round r
1
2
3
4
5
6
7
8
IF incumbent b(r)
b500
b150
b80
b25
b10
b6
b2
b1
Random walk incumbent ˜b(r)
b500
b250
b120
b65
b35
b15
b9
b5
Fig. 2. Showing an example coupled sequence for IF and the Random Walk Model drawn using a measure space deﬁned in Deﬁnition 2. At each round r,
the incumbent b(r) of IF is always superior to the incumbent ˜b(r) of the Random Walk Model, i.e. b(r) ≽˜b(r).
To show stochastic triangle inequality, we ﬁrst note that σ(x) is sub-additive, or concave, for x ⩾0. Deﬁne
α = μi −μ j
μi −μk
such that (μi −μ j) = α(μi −μk) and (μ j −μk) = (1 −α)(μi −μk). Then we know from concavity of σ that
ασ(μi −μk) + (1 −α)σ(0) ⩽σ(μi −μ j),
and also
(1 −α)σ(μi −μk) + ασ(0) ⩽σ(μ j −μk).
Adding the two inequalities above yields
σ(μi −μk) + σ(0) ⩽σ(μi −μ j) + σ(μ j −μk),
and thus
ϵi,k ⩽ϵi, j + ϵ j,k.
2
Appendix B. Analyzing the Random Walk Model
Let b(r) and ˜b(r) denote the candidate bandits in round r of IF and the Random Walk Model described in Deﬁnition 1,
respectively. Our analysis approach leverages a particular type of measure space (deﬁned in Deﬁnition 2 below) in order to
construct a stochastic coupling between IF and the Random Walk Model. This will allow us to draw coupled sequences of
candidates from the execution histories of IF and the Random Walk Model simultaneously. Fig. 2 shows an example pair of
sequences drawn using our measure space. Note that b(r) ≽˜b(r) at any round r. We will show in the following that:
• Measure spaces from Deﬁnition 2 deﬁne the correct distribution of sequences of candidates for IF.
• Measure spaces from Deﬁnition 2 deﬁne the correct distribution of sequences of candidates for the Random Walk
Model.
• Measure spaces from Deﬁnition 2 can be used to draw coupled sequences (one each from IF and the Random Walk
Model) such that b(r) ≽˜b(r) at any round r in any pair of sequences drawn.
• At least one such measure space exists.
This implies that the sequence of candidates in executions of IF is stochastically dominated by random walks in the Random
Walk Model. Hence, any bound on the random walk path length in the Random Walk Model also bounds the number of
rounds in IF.
Deﬁnition 2. We deﬁne a family of measure spaces M in the following way. Each point in the sample space is a joint
realization of the sequences of random variables Xrt
ij and Zr
i for every pair of bandits bi and b j, and positive integers r
and t. We will deﬁne a joint distribution over the random variables Xrt
ij and a conditional distribution over the Zr
i variables
given the Xrt
ij variables. The random variables and their distributions are explained in greater detail below.
• For every pair of bandits bi,b j, and positive integer r, there is a sequence of Bernoulli random variables Xrt
ij (for
t = 1, 2,...) describing the outcomes of comparisons in a match played by bi and b j in round r provided that bi is the
incumbent in that round. In particular Xrt
ij = 1 if bi wins the tth comparison between b j in round r, and Xrt
ij = 0 if bi
loses that comparison (i.e. P(Xrt
ij = 1) = 1/2 + ϵi, j). We will also deﬁne the following useful notation to denote prior
execution histories: X r
i is the σ -ﬁeld generated by the random variables {Xqt
ij : j ̸= i, q < r, t = 1, 2,...}.
• For a ﬁxed i, the random variables Xrt
ij are all mutually independent as one varies j,r,t, and they have the correct
distribution for each pair i, j. (In other words, the probability of bi beating b j is 1/2 + ϵij.)
• For convenience we also deﬁne Y r, for every positive integer r, to denote the identity of the incumbent in round r + 1
(i.e., the bandit that wins round r) when running algorithm IF with the comparison outcomes speciﬁed by {Xrt
ij }. Note
that the value (likewise distribution) of Y r is completely determined by the values (joint distribution) of Xrt
ij .

## Page 16

Y. Yue et al. / Journal of Computer and System Sciences 78 (2012) 1538–1556
1553
• For every bandit bi and positive integer r, there is a random variable Zr
i taking non-negative integer values, such that
the distribution of Y r + Zr
i , conditioned on X r
i , is uniform on 1,..., i −1 at every sample point where Y r−1 ⩽i and IF
does not make a mistake in rounds 1,...,r. (This will later be used to show that the Random Walk Model stochastically
dominates any mistake-free execution of IF.)
The values of Xrt
ij completely determine the history of execution of IF.6 Our independence assumptions ensure that the
history of play observed by IF has the correct distribution over histories.
Again, let b(r) and ˜b(r) denote the candidate bandits in round r of IF and the Random Walk Model, respectively. By
construction, b(r) follows the distribution deﬁned by Y r. We can show that ˜b(r) follows the distribution deﬁned by Y r + Zr
i .
As alluded to in the beginning of this section, this implies that b(r) ≽˜b(r) at any round r.
A priori, it is not obvious that measure spaces M satisfying Deﬁnition 2 exist; the constraint on the conditional distribu-
tion of Y r + Zr
i is non-trivial but we prove below that it is possible to design a measure space that satisﬁes this constraint,
i.e. M is not empty. We will then show how any measure space in M deﬁnes a stochastic coupling between the number
of rounds required in mistake-free executions of IF and the length of random walks in the Random Walk Model. To begin
proving that M is non-empty, we ﬁrst prove in Lemma 12 a constraint on the distribution of the Y r variables. This requires
us to introduce the following notation.
Deﬁnition 3. Let U(i,k,r,t | X r
i ) denote the collection of comparison sequences of length t in round r between the incum-
bent bi and each other remaining b j which results in bk being declared the winner after t comparisons. In other words,
an element in U(i,k,r,t | X r
i ) consists of a realization of each Xt′r
ij
for incumbent bi, all remaining b j, and time steps
1 ⩽t′ ⩽t.
Lemma 12. For any measure space in M, we have
∀r, ∀j ∈{1, 2,..., i −1}:
j

j′=1
P

Y r = j′  X r
i , Nr
⩾
j
i −1,
(B.1)
where bi denotes the incumbent bandit chosen by IF for round r, the Y r and Xrt
ij variables and the X r
i σ -ﬁeld are deﬁned as in
Deﬁnition 2, and Nr denotes the event that IF does not make a mistake in round r.
Proof. We ﬁrst deﬁne Nrti as the event that IF does not make a mistake in round r, that bi is the incumbent in that round,
and that IF makes exactly t comparisons between bi and each other remaining bandit in round r. This notation will be used
throughout the proof.
The proof can be decomposed into two stages. In Stage 1, we present a series of reductions and show that it suﬃces to
prove (B.4) below. In Stage 2, we prove (B.4).
Stage 1, reduction 1. To prove (B.1), it suﬃces to prove the following inequality,
∀t ⩾tmin, ∀r, ∀j ∈{1, 2,..., i −1}:
j

j′=1
P

Y r = j′  X r
i , Nrti
⩾
j
i −1,
(B.2)
where tmin denotes the minimum number of comparisons required for IF to determine a winner. Since (B.2) will be shown
to apply for all feasible t, i, then (B.1) will also hold.
Stage 1, reduction 2. To prove (B.2), it suﬃces to show that
∀1 ⩽j < k < i:
P

Y r = j
 X r
i , Nrti
⩾P

Y r = k
 X r
i , Nrti
,
(B.3)
since then (B.2) follows from iteratively applying the pigeonhole principle (for j = 1,..., i −1), and noting that
i−1

j′=1
P

Y r = j′  X r
i , Nrti
= 1.
Stage 1, reduction 3. Let U(i,k,r,t | X r
i ) be deﬁned as in Deﬁnition 3. To prove (B.3), we will deﬁne a bijection between
U(i, j,r,t | X r
i ) and U(i,k,r,t | X r
i ) for j < k such that
P

U

i, j,r,t
 X r
i
  X r
i , Nrt

⩾P

U

i,k,r,t
 X r
i
  X r
i , Nrti
.
(B.4)
6 Some of the values Xrt
ij are exposed as IF runs and schedules matches. Other values never get exposed. In particular, for pairs of bandits bi and b j
where neither is the incumbent in round r, the values Xrt
ij have no bearing on the history of play observed by IF.

## Page 17

1554
Y. Yue et al. / Journal of Computer and System Sciences 78 (2012) 1538–1556
It is straightforward to see that
P

Y r = k
 X r
i , Nrti
= P

U

i,k,r,t
 X r
i
  X r
i , Nrti
,
(B.5)
since U(i,k,r,t | X r
i ) contains exactly the comparison sequences that result in Y r = k given incumbent bi in round r.
Combined with (B.4), this directly implies (B.3), and thus completes the proof.
Stage 2, proving (B.4). The bijection is deﬁned as follows. Each uk ∈U(i,k,r,t | X r
i , Nrti) is mapped to the corresponding
u j ∈U(i, j,r,t | X r
i , Nrti) that consists of the same sequence of comparison realizations as uk, except that the comparison
realizations involving b j and bk are swapped (implying that b j is declared the winner).
To prove (B.4), it remains to show that P(u j | X r
i , Nrti) ⩾P(uk | X r
i , Nrti) for all u j, uk pairings in the bijection. In the
sequence of comparisons deﬁned by uk, let
A =
t
t′=1
Xrt′
ik
and
B =
t
t′=1
Xrt′
ij .
Note that A < B since bk wins the round.7 Also note that A and B are ﬁxed for any uk.8 Under the corresponding u j, the
two summations are reversed,
B =
t
t′=1
Xrt′
ik
and
A =
t
t′=1
Xrt′
ij ,
and all other sequences of variables Xrt′
ii′ for i′ ̸= j, i′ ̸= k remain the same.
Note that P(Xrt
ik = 1) ⩾P(Xrt
ij = 1), since bk is inferior to b j.9 We deﬁne p = P(Xrt
ij = 1) and q = P(Xrt
ik = 1). Since all the
Xrt′
ii′ variables are mutually independent, we can write the ratio of the conditional probabilities of u j and uk as
P(u j | X r
i , Nrti)
P(uk | X r
i , Nrti) =
P(t′
t=1 Xrt
ij = A)P(t′
t=1 Xrt
ik = B)
P(t′
t=1 Xrt
ij = B)P(t′
t=1 Xrt
ik = A)
= p A(1 −p)t′−AqB(1 −q)t′−B
pB(1 −p)t′−BqA(1 −q)t′−A
= p A−B(1 −q)A−B
qA−B(1 −p)A−B ⩾1,
where the ﬁrst equality follows from noting that all comparisons are independent and canceling out common terms (i.e., the
realizations of Xrt
ii′ for i′ ̸= j and i′ ̸= k), and the last inequality follows from noting that A < B and p ⩽q. This immediately
implies (B.4), and thus completes the proof.
2
Corollary 2. For the setting described in Lemma 12, we also have
∀r, ∀1 ⩽j < i ⩽i′:
j

j′=1
P

Y r = j′  X r
i , Nr
⩾
j
i′ −1.
Lemma 13. The family of measure spaces M deﬁned in Deﬁnition 2 is non-empty.
Proof. We will use the notation for Xrt
jk, Y r, Zr
j, X r
j as described in Deﬁnition 2. We will show that it is possible to
construct a distribution on the non-negative random variables Zr
j which satisﬁes the requirements of Deﬁnition 2. Since
we are conditioning on Xqt
ij for all q < r, then the value of Y r−1 is ﬁxed (i.e., we know who the incumbent is in round r).
Assume WLOG that Y r−1 = i (i.e., the incumbent in round r is bi). We will construct Zr
i based on the following two cases.
Case 1. IF does not make a mistake in round r and Y r−1 ⩽i (meaning the incumbent during round r was bi). We will use
the following ﬂow network to construct the conditional distribution of Y r + Zr
i (given X r
i and Nr),
• source s and sink t,
7 The incumbent bi wins the least number of comparisons with bk versus any other bandit.
8 In Deﬁnition 3, each element uk consists of a realization of all the comparisons. Thus A and B are ﬁxed for any uk.
9 By construction P(Xrt
ik = 1) = 1/2 + ϵi,k.

## Page 18

Y. Yue et al. / Journal of Computer and System Sciences 78 (2012) 1538–1556
1555
• vertices u1,..., ui−1,
• vertices v1,..., vi−1,
• edges from s to each u j with capacity P(Y r = j | X r
i , Nr),
• edges from each u j to vk where k ⩾j with inﬁnite capacity,
• edges from each vk to t with capacity 1/(i −1).
Lemma 12 and Corollary 2 imply that the minimum s–t cut of this network has capacity 1, and consequently the maximum
s–t ﬂow has value 1. In any maximum ﬂow, each edge (s, u j) and each edge (v j,t) (for 1 ⩽j ⩽i −1) must be saturated.
Given a maximum ﬂow, we can interpret the ﬂow on the edge from u j to vk to be the joint conditional probability P(Y r = j,
Zr
i = k −j | X r
i , Nr), from which we can recover the conditional distribution of Zr
i given X r
i
and Nr. The fact that the
conditional distribution of Y r + Zr
i is uniform on 1,..., i −1, given X r
i , Nr, follows from the fact that the ﬂow from vk to t
is exactly 1/(i −1) for every k.
Case 2. IF does make a mistake in round r or Y r−1 > i. Then we set Zr
i to some arbitrary non-negative integer, e.g., 0.
Thus, we have shown that there exists a feasible probability distribution on the Zr
i variables which satisﬁes the require-
ments of Deﬁnition 2. This implies that M is non-empty.
2
Lemma 14. The number of rounds in mistake-free executions of IF is stochastically dominated by the length of random walks in the
Random Walk Model.
Proof. Let b(r) and ˜b(r) be the incumbents chosen by IF and the Random Walk Model, respectively, at round r. It suﬃces to
construct a stochastic coupling between IF and the Random Walk Model such that b(r) ≽˜b(r) for all r.
We can take any measure space in M to construct this stochastic coupling, and we know from Lemma 13 that at least
one such measure space exists. There is one sample point for every possible joint outcome of the random variables Xrt
ij
and Zr
i . The execution of IF is determined by the Xrt
ij variables (note that b(r) = bi′ where i′ = Y r−1). Consider any execution
of IF that is mistake-free through rounds 1,..., s. The analogous execution of the Random Walk Model is determined by
looking at the sequence of incumbents when one runs a “perturbed” version of IF. The perturbation consists to taking the
identity of the incumbent in round r + 1 (for every r = 1,..., s) and modifying it by adding Zr
i (where bi is the incumbent
of “perturbed” IF in round r), and then executing round r + 1 using the perturbed incumbent instead of the one that would
ordinarily be chosen by IF. Both IF and “perturbed” IF start with the same initial incumbent at the beginning of round 1
chosen uniformly from 1,..., K .
It is now straightforward to see that this stochastic coupling holds from the deﬁnition of the Y r and Zr
i variables in
Deﬁnition 2, so long as the initial condition b(1) ≽˜b(1) holds. We ﬁnally note that b(1) = ˜b(1) by construction, which proves
the theorem.
2
References
[1] Jean-Yves Audibert, Sébastien Bubeck, Minimax policies for adversarial and stochastic bandits, in: Conference on Learning Theory (COLT), 2009.
[2] Peter Auer, Nicolò Cesa-Bianchi, Paul Fischer, Finite-time analysis of the multiarmed bandit problem, Mach. Learn. 47 (2) (2002) 235–256.
[3] Peter Auer, Nicolò Cesa-Bianchi, Yoav Freund, Robert Schapire, The nonstochastic multiarmed bandit problem, SIAM J. Comput. 32 (1) (2002) 48–77.
[4] Micah Adler, Peter Gemmell, Mor Harchol-Balter, Richard Karp, Claire Kenyon, Selection in the presence of noise: The design of playoff systems,
in: ACM–SIAM Symposium on Discrete Algorithms (SODA), 1994.
[5] Nir Ailon, Mehryar Mohri, An eﬃcient reduction of ranking to classiﬁcation, in: Conference on Learning Theory (COLT), 2008.
[6] Peter Auer, Using conﬁdence bounds for exploitation-exploration trade, J. Mach. Learn. Res. 3 (2003) 397–422.
[7] Maria-Florina Balcan, Nikhil Bansal, Alina Beygelzimer, Don Coppersmith, John Langford, Gregory Sorkin, Robust reductions from ranking to classiﬁca-
tion, in: Conference on Learning Theory (COLT), 2007.
[8] Michael Ben-Or, Avinatan Hassidim, The bayesian learner is optimal for noisy binary search (and pretty good for quantum as well), in: IEEE Symposium
on Foundations of Computer Science (FOCS), 2008.
[9] Nicolò Cesa-Bianchi, Gábor Lugosi, Gilles Stoltz, Regret minimization under partial monitoring, Math. Oper. Res. 31 (3) (2006) 562–580.
[10] William Cohen, Robert Schapire, Yoram Singer, Learning to order things, J. Artiﬁcial Intelligence Res. 10 (1999) 243–270.
[11] Thomas M. Cover, Joy A. Thomas, Elements of Information Theory, J. Wiley, 1999.
[12] Eyal Even-Dar, Shie Mannor, Yishay Mansour, Action elimination and stopping conditions for the multi-armed bandit and reinforcement learning
problems, J. Mach. Learn. Res. 7 (2006) 1079–1105.
[13] Yoav Freund, Raj Iyer, Robert Schapire, Yoram Singer, An eﬃcient boosting algorithm for combining preferences, J. Mach. Learn. Res. 4 (2003) 933–969.
[14] Uriel Feige, Prabhakar Raghavan, David Peleg, Eli Upfal, Computing with noisy information, SIAM J. Comput. 23 (5) (1994).
[15] Ralf Herbrich, Thore Graepel, Klaus Obermayer, Support vector learning for ordinal regression, in: International Conference on Artiﬁcial Neural Networks
(ICANN), 1999.
[16] Wassily Hoeffding, Probability inequalities for sums of bounded random variables, J. Amer. Statist. Assoc. 58 (1963) 13–30.
[17] Thorsten Joachims, A support vector method for multivariate performance measures, in: International Conference on Machine Learning (ICML), 2005.
[18] Richard M. Karp, Robert Kleinberg, Noisy binary search and its applications, in: ACM–SIAM Symposium on Discrete Algorithms (SODA), 2007.
[19] Robert Kleinberg, Alexandru Niculescu-Mizil, Yogeshwer Sharma, Regret bounds for sleeping experts and bandits, in: Conference on Learning Theory
(COLT), 2008.
[20] T.L. Lai, Herbert Robbins, Asymptotically eﬃcient adaptive allocation rules, Adv. in Appl. Math. 6 (1985) 4–22.
[21] Phil Long, Rocco Servedio, Boosting the area under the ROC curve, in: Proceedings of Neural Information Processing Systems (NIPS), 2007.

## Page 19

1556
Y. Yue et al. / Journal of Computer and System Sciences 78 (2012) 1538–1556
[22] John Langford, Tong Zhang, The epoch-greedy algorithm for contextual multi-armed bandits, in: Proceedings of Neural Information Processing Systems
(NIPS), 2007.
[23] Rajeev Motwani, Prabhakar Raghavan, Randomized Algorithms, Cambridge University Press, 1995.
[24] Shie Mannor, John N. Tsitsiklis, The sample complexity of exploration in the multi-armed bandit problem, J. Mach. Learn. Res. 5 (2004) 623–648.
[25] Sandeep Pandey, Deepak Agarwal, Deepayan Chakrabarti, Vanja Josifovski, Bandits for taxonomies: A model-based approach, in: SIAM Conference on
Data Mining (SDM), 2007.
[26] Filip Radlinski, Madhu Kurup, Thorsten Joachims, How does clickthrough data reﬂect retrieval quality?, in: ACM Conference on Information and Knowl-
edge Management (CIKM), 2008.
[27] Herbert Robbins, Some aspects of the sequential design of experiments, Bull. Amer. Math. Soc. 58 (1952) 527–535.
[28] Yisong Yue, Josef Broder, Robert Kleinberg, Thorsten Joachims, The k-armed dueling bandits problem, in: Conference on Learning Theory (COLT), 2009.
[29] Yisong Yue, Thorsten Joachims, Interactively optimizing information retrieval systems as a dueling bandits problem, in: International Conference on
Machine Learning (ICML), 2009.