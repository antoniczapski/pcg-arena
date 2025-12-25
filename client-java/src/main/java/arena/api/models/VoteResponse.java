package arena.api.models;

import com.fasterxml.jackson.annotation.JsonProperty;

public class VoteResponse {
    @JsonProperty("protocol_version")
    private String protocolVersion;
    
    private boolean accepted;
    
    @JsonProperty("vote_id")
    private String voteId;
    
    @JsonProperty("leaderboard_preview")
    private LeaderboardPreview leaderboardPreview;
    
    public static class LeaderboardPreview {
        @JsonProperty("updated_at_utc")
        private String updatedAtUtc;
        
        private java.util.List<LeaderboardGeneratorPreview> generators;
        
        public String getUpdatedAtUtc() { return updatedAtUtc; }
        public void setUpdatedAtUtc(String updatedAtUtc) { this.updatedAtUtc = updatedAtUtc; }
        public java.util.List<LeaderboardGeneratorPreview> getGenerators() { return generators; }
        public void setGenerators(java.util.List<LeaderboardGeneratorPreview> generators) { 
            this.generators = generators; 
        }
    }
    
    public static class LeaderboardGeneratorPreview {
        @JsonProperty("generator_id")
        private String generatorId;
        
        private String name;
        private double rating;
        
        @JsonProperty("games_played")
        private int gamesPlayed;
        
        public String getGeneratorId() { return generatorId; }
        public void setGeneratorId(String generatorId) { this.generatorId = generatorId; }
        public String getName() { return name; }
        public void setName(String name) { this.name = name; }
        public double getRating() { return rating; }
        public void setRating(double rating) { this.rating = rating; }
        public int getGamesPlayed() { return gamesPlayed; }
        public void setGamesPlayed(int gamesPlayed) { this.gamesPlayed = gamesPlayed; }
    }
    
    public String getProtocolVersion() { return protocolVersion; }
    public void setProtocolVersion(String protocolVersion) { this.protocolVersion = protocolVersion; }
    public boolean isAccepted() { return accepted; }
    public void setAccepted(boolean accepted) { this.accepted = accepted; }
    public String getVoteId() { return voteId; }
    public void setVoteId(String voteId) { this.voteId = voteId; }
    public LeaderboardPreview getLeaderboardPreview() { return leaderboardPreview; }
    public void setLeaderboardPreview(LeaderboardPreview leaderboardPreview) { 
        this.leaderboardPreview = leaderboardPreview; 
    }
}

