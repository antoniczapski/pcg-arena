package arena.ui;

import javax.swing.*;
import java.awt.*;

/**
 * Swing component that renders a tilemap grid.
 */
public class TilemapView extends JPanel {
    private static final int TILE_SIZE = 4; // pixels per tile
    
    private char[][] grid;
    private int width;
    private int height;
    
    public TilemapView() {
        setBackground(Color.BLACK);
    }
    
    /**
     * Set the tilemap to display.
     */
    public void setTilemap(char[][] grid) {
        this.grid = grid;
        if (grid != null && grid.length > 0) {
            this.height = grid.length;
            this.width = grid[0].length;
            setPreferredSize(new Dimension(width * TILE_SIZE, height * TILE_SIZE));
        } else {
            this.width = 0;
            this.height = 0;
            setPreferredSize(new Dimension(200, 100));
        }
        revalidate();
        repaint();
    }
    
    /**
     * Clear the tilemap.
     */
    public void clear() {
        this.grid = null;
        this.width = 0;
        this.height = 0;
        setPreferredSize(new Dimension(200, 100));
        revalidate();
        repaint();
    }
    
    @Override
    protected void paintComponent(Graphics g) {
        super.paintComponent(g);
        
        if (grid == null || grid.length == 0) {
            // Draw placeholder
            g.setColor(Color.GRAY);
            g.drawString("No level loaded", 10, 50);
            return;
        }
        
        Graphics2D g2d = (Graphics2D) g;
        
        // Draw tiles
        for (int y = 0; y < height; y++) {
            for (int x = 0; x < width; x++) {
                char tileChar = grid[y][x];
                TileStyle style = TileStyle.forChar(tileChar);
                
                int screenX = x * TILE_SIZE;
                int screenY = y * TILE_SIZE;
                
                // Draw tile background
                g2d.setColor(style.getColor());
                g2d.fillRect(screenX, screenY, TILE_SIZE, TILE_SIZE);
                
                // Draw label if tile is large enough and has a label
                // Note: With TILE_SIZE=4, labels are not drawn (too small)
                // This code is kept for future when TILE_SIZE might be increased
            }
        }
    }
}

