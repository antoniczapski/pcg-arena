package arena.api.models;

import com.fasterxml.jackson.annotation.JsonProperty;
import java.util.Map;

public class BattleRequest {
    @JsonProperty("client_version")
    private String clientVersion;
    
    @JsonProperty("session_id")
    private String sessionId;
    
    @JsonProperty("player_id")
    private String playerId;
    
    private Map<String, Object> preferences;
    
    public BattleRequest(String clientVersion, String sessionId) {
        this.clientVersion = clientVersion;
        this.sessionId = sessionId;
        this.playerId = null;
        this.preferences = Map.of("mode", "standard");
    }
    
    public String getClientVersion() { return clientVersion; }
    public void setClientVersion(String clientVersion) { this.clientVersion = clientVersion; }
    public String getSessionId() { return sessionId; }
    public void setSessionId(String sessionId) { this.sessionId = sessionId; }
    public String getPlayerId() { return playerId; }
    public void setPlayerId(String playerId) { this.playerId = playerId; }
    public Map<String, Object> getPreferences() { return preferences; }
    public void setPreferences(Map<String, Object> preferences) { this.preferences = preferences; }
}

