package arena.config;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Client configuration loader.
 * Reads from CLI args, environment variables, or defaults.
 */
public class ClientConfig {
    private static final Logger logger = LoggerFactory.getLogger(ClientConfig.class);
    
    public static final String CLIENT_VERSION = "0.1.0";
    public static final String PROTOCOL_VERSION = "arena/v0";
    
    private final String baseUrl;
    private final String sessionId;
    
    private ClientConfig(String baseUrl, String sessionId) {
        this.baseUrl = baseUrl;
        this.sessionId = sessionId;
    }
    
    public static ClientConfig load(String[] args) {
        String baseUrl = getBaseUrl(args);
        String sessionId = java.util.UUID.randomUUID().toString();
        
        logger.info("Client configuration loaded:");
        logger.info("  Base URL: {}", baseUrl);
        logger.info("  Session ID: {}", sessionId.substring(0, 8) + "...");
        logger.info("  Client Version: {}", CLIENT_VERSION);
        logger.info("  Protocol Version: {}", PROTOCOL_VERSION);
        
        return new ClientConfig(baseUrl, sessionId);
    }
    
    private static String getBaseUrl(String[] args) {
        // Check CLI args first
        for (int i = 0; i < args.length - 1; i++) {
            if ("--base-url".equals(args[i])) {
                return args[i + 1];
            }
        }
        
        // Check environment variable
        String envUrl = System.getenv("ARENA_BASE_URL");
        if (envUrl != null && !envUrl.isEmpty()) {
            return envUrl;
        }
        
        // Default
        return "http://localhost:8080";
    }
    
    public String getBaseUrl() {
        return baseUrl;
    }
    
    public String getSessionId() {
        return sessionId;
    }
    
    public String getShortSessionId() {
        return sessionId.substring(0, 8);
    }
}

