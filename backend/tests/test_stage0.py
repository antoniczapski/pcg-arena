"""
Stage 0 acceptance tests for PCG Arena backend.

Tests:
1. migrations + seed import populates expected counts
2. /v1/battles:next returns battle and inserts ISSUED row
3. voting updates ratings (LEFT win)
4. idempotent vote replay doesn't double-update
5. conflicting replay triggers DUPLICATE_VOTE_CONFLICT
"""

import uuid
import pytest


class TestMigrationsAndSeedImport:
    """Test 1: Migrations and seed import populate expected counts."""
    
    def test_migrations_applied(self, test_db):
        """Migrations are applied on startup."""
        # At least 2 migrations (001_init.sql, 002_indexes.sql)
        assert test_db["migrations_applied"] >= 2
    
    def test_generators_imported(self, test_db):
        """Generators are imported from seed data."""
        # Should have 3 generators (hopper, genetic, notch)
        assert test_db["generators"] == 3
    
    def test_levels_imported(self, test_db):
        """Levels are imported from seed data."""
        # Should have 30 levels (10 per generator × 3 generators)
        assert test_db["levels"] == 30
    
    def test_ratings_initialized(self, client):
        """All generators have ratings initialized."""
        response = client.get("/v1/leaderboard")
        assert response.status_code == 200
        
        data = response.json()
        assert data["protocol_version"] == "arena/v0"
        assert len(data["generators"]) == 3
        
        # All ratings should be 1000.0 initially
        for gen in data["generators"]:
            assert gen["rating"] == 1000.0
            assert gen["games_played"] == 0


class TestBattleCreation:
    """Test 2: /v1/battles:next returns battle and inserts ISSUED row."""
    
    def test_battle_creation_returns_valid_response(self, client):
        """Battle creation returns valid response with two levels."""
        session_id = str(uuid.uuid4())
        
        response = client.post("/v1/battles:next", json={
            "client_version": "0.1.0",
            "session_id": session_id,
        })
        
        assert response.status_code == 200
        data = response.json()
        
        # Check protocol version
        assert data["protocol_version"] == "arena/v0"
        
        # Check battle structure
        battle = data["battle"]
        assert "battle_id" in battle
        assert battle["battle_id"].startswith("btl_")
        assert "issued_at_utc" in battle
        assert "left" in battle
        assert "right" in battle
        
        # Check presentation config
        pres = battle["presentation"]
        assert pres["play_order"] == "LEFT_THEN_RIGHT"
        assert pres["reveal_generator_names_after_vote"] == True
        assert pres["suggested_time_limit_seconds"] == 300
        
        # Check left and right sides have different generators
        left_gen = battle["left"]["generator"]["generator_id"]
        right_gen = battle["right"]["generator"]["generator_id"]
        assert left_gen != right_gen
        
        # Check level payload
        assert "tilemap" in battle["left"]["level_payload"]
        assert "tilemap" in battle["right"]["level_payload"]
    
    def test_battle_persisted_with_issued_status(self, client):
        """Created battle is persisted with ISSUED status."""
        session_id = str(uuid.uuid4())
        
        # Create battle
        response = client.post("/v1/battles:next", json={
            "client_version": "0.1.0",
            "session_id": session_id,
        })
        assert response.status_code == 200
        battle_id = response.json()["battle"]["battle_id"]
        
        # Check in debug endpoint
        debug_response = client.get(f"/debug/battles?status=ISSUED&limit=100")
        assert debug_response.status_code == 200
        
        battles = debug_response.json()["battles"]
        battle_ids = [b["battle_id"] for b in battles]
        assert battle_id in battle_ids


class TestVotingUpdatesRatings:
    """Test 3: Voting updates ratings (LEFT win)."""
    
    def test_left_win_updates_ratings(self, client):
        """LEFT vote increases left generator rating, decreases right."""
        session_id = str(uuid.uuid4())
        
        # Get initial ratings
        initial_response = client.get("/v1/leaderboard")
        initial_data = initial_response.json()
        initial_ratings = {g["generator_id"]: g["rating"] for g in initial_data["generators"]}
        
        # Create battle
        battle_response = client.post("/v1/battles:next", json={
            "client_version": "0.1.0",
            "session_id": session_id,
        })
        assert battle_response.status_code == 200
        battle = battle_response.json()["battle"]
        battle_id = battle["battle_id"]
        left_gen_id = battle["left"]["generator"]["generator_id"]
        right_gen_id = battle["right"]["generator"]["generator_id"]
        
        # Submit LEFT vote
        vote_response = client.post("/v1/votes", json={
            "client_version": "0.1.0",
            "session_id": session_id,
            "battle_id": battle_id,
            "result": "LEFT",
            "tags": ["fun"],
        })
        assert vote_response.status_code == 200
        vote_data = vote_response.json()
        assert vote_data["accepted"] == True
        assert "vote_id" in vote_data
        
        # Check ratings changed
        final_response = client.get("/v1/leaderboard")
        final_data = final_response.json()
        final_ratings = {g["generator_id"]: g["rating"] for g in final_data["generators"]}
        
        # Left generator should have gained rating
        assert final_ratings[left_gen_id] > initial_ratings[left_gen_id]
        # Right generator should have lost rating
        assert final_ratings[right_gen_id] < initial_ratings[right_gen_id]
        
        # Check games_played incremented
        for gen in final_data["generators"]:
            if gen["generator_id"] in (left_gen_id, right_gen_id):
                assert gen["games_played"] >= 1


class TestIdempotentVoteReplay:
    """Test 4: Idempotent vote replay doesn't double-update."""
    
    def test_identical_vote_replay_accepted_without_double_update(self, client):
        """Replaying identical vote returns same result without double-updating ratings."""
        session_id = str(uuid.uuid4())
        
        # Create battle
        battle_response = client.post("/v1/battles:next", json={
            "client_version": "0.1.0",
            "session_id": session_id,
        })
        assert battle_response.status_code == 200
        battle = battle_response.json()["battle"]
        battle_id = battle["battle_id"]
        left_gen_id = battle["left"]["generator"]["generator_id"]
        
        vote_payload = {
            "client_version": "0.1.0",
            "session_id": session_id,
            "battle_id": battle_id,
            "result": "RIGHT",
            "tags": ["creative"],
        }
        
        # First vote
        vote1_response = client.post("/v1/votes", json=vote_payload)
        assert vote1_response.status_code == 200
        vote1_data = vote1_response.json()
        vote_id_1 = vote1_data["vote_id"]
        
        # Get rating after first vote
        rating1_response = client.get("/v1/leaderboard")
        rating1 = {g["generator_id"]: g["rating"] for g in rating1_response.json()["generators"]}
        
        # Replay identical vote
        vote2_response = client.post("/v1/votes", json=vote_payload)
        assert vote2_response.status_code == 200
        vote2_data = vote2_response.json()
        vote_id_2 = vote2_data["vote_id"]
        
        # Should return same vote_id
        assert vote_id_1 == vote_id_2
        
        # Get rating after replay
        rating2_response = client.get("/v1/leaderboard")
        rating2 = {g["generator_id"]: g["rating"] for g in rating2_response.json()["generators"]}
        
        # Ratings should NOT have changed (no double-update)
        assert rating1[left_gen_id] == rating2[left_gen_id]


class TestConflictingVoteReplay:
    """Test 5: Conflicting replay triggers DUPLICATE_VOTE_CONFLICT."""
    
    def test_different_payload_for_same_battle_rejected(self, client):
        """Submitting different payload for same battle returns conflict error."""
        session_id = str(uuid.uuid4())
        
        # Create battle
        battle_response = client.post("/v1/battles:next", json={
            "client_version": "0.1.0",
            "session_id": session_id,
        })
        assert battle_response.status_code == 200
        battle_id = battle_response.json()["battle"]["battle_id"]
        
        # First vote: LEFT
        vote1_response = client.post("/v1/votes", json={
            "client_version": "0.1.0",
            "session_id": session_id,
            "battle_id": battle_id,
            "result": "LEFT",
            "tags": [],
        })
        assert vote1_response.status_code == 200
        
        # Second vote: RIGHT (different result)
        vote2_response = client.post("/v1/votes", json={
            "client_version": "0.1.0",
            "session_id": session_id,
            "battle_id": battle_id,
            "result": "RIGHT",
            "tags": [],
        })
        
        # Should get 409 Conflict
        assert vote2_response.status_code == 409
        error_data = vote2_response.json()
        
        assert error_data["protocol_version"] == "arena/v0"
        assert error_data["error"]["code"] == "DUPLICATE_VOTE_CONFLICT"
        assert error_data["error"]["retryable"] == False

