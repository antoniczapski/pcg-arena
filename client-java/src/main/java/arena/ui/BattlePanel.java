package arena.ui;

import arena.api.models.BattleResponse;

import javax.swing.*;
import java.awt.*;

/**
 * Panel displaying a battle (left and right levels side-by-side).
 */
public class BattlePanel extends JPanel {
    private final TilemapView leftView;
    private final TilemapView rightView;
    private final JLabel leftLabel;
    private final JLabel rightLabel;
    
    public BattlePanel() {
        setLayout(new BorderLayout());
        
        // Create main content panel
        JPanel contentPanel = new JPanel(new GridLayout(1, 2, 10, 0));
        
        // Left side
        JPanel leftPanel = new JPanel(new BorderLayout());
        leftLabel = new JLabel("Left: No level", SwingConstants.CENTER);
        leftLabel.setFont(new Font("SansSerif", Font.BOLD, 12));
        leftView = new TilemapView();
        JScrollPane leftScroll = new JScrollPane(leftView);
        leftScroll.setPreferredSize(new Dimension(400, 300));
        leftPanel.add(leftLabel, BorderLayout.NORTH);
        leftPanel.add(leftScroll, BorderLayout.CENTER);
        
        // Right side
        JPanel rightPanel = new JPanel(new BorderLayout());
        rightLabel = new JLabel("Right: No level", SwingConstants.CENTER);
        rightLabel.setFont(new Font("SansSerif", Font.BOLD, 12));
        rightView = new TilemapView();
        JScrollPane rightScroll = new JScrollPane(rightView);
        rightScroll.setPreferredSize(new Dimension(400, 300));
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
        try {
            // Parse and display left level
            String leftTilemap = battle.getLeft().getLevelPayload().getTilemap();
            char[][] leftGrid = TilemapParser.parse(leftTilemap);
            leftView.setTilemap(leftGrid);
            
            BattleResponse.Generator leftGen = battle.getLeft().getGenerator();
            String leftGenId = leftGen.getGeneratorId();
            String leftGenIdShort = leftGenId.length() >= 8 ? leftGenId.substring(0, 8) : leftGenId;
            leftLabel.setText(String.format("LEFT: %s v%s (ID: %s)", 
                leftGen.getName(), 
                leftGen.getVersion(),
                leftGenIdShort));
            
            // Parse and display right level
            String rightTilemap = battle.getRight().getLevelPayload().getTilemap();
            char[][] rightGrid = TilemapParser.parse(rightTilemap);
            rightView.setTilemap(rightGrid);
            
            BattleResponse.Generator rightGen = battle.getRight().getGenerator();
            String rightGenId = rightGen.getGeneratorId();
            String rightGenIdShort = rightGenId.length() >= 8 ? rightGenId.substring(0, 8) : rightGenId;
            rightLabel.setText(String.format("RIGHT: %s v%s (ID: %s)", 
                rightGen.getName(), 
                rightGen.getVersion(),
                rightGenIdShort));
            
        } catch (Exception e) {
            clear();
            throw new RuntimeException("Failed to display battle: " + e.getMessage(), e);
        }
    }
    
    /**
     * Clear the battle display.
     */
    public void clear() {
        leftView.clear();
        rightView.clear();
        leftLabel.setText("Left: No level");
        rightLabel.setText("Right: No level");
    }
}

