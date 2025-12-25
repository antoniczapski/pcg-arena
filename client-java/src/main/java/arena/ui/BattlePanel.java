package arena.ui;

import arena.api.models.BattleResponse;

import javax.swing.*;
import java.awt.*;

/**
 * Panel displaying a battle (top and bottom levels vertically stacked).
 */
public class BattlePanel extends JPanel {
    private final TilemapView topView;
    private final TilemapView bottomView;
    private final JLabel topLabel;
    private final JLabel bottomLabel;
    private boolean generatorsRevealed = false;
    
    public BattlePanel() {
        setLayout(new BorderLayout());
        
        // Create main content panel (vertical layout)
        JPanel contentPanel = new JPanel(new GridLayout(2, 1, 0, 10));
        
        // Top level
        JPanel topPanel = new JPanel(new BorderLayout());
        topLabel = new JLabel("TOP LEVEL", SwingConstants.CENTER);
        topLabel.setFont(new Font("SansSerif", Font.BOLD, 12));
        topView = new TilemapView();
        JScrollPane topScroll = new JScrollPane(topView, 
            JScrollPane.VERTICAL_SCROLLBAR_NEVER,  // No vertical scrolling - tight Y-axis
            JScrollPane.HORIZONTAL_SCROLLBAR_AS_NEEDED);  // Horizontal scroll for wide levels
        // Set minimum height to accommodate 16-tile-high level (16 tiles * 4 pixels = 64 + some buffer)
        topScroll.setPreferredSize(new Dimension(800, 80));
        topPanel.add(topLabel, BorderLayout.NORTH);
        topPanel.add(topScroll, BorderLayout.CENTER);
        
        // Bottom level
        JPanel bottomPanel = new JPanel(new BorderLayout());
        bottomLabel = new JLabel("BOTTOM LEVEL", SwingConstants.CENTER);
        bottomLabel.setFont(new Font("SansSerif", Font.BOLD, 12));
        bottomView = new TilemapView();
        JScrollPane bottomScroll = new JScrollPane(bottomView,
            JScrollPane.VERTICAL_SCROLLBAR_NEVER,  // No vertical scrolling - tight Y-axis
            JScrollPane.HORIZONTAL_SCROLLBAR_AS_NEEDED);  // Horizontal scroll for wide levels
        // Set minimum height to accommodate 16-tile-high level (16 tiles * 4 pixels = 64 + some buffer)
        bottomScroll.setPreferredSize(new Dimension(800, 80));
        bottomPanel.add(bottomLabel, BorderLayout.NORTH);
        bottomPanel.add(bottomScroll, BorderLayout.CENTER);
        
        contentPanel.add(topPanel);
        contentPanel.add(bottomPanel);
        
        add(contentPanel, BorderLayout.CENTER);
    }
    
    /**
     * Display a battle.
     */
    public void displayBattle(BattleResponse.Battle battle) {
        generatorsRevealed = false;  // Reset state
        
        try {
            // Parse and display top level
            String topTilemap = battle.getTop().getLevelPayload().getTilemap();
            char[][] topGrid = TilemapParser.parse(topTilemap);
            topView.setTilemap(topGrid);
            
            // Initially hide generator names
            topLabel.setText("TOP LEVEL");
            
            // Parse and display bottom level
            String bottomTilemap = battle.getBottom().getLevelPayload().getTilemap();
            char[][] bottomGrid = TilemapParser.parse(bottomTilemap);
            bottomView.setTilemap(bottomGrid);
            
            // Initially hide generator names
            bottomLabel.setText("BOTTOM LEVEL");
            
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
        
        BattleResponse.Generator topGen = battle.getTop().getGenerator();
        String topGenId = topGen.getGeneratorId();
        String topGenIdShort = topGenId.length() >= 8 ? topGenId.substring(0, 8) : topGenId;
        topLabel.setText(String.format("TOP: %s v%s (ID: %s)", 
            topGen.getName(), 
            topGen.getVersion(),
            topGenIdShort));
        
        BattleResponse.Generator bottomGen = battle.getBottom().getGenerator();
        String bottomGenId = bottomGen.getGeneratorId();
        String bottomGenIdShort = bottomGenId.length() >= 8 ? bottomGenId.substring(0, 8) : bottomGenId;
        bottomLabel.setText(String.format("BOTTOM: %s v%s (ID: %s)", 
            bottomGen.getName(), 
            bottomGen.getVersion(),
            bottomGenIdShort));
    }
    
    /**
     * Clear the battle display.
     */
    public void clear() {
        topView.clear();
        bottomView.clear();
        topLabel.setText("TOP LEVEL");
        bottomLabel.setText("BOTTOM LEVEL");
        generatorsRevealed = false;
    }
}

