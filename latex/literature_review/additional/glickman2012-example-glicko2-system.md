# Example of the Glicko-2 System

**Authors:** Mark E. Glickman
**Year:** 2012
**Source:** Technical Report, Boston University
**Citation Key:** `glickman2012glicko2`

---

## Extracted Content

<!-- Page 1 -->
Example of the Glicko-2 system
Professor Mark E. Glickman
Boston University
March 22, 2022
Every player in the Glicko-2 system has a rating, r, a rating deviation, RD, and a rating
volatility σ. The volatility measure indicates the degree of expected ﬂuctuation in a player’s
rating. The volatility measure is high when a player has erratic performances (e.g., when
the player has had exceptionally strong results after a period of stability), and the volatility
measure is low when the player performs at a consistent level. As with the original Glicko
system, it is usually informative to summarize a player’s strength in the form of an interval
(rather than merely report a rating). One way to do this is to report a 95% conﬁdence
interval. The lowest value in the interval is the player’s rating minus twice the RD, and the
highest value is the player’s rating plus twice the RD. So, for example, if a player’s rating
is 1850 and the RD is 50, the interval would go from 1750 to 1950. We would then say
that we’re 95% conﬁdent that the player’s actual strength is between 1750 and 1950. When
a player has a low RD, the interval would be narrow, so that we would be 95% conﬁdent
about a player’s strength being in a small interval of values. The volatility measure does not
appear in the calculation of this interval.
The formulas:
To apply the rating algorithm, we treat a collection of games within a “rating period” to have
occurred simultaneously. Players would have ratings, RD’s, and volatilities at the beginning
of the rating period, game outcomes would be observed, and then updated ratings, RD’s and
volatilities would be computed at the end of the rating period (which would then be used
as the pre-period information for the subsequent rating period). The Glicko-2 system works
best when the number of games in a rating period is moderate to large, say an average of at
least 10-15 games per player in a rating period. The length of time for a rating period is at
the discretion of the administrator.
The rating scale for Glicko-2 is diﬀerent from that of the original Glicko system. However, it
is easy to go back and forth between the two scales. The following steps assume that ratings
are on the original Glicko scale, but the formulas convert to the Glicko-2 scale, and then
convert back at the end to Glicko.
Step 1. Determine a rating and RD for each player at the onset of the rating period. The
system constant, τ, which constrains the change in volatility over time, needs to be
set prior to application of the system. Reasonable choices are between 0.3 and 1.2,
though the system should be tested to decide which value results in greatest predictive
accuracy. Smaller values of τ prevent the volatility measures from changing by large
1


<!-- Page 2 -->
amounts, which in turn prevent enormous changes in ratings based on very improbable
results.
If the application of Glicko-2 is expected to involve extremely improbable
collections of game outcomes, then τ should be set to a small value, even as small as,
say, τ = 0.2.
(a) If the player is unrated, set the rating to 1500 and the RD to 350. Set the player’s
volatility to 0.06 (this value depends on the particular application).
(b) Otherwise, use the player’s most recent rating, RD, and volatility σ.
Step 2. For each player, convert the ratings and RD’s onto the Glicko-2 scale:
µ
=
(r −1500)/173.7178
φ
=
RD/173.7178
The value of σ, the volatility, does not change.
We now want to update the rating of a player with (Glicko-2) rating µ, rating deviation
φ, and volatility σ.
He plays against m opponents with ratings µ1, . . . , µm, rating
deviations φ1, . . . , φm. Let s1, . . . , sm be the scores against each opponent (0 for a loss,
0.5 for a draw, and 1 for a win). The opponents’ volatilities are not relevant in the
calculations.
Step 3. Compute the quantity v.
This is the estimated variance of the team’s/player’s
rating based only on game outcomes.
v =


m
X
j=1
g(φj)2E(µ, µj, φj){1 −E(µ, µj, φj)}


−1
where
g(φ)
=
1
q
1 + 3φ2/π2,
E(µ, µj, φj)
=
1
1 + exp(−g(φj)(µ −µj)).
Step 4. Compute the quantity ∆, the estimated improvement in rating by comparing the
pre-period rating to the performance rating based only on game outcomes.
∆= v
m
X
j=1
g(φj){sj −E(µ, µj, φj)}
with g() and E() deﬁned above.
Step 5. Determine the new value, σ′, of the volatility. This computation requires iteration.
Note: This iterative procedure has been revised as of February 22, 2012, and is now
stable.
2


<!-- Page 3 -->
1. Let a = ln(σ2), and deﬁne
f(x) = ex(∆2 −φ2 −v −ex)
2(φ2 + v + ex)2
−(x −a)
τ 2
Also, deﬁne a convergence tolerance, ε. The value ε = 0.000001 is a suﬃciently
small choice.
2. Set the initial values of the iterative algorithm.
• Set A = a = ln(σ2)
• If ∆2 > φ2 + v, then set B = ln(∆2 −φ2 −v).
If ∆2 ≤φ2 + v, then perform the following iteration:
(i) Let k = 1
(ii) If f(a −kτ) < 0, then
Set k ←k + 1
Go to (ii).
and set B = a −kτ. The values A and B are chosen to bracket ln(σ′2), and
the remainder of the algorithm iteratively narrows this bracket.
3. Let fA = f(A) and fB = f(B).
4. While |B −A| > ε, carry out the following steps.
(a) Let C = A + (A −B)fA/(fB −fA), and let fC = f(C).
(b) If fCfB ≤0, then set A ←B and fA ←fB; otherwise, just set fA ←fA/2.
(c) Set B ←C and fB ←fC.
(d) Stop if |B −A| ≤ε. Repeat the above three steps otherwise.
5. Once |B −A| ≤ε, set
σ′ ←eA/2
Some comments: The original procedure, an application of the Newton-Raphson algorithm, turned out to be less stable than I realized. Even though the function to be
optimized was reasonably well-behaved (one local maximum that was a global maximum, continuous, diﬀerentiable, etc.), the algorithm occasionally did not converge due
to a poor starting value. Attempts to improve the choice of a starting value did not
result in any systematic method to salvage the algorithm, so I decided to start afresh
to produce a consistently stable numerical procedure.
The new algorithm is based on the so-called “Illinois algorithm,” a variant of the regula
falsi (false position) procedure. The Illinois algorithm is quite stable, reliable, and
converges quickly. The algorithm takes advantage of the knowledge that the desired
value of σ′ can be sandwiched at the start of the algorithm by the initial choices of A
and B. Other algorithms also would work well, such as the BFGS algorithm (but this
is a bit cumbersome to code), and bisection algorithms (though this can be slow to
converge).
A few technical comments about the above procedure:
3


<!-- Page 4 -->
• When ∆2 ≤φ2 + v, a special provision needs to be made to bracket ln(σ′2) which
requires searching values to the left of a = ln(σ2) in multiples of kτ. Based on
my tests, k is almost always 1, and very rarely 2 or more.
• The main iteration of the Illinois algorithm to narrow the bracket around ln(σ′2)
is reasonably quick. From simulation analyses, the median number of iterations
to narrow the bracket to a width of less than ε = 0.000001 was 5, with a mean of
5.6, and a maximum of 19 (in 10000 simulations).
Step 6. Update the rating deviation to the new pre-rating period value, φ∗:
φ∗=
q
φ2 + σ′2
Step 7. Update the rating and RD to the new values, µ′ and φ′:
φ′
=
1/
s
1
φ∗2 + 1
v
µ′
=
µ + φ′2
m
X
j=1
g(φj){sj −E(µ, µj, φj)}
Step 8. Convert ratings and RD’s back to original scale:
r′
=
173.7178µ′ + 1500
RD′
=
173.7178φ′
Note that if a player does not compete during the rating period, then only Step 6 applies. In
this case, the player’s rating and volatility parameters remain the same, but the RD increases
according to
φ′ = φ∗=
q
φ2 + σ2.
Example calculation:
Suppose a player rated 1500 competes against players rated 1400, 1550 and 1700, winning
the ﬁrst game and losing the next two. Assume the 1500-rated player’s rating deviation
is 200, and his opponents’ are 30, 100 and 300, respectively. Assume the 1500 player has
volatility σ = 0.06, and the system constant τ is 0.5.
Converting to the Glicko-2 scale, the player’s rating and RD become 0 and 1.1513. For the
opponents:
4


<!-- Page 5 -->
j
µj
φj
g(φj)
E(µ, µj, φj)
sj
1
−0.5756
0.1727
0.9955
0.639
1
2
0.2878
0.5756
0.9531
0.432
0
3
1.1513
1.7269
0.7242
0.303
0
We then compute
v
=

[(0.9955)2(0.639)(1 −0.639)
+(0.9531)2(0.432)(1 −0.432) + (0.7242)2(0.303)(1 −0.303)]
−1
=
1.7785
And now
∆
=
1.7785 (0.9955(1 −0.639) + 0.9531(0 −0.432) + 0.7242(0 −0.303))
=
−0.4834
The starting values in the iterative procedure are A = a = ln(0.062) = −5.62682, and (with
k = 1) B = a −kτ = −5.62682 −(1.0)(0.5) = −6.12682, with corresponding function values
computed as fA = −0.00053567 and fB = 1.999675. The following table summarizes the
iterations (iteration 0 corresponds to the initial values above):
Iteration
A
B
fA
fB
0
−5.62682
−6.12682
−0.00053567
1.999675
1
−5.62682
−5.62696
−0.00026784
0.000000015238
2
−5.62696
−5.62696
0.000000015238
0.000000015238
The iterative procedure therefore converges to A = −5.62696, so we set σ′ = e−5.62696/2 =
0.05999.
Now update to the new value of φ∗:
φ∗=
√
1.15132 + 0.059992 = 1.152862.
Next, update to the new values of φ′ and µ′:
φ′
=
1/
s
1
1.15292 +
1
1.7785 = 0.8722
µ′
=
0 + (0.8722)2 ×
[0.9955(1 −0.639)
+0.9531(0 −0.432)
+0.7242(0 −0.303)]
=
0 + 0.7607(−0.272) = −0.2069
5


<!-- Page 6 -->
Finally, convert back to the Glicko scale:
r′
=
−0.2069(173.7178) + 1500 = 1464.06
RD′
=
0.8722(173.7178) = 151.52
The new volatility σ′ = 0.05999.
Note that the resulting rating for this computation does not diﬀer much from the original
Glicko computation because the game outcomes do not provide any evidence of inconsistent
performance.
6
