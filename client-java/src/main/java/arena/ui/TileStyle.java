package arena.ui;

import java.awt.Color;

/**
 * Visual style for a tile character.
 */
public class TileStyle {
    public enum TileType {
        AIR, SOLID, COIN, PIPE, ENEMY, SPECIAL
    }
    
    private final TileType type;
    private final Color color;
    private final String label;
    
    public TileStyle(TileType type, Color color, String label) {
        this.type = type;
        this.color = color;
        this.label = label;
    }
    
    public TileType getType() { return type; }
    public Color getColor() { return color; }
    public String getLabel() { return label; }
    
    /**
     * Get visual style for a tile character.
     */
    public static TileStyle forChar(char c) {
        switch (c) {
            // Air
            case '-':
                return new TileStyle(TileType.AIR, new Color(135, 206, 235), "");
            
            // Solid blocks
            case 'X': // Ground
                return new TileStyle(TileType.SOLID, new Color(139, 69, 19), "");
            case '#': // Pyramid block
                return new TileStyle(TileType.SOLID, new Color(160, 82, 45), "#");
            case 'S': // Normal brick
                return new TileStyle(TileType.SOLID, new Color(178, 34, 34), "S");
            
            // Coins and collectibles
            case 'o': // Coin
                return new TileStyle(TileType.COIN, new Color(255, 215, 0), "o");
            case 'C': // Coin brick
                return new TileStyle(TileType.COIN, new Color(255, 215, 0), "C");
            case 'L': // Life brick
                return new TileStyle(TileType.COIN, new Color(0, 255, 127), "L");
            case 'U': // Special brick
                return new TileStyle(TileType.COIN, new Color(255, 165, 0), "U");
            case '@': // Special question block
                return new TileStyle(TileType.COIN, new Color(255, 140, 0), "@");
            case '!': // Coin question block
                return new TileStyle(TileType.COIN, new Color(255, 165, 0), "!");
            case '2': // Coin hidden block
                return new TileStyle(TileType.COIN, new Color(255, 215, 0), "2");
            case '1': // Life hidden block
                return new TileStyle(TileType.COIN, new Color(0, 255, 127), "1");
            case 'D': // Used block
                return new TileStyle(TileType.SOLID, new Color(160, 82, 45), "D");
            
            // Pipes and platforms
            case 't': // Pipe
                return new TileStyle(TileType.PIPE, new Color(34, 139, 34), "t");
            case 'T': // Pipe with flower
                return new TileStyle(TileType.PIPE, new Color(34, 139, 34), "T");
            case '|': // Platform background
                return new TileStyle(TileType.PIPE, new Color(100, 149, 237), "|");
            case '%': // Platform
                return new TileStyle(TileType.SOLID, new Color(139, 90, 43), "%");
            case '*': // Bullet Bill
                return new TileStyle(TileType.ENEMY, new Color(64, 64, 64), "*");
            
            // Enemies
            case 'g': // Goomba
                return new TileStyle(TileType.ENEMY, new Color(139, 69, 19), "g");
            case 'G': // Goomba winged
                return new TileStyle(TileType.ENEMY, new Color(139, 69, 19), "G");
            case 'r': // Red Koopa
                return new TileStyle(TileType.ENEMY, new Color(220, 20, 60), "r");
            case 'R': // Red Koopa winged
                return new TileStyle(TileType.ENEMY, new Color(220, 20, 60), "R");
            case 'k': // Green Koopa
                return new TileStyle(TileType.ENEMY, new Color(34, 139, 34), "k");
            case 'K': // Green Koopa winged
                return new TileStyle(TileType.ENEMY, new Color(34, 139, 34), "K");
            case 'y': // Spiky
                return new TileStyle(TileType.ENEMY, new Color(255, 69, 0), "y");
            case 'Y': // Spiky winged
                return new TileStyle(TileType.ENEMY, new Color(255, 69, 0), "Y");
            
            // Special markers
            case 'M': // Mario start
                return new TileStyle(TileType.SPECIAL, new Color(0, 255, 0), "M");
            case 'F': // Mario exit
                return new TileStyle(TileType.SPECIAL, new Color(255, 0, 255), "F");
            
            // Unknown (fallback)
            default:
                return new TileStyle(TileType.AIR, Color.GRAY, String.valueOf(c));
        }
    }
}

