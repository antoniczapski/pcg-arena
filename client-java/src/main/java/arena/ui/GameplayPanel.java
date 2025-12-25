package arena.ui;

import arena.game.core.MarioGame;
import arena.game.core.MarioResult;
import arena.game.input.HumanAgent;

import javax.swing.*;
import java.awt.*;
import java.awt.event.KeyAdapter;
import java.awt.event.KeyEvent;

/**
 * Panel that embeds the Mario game engine and handles gameplay flow:
 * WAITING_TO_START -> PLAYING -> FINISHED
 */
public class GameplayPanel extends JPanel {
    public enum State {
        WAITING_TO_START,  // Show "Press SPACE to start" overlay
        PLAYING,           // Game is running
        FINISHED           // Game completed
    }

    private State state;
    private MarioGame game;
    private HumanAgent agent;
    private MarioResult result;
    private String levelText;
    private JLabel overlayLabel;

    public GameplayPanel() {
        setLayout(new BorderLayout());
        setPreferredSize(new Dimension(256 * 2, 240 * 2));
        setBackground(Color.BLACK);
        setFocusable(true);

        // Create overlay label for "Press SPACE to start"
        overlayLabel = new JLabel("Press SPACE to start", SwingConstants.CENTER);
        overlayLabel.setFont(new Font("Arial", Font.BOLD, 24));
        overlayLabel.setForeground(Color.WHITE);
        overlayLabel.setOpaque(false);
        add(overlayLabel, BorderLayout.CENTER);

        // Listen for SPACE key to start gameplay
        addKeyListener(new KeyAdapter() {
            @Override
            public void keyPressed(KeyEvent e) {
                if (e.getKeyCode() == KeyEvent.VK_SPACE && state == State.WAITING_TO_START) {
                    startGameplay();
                }
            }
        });

        state = State.WAITING_TO_START;
    }

    /**
     * Load a level and prepare for gameplay
     * @param levelText the level string to load
     * @param requestFocus if true, request focus for this panel
     */
    public void loadLevel(String levelText, boolean requestFocus) {
        this.levelText = levelText;
        this.state = State.WAITING_TO_START;
        this.result = null;
        
        // Clean up any existing game
        if (game != null) {
            game.stopGame();
            game = null;
        }
        agent = null;

        // Reset UI to show overlay
        removeAll();
        overlayLabel.setText("Press SPACE to start");
        add(overlayLabel, BorderLayout.CENTER);
        revalidate();
        repaint();
        
        if (requestFocus) {
            requestFocusInWindow();
        }
    }
    
    /**
     * Load a level without requesting focus (for convenience)
     */
    public void loadLevel(String levelText) {
        loadLevel(levelText, false);
    }

    /**
     * Start the gameplay (called when user presses SPACE)
     */
    private void startGameplay() {
        state = State.PLAYING;
        agent = new HumanAgent();
        game = new MarioGame();

        // Create render component but don't initialize yet
        game.initEmbeddedMode(2.0f, agent);

        // Remove overlay and add game render component
        removeAll();
        add(game.getRenderComponent(), BorderLayout.CENTER);
        revalidate();
        repaint();

        // CRITICAL: Initialize assets AFTER component is added to visible hierarchy
        // This ensures getGraphicsConfiguration() returns non-null
        SwingUtilities.invokeLater(() -> {
            // Now init() will work because component has valid GraphicsConfiguration
            game.getRenderComponent().init();
            
            // Start game in background with callback
            game.startGameEmbedded(levelText, 200, 0, (gameResult) -> {
                this.result = gameResult;
                this.state = State.FINISHED;
                SwingUtilities.invokeLater(() -> {
                    // Notify parent that game finished
                    firePropertyChange("gameFinished", false, true);
                });
            });

            // Give focus to render component for input
            game.getRenderComponent().requestFocusInWindow();
        });
    }

    /**
     * Get current state
     */
    public State getState() {
        return state;
    }

    /**
     * Get game result (null if not finished)
     */
    public MarioResult getResult() {
        return result;
    }

    /**
     * Check if level has been played (finished or stopped)
     */
    public boolean isPlayed() {
        return state == State.FINISHED;
    }

    /**
     * Stop gameplay early (for skip functionality)
     */
    public void stopGameplay() {
        if (game != null && state == State.PLAYING) {
            game.stopGame();
        }
    }
}

