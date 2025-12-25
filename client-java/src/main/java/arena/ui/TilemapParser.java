package arena.ui;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Parses and validates tilemap strings.
 */
public class TilemapParser {
    private static final Logger logger = LoggerFactory.getLogger(TilemapParser.class);
    private static final int EXPECTED_HEIGHT = 16;
    private static final int MIN_WIDTH = 1;
    private static final int MAX_WIDTH = 250;
    
    /**
     * Parse tilemap into 2D char array.
     * Validates dimensions only - accepts any character.
     * 
     * @throws IllegalArgumentException if tilemap dimensions are invalid
     */
    public static char[][] parse(String tilemap) throws IllegalArgumentException {
        if (tilemap == null || tilemap.isEmpty()) {
            throw new IllegalArgumentException("Tilemap is empty");
        }
        
        String[] lines = tilemap.split("\n");
        
        // Validate height
        if (lines.length != EXPECTED_HEIGHT) {
            throw new IllegalArgumentException(
                String.format("Invalid height: expected %d, got %d", EXPECTED_HEIGHT, lines.length)
            );
        }
        
        // Validate width consistency
        int width = lines[0].length();
        if (width < MIN_WIDTH || width > MAX_WIDTH) {
            throw new IllegalArgumentException(
                String.format("Invalid width: expected %d-%d, got %d", MIN_WIDTH, MAX_WIDTH, width)
            );
        }
        
        for (int i = 1; i < lines.length; i++) {
            if (lines[i].length() != width) {
                throw new IllegalArgumentException(
                    String.format("Inconsistent width: line 0 has %d chars, line %d has %d chars", 
                        width, i, lines[i].length())
                );
            }
        }
        
        // Parse into 2D array - accept any character
        char[][] grid = new char[EXPECTED_HEIGHT][width];
        for (int y = 0; y < EXPECTED_HEIGHT; y++) {
            for (int x = 0; x < width; x++) {
                grid[y][x] = lines[y].charAt(x);
            }
        }
        
        logger.info("Tilemap parsed successfully: {}x{}", width, EXPECTED_HEIGHT);
        return grid;
    }
}

