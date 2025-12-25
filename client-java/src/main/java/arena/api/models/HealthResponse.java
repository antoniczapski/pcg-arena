package arena.api.models;

import com.fasterxml.jackson.annotation.JsonProperty;

public class HealthResponse {
    @JsonProperty("protocol_version")
    private String protocolVersion;
    
    private String status;
    
    @JsonProperty("build_info")
    private BuildInfo buildInfo;
    
    public static class BuildInfo {
        private String version;
        private String protocol;
        
        public String getVersion() { return version; }
        public void setVersion(String version) { this.version = version; }
        public String getProtocol() { return protocol; }
        public void setProtocol(String protocol) { this.protocol = protocol; }
    }
    
    public String getProtocolVersion() { return protocolVersion; }
    public void setProtocolVersion(String protocolVersion) { this.protocolVersion = protocolVersion; }
    public String getStatus() { return status; }
    public void setStatus(String status) { this.status = status; }
    public BuildInfo getBuildInfo() { return buildInfo; }
    public void setBuildInfo(BuildInfo buildInfo) { this.buildInfo = buildInfo; }
}

