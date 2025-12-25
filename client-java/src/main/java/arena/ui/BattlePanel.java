package arena.ui;

import arena.api.models.BattleResponse;

import javax.swing.*;
import java.awt.*;

/**
 * Panel displaying a battle (left and right levels horizontally stacked).
 */
public class BattlePanel extends JPanel {
    private final TilemapView leftView;
    private final TilemapView rightView;
    private final JLabel leftLabel;
    private final JLabel rightLabel;
    private boolean generatorsRevealed = false;
    
    public BattlePanel() {
        setLayout(new BorderLayout());
        
        // Create main content panel (horizontal layout)
        JPanel contentPanel = new JPanel(new GridLayout(1, 2, 10, 0));
        
        // Left level
        JPanel leftPanel = new JPanel(new BorderLayout());
        leftLabel = new JLabel("LEFT LEVEL", SwingConstants.CENTER);
        leftLabel.setFont(new Font("SansSerif", Font.BOLD, 12));
        leftView = new TilemapView();
        JScrollPane leftScroll = new JScrollPane(leftView, 
            JScrollPane.VERTICAL_SCROLLBAR_NEVER,  // No vertical scrolling - tight Y-axis
            JScrollPane.HORIZONTAL_SCROLLBAR_AS_NEEDED);  // Horizontal scroll for wide levels
        // Set minimum height to accommodate 16-tile-high level (16 tiles * 4 pixels = 64 + some buffer)
        leftScroll.setPreferredSize(new Dimension(400, 80));
        leftPanel.add(leftLabel, BorderLayout.NORTH);
        leftPanel.add(leftScroll, BorderLayout.CENTER);
        
        // Right level
        JPanel rightPanel = new JPanel(new BorderLayout());
        rightLabel = new JLabel("RIGHT LEVEL", SwingConstants.CENTER);
        rightLabel.setFont(new Font("SansSerif", Font.BOLD, 12));
        rightView = new TilemapView();
        JScrollPane rightScroll = new JScrollPane(rightView,
            JScrollPane.VERTICAL_SCROLLBAR_NEVER,  // No vertical scrolling - tight Y-axis
            JScrollPane.HORIZONTAL_SCROLLBAR_AS_NEEDED);  // Horizontal scroll for wide levels
        // Set minimum height to accommodate 16-tile-high level (16 tiles * 4 pixels = 64 + some buffer)
        rightScroll.setPreferredSize(new Dimension(400, 80));
        rightPanel.add(rightLabel, BorderLayout.NORTH);
        rightPanel.add(rightScroll, BorderLayout.CENTER);
        
        contentPanel.add(leftPanel);
        contentPanel.add(rightPanel);
        
        add(contentPanel, BorderLayout.CENTER);
    }
    
    /**
     * Display a battle.
     */
    public void displayBattle(BattleResponse.Battle battle) {
        generatorsRevealed = false;  // Reset state
        
        try {
            // Parse and display left level
            String leftTilemap = battle.getLeft().getLevelPayload().getTilemap();
            char[][] leftGrid = TilemapParser.parse(leftTilemap);
            leftView.setTilemap(leftGrid);
            
            // Initially hide generator names
            leftLabel.setText("LEFT LEVEL");
            
            // Parse and display right level
            String rightTilemap = battle.getRight().getLevelPayload().getTilemap();
            char[][] rightGrid = TilemapParser.parse(rightTilemap);
            rightView.setTilemap(rightGrid);
            
            // Initially hide generator names
            rightLabel.setText("RIGHT LEVEL");
            
        } catch (Exception e) {
            clear();
            throw new RuntimeException("Failed to display battle: " + e.getMessage(), e);
        }
    }
    
    /**
     * Reveal generator names after voting.
     */
    public void revealGenerators(BattleResponse.Battle battle) {
        generatorsRevealed = true;
        
        BattleResponse.Generator leftGen = battle.getLeft().getGenerator();
        String leftGenId = leftGen.getGeneratorId();
        String leftGenIdShort = leftGenId.length() >= 8 ? leftGenId.substring(0, 8) : leftGenId;
        leftLabel.setText(String.format("LEFT: %s v%s (ID: %s)", 
            leftGen.getName(), 
            leftGen.getVersion(),
            leftGenIdShort));
        
        BattleResponse.Generator rightGen = battle.getRight().getGenerator();
        String rightGenId = rightGen.getGeneratorId();
        String rightGenIdShort = rightGenId.length() >= 8 ? rightGenId.substring(0, 8) : rightGenId;
        rightLabel.setText(String.format("RIGHT: %s v%s (ID: %s)", 
            rightGen.getName(), 
            rightGen.getVersion(),
            rightGenIdShort));
    }
    
    /**
     * Clear the battle display.
     */
    public void clear() {
        leftView.clear();
        rightView.clear();
        leftLabel.setText("LEFT LEVEL");
        rightLabel.setText("RIGHT LEVEL");
        generatorsRevealed = false;
    }
}
