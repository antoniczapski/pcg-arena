"""
PCG Arena - Glicko-2 Rating System
Protocol: arena/v0

Implements the Glicko-2 rating system for pairwise comparisons.
Reference: http://www.glicko.net/glicko/glicko2.pdf

Key concepts:
- Rating (μ): Skill estimate (default 1500 in standard Glicko-2, we use 1000)
- Rating Deviation (RD/φ): Uncertainty in rating (high = uncertain)
- Volatility (σ): Expected fluctuation in player performance

The algorithm:
1. Convert ratings to Glicko-2 scale
2. Compute expected outcome
3. Update rating, RD, and volatility based on actual outcome
4. Convert back to display scale
"""

import math
import logging
from dataclasses import dataclass
from typing import Tuple

logger = logging.getLogger(__name__)

# Glicko-2 system constants
GLICKO2_SCALE = 173.7178  # Converts between Glicko-2 and display scale
TAU = 0.5  # System constant (constrains volatility change per period)
EPSILON = 0.000001  # Convergence tolerance for volatility iteration

# Default values (display scale)
DEFAULT_RATING = 1000.0
DEFAULT_RD = 350.0
DEFAULT_VOLATILITY = 0.06

# RD bounds (display scale)
MIN_RD = 30.0  # Very confident
MAX_RD = 350.0  # Very uncertain

# Rating bounds (display scale)
MIN_RATING = 100.0
MAX_RATING = 3000.0


@dataclass
class GlickoRating:
    """Represents a Glicko-2 rating with all components."""
    rating: float  # μ in display scale
    rd: float  # φ in display scale (RD)
    volatility: float  # σ
    
    def to_glicko2_scale(self) -> Tuple[float, float]:
        """Convert rating and RD to Glicko-2 scale (centered at 0)."""
        mu = (self.rating - DEFAULT_RATING) / GLICKO2_SCALE
        phi = self.rd / GLICKO2_SCALE
        return mu, phi
    
    @staticmethod
    def from_glicko2_scale(mu: float, phi: float, sigma: float) -> 'GlickoRating':
        """Convert from Glicko-2 scale back to display scale."""
        rating = mu * GLICKO2_SCALE + DEFAULT_RATING
        rd = phi * GLICKO2_SCALE
        
        # Clamp to bounds
        rating = max(MIN_RATING, min(MAX_RATING, rating))
        rd = max(MIN_RD, min(MAX_RD, rd))
        
        return GlickoRating(rating=rating, rd=rd, volatility=sigma)


def g(phi: float) -> float:
    """Glicko-2 g function: reduces impact based on opponent's uncertainty."""
    return 1.0 / math.sqrt(1.0 + 3.0 * phi * phi / (math.pi * math.pi))


def E(mu: float, mu_j: float, phi_j: float) -> float:
    """Expected score against opponent j."""
    return 1.0 / (1.0 + math.exp(-g(phi_j) * (mu - mu_j)))


def compute_variance(mu: float, opponent_mu: float, opponent_phi: float) -> float:
    """Compute variance v for a single game."""
    g_val = g(opponent_phi)
    e_val = E(mu, opponent_mu, opponent_phi)
    return 1.0 / (g_val * g_val * e_val * (1.0 - e_val))


def compute_delta(mu: float, opponent_mu: float, opponent_phi: float, score: float) -> float:
    """Compute delta (improvement) for a single game."""
    g_val = g(opponent_phi)
    e_val = E(mu, opponent_mu, opponent_phi)
    v = compute_variance(mu, opponent_mu, opponent_phi)
    return v * g_val * (score - e_val)


def compute_new_volatility(sigma: float, phi: float, v: float, delta: float) -> float:
    """
    Compute new volatility using iterative algorithm (Step 5 of Glicko-2).
    
    Uses the Illinois algorithm to find the root of f(x) = 0.
    """
    a = math.log(sigma * sigma)
    phi_sq = phi * phi
    
    def f(x: float) -> float:
        ex = math.exp(x)
        num = ex * (delta * delta - phi_sq - v - ex)
        denom = 2.0 * (phi_sq + v + ex) ** 2
        return num / denom - (x - a) / (TAU * TAU)
    
    # Initial bounds
    A = a
    
    if delta * delta > phi_sq + v:
        B = math.log(delta * delta - phi_sq - v)
    else:
        k = 1
        while f(a - k * TAU) < 0:
            k += 1
        B = a - k * TAU
    
    # Illinois algorithm
    f_A = f(A)
    f_B = f(B)
    
    iterations = 0
    max_iterations = 100
    
    while abs(B - A) > EPSILON and iterations < max_iterations:
        C = A + (A - B) * f_A / (f_B - f_A)
        f_C = f(C)
        
        if f_C * f_B <= 0:
            A = B
            f_A = f_B
        else:
            f_A = f_A / 2.0
        
        B = C
        f_B = f_C
        iterations += 1
    
    return math.exp(A / 2.0)


def update_rating_after_game(
    player: GlickoRating,
    opponent: GlickoRating,
    score: float  # 1.0 = win, 0.5 = tie, 0.0 = loss
) -> GlickoRating:
    """
    Update a player's rating after a single game.
    
    Args:
        player: Current player rating
        opponent: Opponent's rating
        score: Game outcome (1.0 = win, 0.5 = tie, 0.0 = loss)
    
    Returns:
        Updated player rating
    """
    # Step 1-2: Convert to Glicko-2 scale
    mu, phi = player.to_glicko2_scale()
    mu_j, phi_j = opponent.to_glicko2_scale()
    sigma = player.volatility
    
    # Step 3: Compute variance
    v = compute_variance(mu, mu_j, phi_j)
    
    # Step 4: Compute delta
    delta = compute_delta(mu, mu_j, phi_j, score)
    
    # Step 5: Compute new volatility
    sigma_new = compute_new_volatility(sigma, phi, v, delta)
    
    # Step 6: Update pre-rating period value
    phi_star = math.sqrt(phi * phi + sigma_new * sigma_new)
    
    # Step 7: Update rating and RD
    phi_new = 1.0 / math.sqrt(1.0 / (phi_star * phi_star) + 1.0 / v)
    
    g_val = g(phi_j)
    e_val = E(mu, mu_j, phi_j)
    mu_new = mu + phi_new * phi_new * g_val * (score - e_val)
    
    # Step 8: Convert back to display scale
    return GlickoRating.from_glicko2_scale(mu_new, phi_new, sigma_new)


def update_ratings_glicko2(
    left_rating: float,
    left_rd: float,
    left_volatility: float,
    right_rating: float,
    right_rd: float,
    right_volatility: float,
    result: str  # "LEFT", "RIGHT", "TIE", "SKIP"
) -> Tuple[GlickoRating, GlickoRating]:
    """
    Update both ratings after a match using Glicko-2.
    
    Args:
        left_rating: Left generator's current rating
        left_rd: Left generator's current RD
        left_volatility: Left generator's current volatility
        right_rating: Right generator's current rating
        right_rd: Right generator's current RD
        right_volatility: Right generator's current volatility
        result: Match outcome
    
    Returns:
        Tuple of (new_left_rating, new_right_rating) as GlickoRating objects
    """
    left = GlickoRating(rating=left_rating, rd=left_rd, volatility=left_volatility)
    right = GlickoRating(rating=right_rating, rd=right_rd, volatility=right_volatility)
    
    if result == "SKIP":
        # SKIP: No rating change, but RD might increase over time
        # For now, keep ratings unchanged
        return left, right
    
    # Determine scores
    if result == "LEFT":
        left_score = 1.0
        right_score = 0.0
    elif result == "RIGHT":
        left_score = 0.0
        right_score = 1.0
    elif result == "TIE":
        left_score = 0.5
        right_score = 0.5
    else:
        raise ValueError(f"Invalid result: {result}")
    
    # Update both ratings
    new_left = update_rating_after_game(left, right, left_score)
    new_right = update_rating_after_game(right, left, right_score)
    
    logger.info(
        f"Glicko-2 update: result={result} "
        f"left={left.rating:.1f}±{left.rd:.1f} -> {new_left.rating:.1f}±{new_left.rd:.1f} "
        f"right={right.rating:.1f}±{right.rd:.1f} -> {new_right.rating:.1f}±{new_right.rd:.1f}"
    )
    
    return new_left, new_right


def compute_expected_outcome(
    rating1: float, rd1: float,
    rating2: float, rd2: float
) -> float:
    """
    Compute expected outcome probability for player 1 winning.
    
    Args:
        rating1, rd1: Player 1's rating and RD
        rating2, rd2: Player 2's rating and RD
    
    Returns:
        Probability that player 1 wins (0.0 to 1.0)
    """
    # Convert to Glicko-2 scale
    mu1 = (rating1 - DEFAULT_RATING) / GLICKO2_SCALE
    phi1 = rd1 / GLICKO2_SCALE
    mu2 = (rating2 - DEFAULT_RATING) / GLICKO2_SCALE
    phi2 = rd2 / GLICKO2_SCALE
    
    return E(mu1, mu2, phi2)


def information_gain(rd1: float, rd2: float) -> float:
    """
    Estimate information gain from a match between two players.
    
    Higher when both players have high RD (uncertain ratings).
    Used by matchmaking to prioritize informative matches.
    
    Args:
        rd1, rd2: Rating deviations of both players
    
    Returns:
        Information gain estimate (higher = more informative)
    """
    # Normalize RDs to [0, 1] range
    norm_rd1 = (rd1 - MIN_RD) / (MAX_RD - MIN_RD)
    norm_rd2 = (rd2 - MIN_RD) / (MAX_RD - MIN_RD)
    
    # Combined uncertainty (geometric mean)
    return math.sqrt(norm_rd1 * norm_rd2)


def match_quality(
    rating1: float, rd1: float,
    rating2: float, rd2: float
) -> float:
    """
    Compute match quality (similar to TrueSkill's match quality).
    
    High quality matches are between players of similar skill
    where the outcome is uncertain.
    
    Args:
        rating1, rd1: Player 1's rating and RD
        rating2, rd2: Player 2's rating and RD
    
    Returns:
        Match quality score (0.0 to 1.0, higher = better match)
    """
    # Rating difference penalty
    rating_diff = abs(rating1 - rating2)
    combined_rd = math.sqrt(rd1 * rd1 + rd2 * rd2)
    
    # Quality based on how uncertain the outcome is
    # Best match is when expected outcome is close to 0.5
    expected = compute_expected_outcome(rating1, rd1, rating2, rd2)
    outcome_uncertainty = 1.0 - abs(2.0 * expected - 1.0)  # 1.0 when expected=0.5
    
    # Penalty for very large rating differences
    rating_penalty = math.exp(-rating_diff * rating_diff / (2 * combined_rd * combined_rd))
    
    return outcome_uncertainty * rating_penalty

