package arena.util;

import java.time.Instant;
import java.time.ZoneId;
import java.time.format.DateTimeFormatter;

/**
 * Time utility functions.
 */
public class TimeUtil {
    /**
     * Get current ISO timestamp.
     */
    public static String now() {
        return Instant.now().toString();
    }
    
    /**
     * Format an ISO timestamp for display.
     */
    public static String formatTimestamp(String isoTimestamp) {
        try {
            Instant instant = Instant.parse(isoTimestamp);
            return DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss")
                .withZone(ZoneId.systemDefault())
                .format(instant);
        } catch (Exception e) {
            return isoTimestamp;
        }
    }
}

