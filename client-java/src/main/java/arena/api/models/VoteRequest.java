package arena.api.models;

import com.fasterxml.jackson.annotation.JsonProperty;
import java.util.List;
import java.util.Map;

public class VoteRequest {
    @JsonProperty("client_version")
    private String clientVersion;
    
    @JsonProperty("session_id")
    private String sessionId;
    
    @JsonProperty("battle_id")
    private String battleId;
    
    private String result;
    
    @JsonProperty("left_tags")
    private List<String> leftTags;
    
    @JsonProperty("right_tags")
    private List<String> rightTags;
    
    private Map<String, Object> telemetry;
    
    public VoteRequest(String clientVersion, String sessionId, String battleId, 
                      String result, List<String> leftTags, List<String> rightTags, Map<String, Object> telemetry) {
        this.clientVersion = clientVersion;
        this.sessionId = sessionId;
        this.battleId = battleId;
        this.result = result;
        this.leftTags = leftTags;
        this.rightTags = rightTags;
        this.telemetry = telemetry;
    }
    
    public String getClientVersion() { return clientVersion; }
    public void setClientVersion(String clientVersion) { this.clientVersion = clientVersion; }
    public String getSessionId() { return sessionId; }
    public void setSessionId(String sessionId) { this.sessionId = sessionId; }
    public String getBattleId() { return battleId; }
    public void setBattleId(String battleId) { this.battleId = battleId; }
    public String getResult() { return result; }
    public void setResult(String result) { this.result = result; }
    public List<String> getLeftTags() { return leftTags; }
    public void setLeftTags(List<String> leftTags) { this.leftTags = leftTags; }
    public List<String> getRightTags() { return rightTags; }
    public void setRightTags(List<String> rightTags) { this.rightTags = rightTags; }
    public Map<String, Object> getTelemetry() { return telemetry; }
    public void setTelemetry(Map<String, Object> telemetry) { this.telemetry = telemetry; }
}
