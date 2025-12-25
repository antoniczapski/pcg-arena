package arena.api.models;

import com.fasterxml.jackson.annotation.JsonProperty;

public class BattleResponse {
    @JsonProperty("protocol_version")
    private String protocolVersion;
    
    private Battle battle;
    
    public static class Battle {
        @JsonProperty("battle_id")
        private String battleId;
        
        @JsonProperty("issued_at_utc")
        private String issuedAtUtc;
        
        @JsonProperty("expires_at_utc")
        private String expiresAtUtc;
        
        private LevelInfo top;
        private LevelInfo bottom;
        private Presentation presentation;
        
        public String getBattleId() { return battleId; }
        public void setBattleId(String battleId) { this.battleId = battleId; }
        public String getIssuedAtUtc() { return issuedAtUtc; }
        public void setIssuedAtUtc(String issuedAtUtc) { this.issuedAtUtc = issuedAtUtc; }
        public String getExpiresAtUtc() { return expiresAtUtc; }
        public void setExpiresAtUtc(String expiresAtUtc) { this.expiresAtUtc = expiresAtUtc; }
        public LevelInfo getTop() { return top; }
        public void setTop(LevelInfo top) { this.top = top; }
        public LevelInfo getBottom() { return bottom; }
        public void setBottom(LevelInfo bottom) { this.bottom = bottom; }
        public Presentation getPresentation() { return presentation; }
        public void setPresentation(Presentation presentation) { this.presentation = presentation; }
    }
    
    public static class LevelInfo {
        @JsonProperty("level_id")
        private String levelId;
        
        private Generator generator;
        private Format format;
        
        @JsonProperty("level_payload")
        private LevelPayload levelPayload;
        
        public String getLevelId() { return levelId; }
        public void setLevelId(String levelId) { this.levelId = levelId; }
        public Generator getGenerator() { return generator; }
        public void setGenerator(Generator generator) { this.generator = generator; }
        public Format getFormat() { return format; }
        public void setFormat(Format format) { this.format = format; }
        public LevelPayload getLevelPayload() { return levelPayload; }
        public void setLevelPayload(LevelPayload levelPayload) { this.levelPayload = levelPayload; }
    }
    
    public static class Generator {
        @JsonProperty("generator_id")
        private String generatorId;
        
        private String name;
        private String version;
        
        @JsonProperty("documentation_url")
        private String documentationUrl;
        
        public String getGeneratorId() { return generatorId; }
        public void setGeneratorId(String generatorId) { this.generatorId = generatorId; }
        public String getName() { return name; }
        public void setName(String name) { this.name = name; }
        public String getVersion() { return version; }
        public void setVersion(String version) { this.version = version; }
        public String getDocumentationUrl() { return documentationUrl; }
        public void setDocumentationUrl(String documentationUrl) { this.documentationUrl = documentationUrl; }
    }
    
    public static class Format {
        private String type;
        private int width;
        private int height;
        private String newline;
        
        public String getType() { return type; }
        public void setType(String type) { this.type = type; }
        public int getWidth() { return width; }
        public void setWidth(int width) { this.width = width; }
        public int getHeight() { return height; }
        public void setHeight(int height) { this.height = height; }
        public String getNewline() { return newline; }
        public void setNewline(String newline) { this.newline = newline; }
    }
    
    public static class LevelPayload {
        private String encoding;
        private String tilemap;
        
        public String getEncoding() { return encoding; }
        public void setEncoding(String encoding) { this.encoding = encoding; }
        public String getTilemap() { return tilemap; }
        public void setTilemap(String tilemap) { this.tilemap = tilemap; }
    }
    
    public static class Presentation {
        @JsonProperty("play_order")
        private String playOrder;
        
        @JsonProperty("reveal_generator_names_after_vote")
        private boolean revealGeneratorNamesAfterVote;
        
        @JsonProperty("suggested_time_limit_seconds")
        private int suggestedTimeLimitSeconds;
        
        public String getPlayOrder() { return playOrder; }
        public void setPlayOrder(String playOrder) { this.playOrder = playOrder; }
        public boolean isRevealGeneratorNamesAfterVote() { return revealGeneratorNamesAfterVote; }
        public void setRevealGeneratorNamesAfterVote(boolean reveal) { this.revealGeneratorNamesAfterVote = reveal; }
        public int getSuggestedTimeLimitSeconds() { return suggestedTimeLimitSeconds; }
        public void setSuggestedTimeLimitSeconds(int seconds) { this.suggestedTimeLimitSeconds = seconds; }
    }
    
    public String getProtocolVersion() { return protocolVersion; }
    public void setProtocolVersion(String protocolVersion) { this.protocolVersion = protocolVersion; }
    public Battle getBattle() { return battle; }
    public void setBattle(Battle battle) { this.battle = battle; }
}

