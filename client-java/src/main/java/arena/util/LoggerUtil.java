package arena.util;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.File;

/**
 * Logger utilities for client-side logging.
 */
public class LoggerUtil {
    private static final Logger logger = LoggerFactory.getLogger(LoggerUtil.class);
    
    /**
     * Ensure log directory exists.
     */
    public static void ensureLogDirectory() {
        File logDir = new File("logs");
        if (!logDir.exists()) {
            boolean created = logDir.mkdirs();
            if (created) {
                logger.info("Created logs directory");
            }
        }
    }
    
    /**
     * Log an API request.
     */
    public static void logRequest(String method, String path) {
        logger.info("API Request: {} {}", method, path);
    }
    
    /**
     * Log an API response.
     */
    public static void logResponse(String method, String path, int statusCode) {
        logger.info("API Response: {} {} -> {}", method, path, statusCode);
    }
    
    /**
     * Log an API error.
     */
    public static void logError(String method, String path, String errorCode, String message) {
        logger.error("API Error: {} {} -> {} - {}", method, path, errorCode, message);
    }
    
    /**
     * Log battle information.
     */
    public static void logBattle(String battleId) {
        logger.info("Battle loaded: {}", battleId);
    }
    
    /**
     * Log vote submission.
     */
    public static void logVote(String battleId, String result, String voteId) {
        logger.info("Vote submitted: battle={}, result={}, vote_id={}", battleId, result, voteId);
    }
}

