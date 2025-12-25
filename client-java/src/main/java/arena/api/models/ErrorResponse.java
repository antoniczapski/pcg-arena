package arena.api.models;

import com.fasterxml.jackson.annotation.JsonProperty;
import java.util.Map;

public class ErrorResponse {
    @JsonProperty("protocol_version")
    private String protocolVersion;
    
    private ErrorInfo error;
    
    public static class ErrorInfo {
        private String code;
        private String message;
        private boolean retryable;
        private Map<String, Object> details;
        
        public String getCode() { return code; }
        public void setCode(String code) { this.code = code; }
        public String getMessage() { return message; }
        public void setMessage(String message) { this.message = message; }
        public boolean isRetryable() { return retryable; }
        public void setRetryable(boolean retryable) { this.retryable = retryable; }
        public Map<String, Object> getDetails() { return details; }
        public void setDetails(Map<String, Object> details) { this.details = details; }
    }
    
    public String getProtocolVersion() { return protocolVersion; }
    public void setProtocolVersion(String protocolVersion) { this.protocolVersion = protocolVersion; }
    public ErrorInfo getError() { return error; }
    public void setError(ErrorInfo error) { this.error = error; }
}

