package arena.api.models;

import com.fasterxml.jackson.annotation.JsonProperty;
import java.util.List;

public class LeaderboardResponse {
    @JsonProperty("protocol_version")
    private String protocolVersion;
    
    @JsonProperty("updated_at_utc")
    private String updatedAtUtc;
    
    private List<GeneratorRanking> generators;
    
    @JsonProperty("rating_system")
    private RatingSystem ratingSystem;
    
    public static class GeneratorRanking {
        private int rank;
        
        @JsonProperty("generator_id")
        private String generatorId;
        
        private String name;
        private String version;
        
        @JsonProperty("documentation_url")
        private String documentationUrl;
        
        private double rating;
        
        @JsonProperty("games_played")
        private int gamesPlayed;
        
        private int wins;
        private int losses;
        private int ties;
        private int skips;
        
        public int getRank() { return rank; }
        public void setRank(int rank) { this.rank = rank; }
        public String getGeneratorId() { return generatorId; }
        public void setGeneratorId(String generatorId) { this.generatorId = generatorId; }
        public String getName() { return name; }
        public void setName(String name) { this.name = name; }
        public String getVersion() { return version; }
        public void setVersion(String version) { this.version = version; }
        public String getDocumentationUrl() { return documentationUrl; }
        public void setDocumentationUrl(String documentationUrl) { this.documentationUrl = documentationUrl; }
        public double getRating() { return rating; }
        public void setRating(double rating) { this.rating = rating; }
        public int getGamesPlayed() { return gamesPlayed; }
        public void setGamesPlayed(int gamesPlayed) { this.gamesPlayed = gamesPlayed; }
        public int getWins() { return wins; }
        public void setWins(int wins) { this.wins = wins; }
        public int getLosses() { return losses; }
        public void setLosses(int losses) { this.losses = losses; }
        public int getTies() { return ties; }
        public void setTies(int ties) { this.ties = ties; }
        public int getSkips() { return skips; }
        public void setSkips(int skips) { this.skips = skips; }
    }
    
    public static class RatingSystem {
        private String name;
        
        @JsonProperty("initial_rating")
        private double initialRating;
        
        @JsonProperty("k_factor")
        private int kFactor;
        
        public String getName() { return name; }
        public void setName(String name) { this.name = name; }
        public double getInitialRating() { return initialRating; }
        public void setInitialRating(double initialRating) { this.initialRating = initialRating; }
        public int getKFactor() { return kFactor; }
        public void setKFactor(int kFactor) { this.kFactor = kFactor; }
    }
    
    public String getProtocolVersion() { return protocolVersion; }
    public void setProtocolVersion(String protocolVersion) { this.protocolVersion = protocolVersion; }
    public String getUpdatedAtUtc() { return updatedAtUtc; }
    public void setUpdatedAtUtc(String updatedAtUtc) { this.updatedAtUtc = updatedAtUtc; }
    public List<GeneratorRanking> getGenerators() { return generators; }
    public void setGenerators(List<GeneratorRanking> generators) { this.generators = generators; }
    public RatingSystem getRatingSystem() { return ratingSystem; }
    public void setRatingSystem(RatingSystem ratingSystem) { this.ratingSystem = ratingSystem; }
}

