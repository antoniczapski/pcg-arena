package arena.api;

/**
 * Exception thrown when API calls fail.
 */
public class ArenaApiException extends Exception {
    private final String errorCode;
    private final boolean retryable;
    
    public ArenaApiException(String errorCode, String message, boolean retryable) {
        super(message);
        this.errorCode = errorCode;
        this.retryable = retryable;
    }
    
    public ArenaApiException(String message) {
        super(message);
        this.errorCode = "CLIENT_ERROR";
        this.retryable = false;
    }
    
    public ArenaApiException(String message, Throwable cause) {
        super(message, cause);
        this.errorCode = "CLIENT_ERROR";
        this.retryable = true;
    }
    
    public String getErrorCode() {
        return errorCode;
    }
    
    public boolean isRetryable() {
        return retryable;
    }
}

