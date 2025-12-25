package arena.ui;

import arena.api.ArenaApiClient;
import arena.api.ArenaApiException;
import arena.api.models.BattleResponse;
import arena.api.models.LeaderboardResponse;
import arena.api.models.VoteResponse;
import arena.config.ClientConfig;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import javax.swing.*;
import java.awt.*;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * Main application window.
 */
public class MainWindow extends JFrame {
    private static final Logger logger = LoggerFactory.getLogger(MainWindow.class);
    
    // Allowed tags from spec (updated to match backend)
    private static final String[] ALLOWED_TAGS = {
        "fun", "boring", "good_flow", "creative", "unfair", 
        "confusing", "too_hard", "too_easy", "not_mario_like"
    };
    private static final int MAX_TAGS = 3;
    
    // UI state
    private enum State {
        STARTING,
        READY_NO_BATTLE,
        BATTLE_LOADED_WAITING_LEFT,      // Phase 2: Waiting for user to press SPACE on left level
        PLAYING_LEFT,                     // Phase 2: Playing left level
        LEFT_FINISHED_WAITING_RIGHT,     // Phase 2: Left finished, waiting for SPACE on right
        PLAYING_RIGHT,                    // Phase 2: Playing right level
        BOTH_FINISHED_READY_TO_VOTE,    // Phase 2: Both levels played, ready to vote
        BATTLE_LOADED_PENDING_VOTE,      // Phase 1: Static view (deprecated)
        SUBMITTING_VOTE,
        VOTED_SHOW_RESULT,
        ERROR_RECOVERABLE,
        ERROR_FATAL
    }
    
    private State currentState = State.STARTING;
    
    // Components
    private final ClientConfig config;
    private final ArenaApiClient apiClient;
    
    private JLabel statusLabel;
    private JLabel sessionLabel;
    private JLabel battleIdLabel;
    
    // Phase 2: Gameplay panels instead of static views
    private GameplayPanel leftGameplayPanel;
    private GameplayPanel rightGameplayPanel;
    private JLabel leftLabel;
    private JLabel rightLabel;
    private JLabel controlsLabel;  // Phase 2: Show controls
    
    // Phase 2: Telemetry storage
    private LevelPlayResult leftPlayResult;
    private LevelPlayResult rightPlayResult;
    
    private LeaderboardPanel leaderboardPanel;
    
    private JButton leftButton;
    private JButton rightButton;
    private JButton tieButton;
    private JButton skipButton;
    private JButton nextBattleButton;
    private JButton retryButton;
    
    private Map<String, JCheckBox> leftTagCheckboxes;
    private Map<String, JCheckBox> rightTagCheckboxes;
    
    // State
    private BattleResponse.Battle currentBattle;
    private VoteRequest pendingVote;
    
    // Inner class to hold retry info
    private static class VoteRequest {
        String sessionId;
        String battleId;
        String result;
        List<String> leftTags;
        List<String> rightTags;
        
        VoteRequest(String sessionId, String battleId, String result, List<String> leftTags, List<String> rightTags) {
            this.sessionId = sessionId;
            this.battleId = battleId;
            this.result = result;
            this.leftTags = new ArrayList<>(leftTags);
            this.rightTags = new ArrayList<>(rightTags);
        }
    }
    
    public MainWindow(ClientConfig config, ArenaApiClient apiClient) {
        super("PCG Arena Client v" + ClientConfig.CLIENT_VERSION);
        this.config = config;
        this.apiClient = apiClient;
        
        initUI();
        setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        pack();
        setLocationRelativeTo(null);
    }
    
    private void initUI() {
        setLayout(new BorderLayout(10, 10));
        
        // Top bar
        JPanel topBar = new JPanel(new GridLayout(3, 1));
        statusLabel = new JLabel("Status: Starting...", SwingConstants.CENTER);
        statusLabel.setFont(new Font("SansSerif", Font.BOLD, 12));
        sessionLabel = new JLabel("Session: " + config.getShortSessionId() + " | Backend: " + config.getBaseUrl(), SwingConstants.CENTER);
        battleIdLabel = new JLabel("Battle: -", SwingConstants.CENTER);
        topBar.add(statusLabel);
        topBar.add(sessionLabel);
        topBar.add(battleIdLabel);
        add(topBar, BorderLayout.NORTH);
        
        // Center: Main content with horizontal layout (left and right side by side)
        JPanel centerPanel = new JPanel();
        centerPanel.setLayout(new BoxLayout(centerPanel, BoxLayout.Y_AXIS));
        
        // === CONTROLS LABEL === (Phase 2)
        controlsLabel = new JLabel("Controls: Arrow Keys = Move, S = Jump, A = Run/Fire", SwingConstants.CENTER);
        controlsLabel.setFont(new Font("SansSerif", Font.BOLD, 14));
        controlsLabel.setAlignmentX(Component.CENTER_ALIGNMENT);
        centerPanel.add(controlsLabel);
        centerPanel.add(Box.createRigidArea(new Dimension(0, 5)));
        
        // === LEVELS PANEL (HORIZONTAL LAYOUT) ===
        JPanel levelsPanel = new JPanel(new GridLayout(1, 2, 10, 0));
        
        // === LEFT LEVEL === (Phase 2: GameplayPanel)
        JPanel leftLevelPanel = new JPanel(new BorderLayout());
        leftLabel = new JLabel("LEFT LEVEL", SwingConstants.CENTER);
        leftLabel.setFont(new Font("SansSerif", Font.BOLD, 12));
        leftGameplayPanel = new GameplayPanel();
        leftLevelPanel.add(leftLabel, BorderLayout.NORTH);
        leftLevelPanel.add(leftGameplayPanel, BorderLayout.CENTER);
        levelsPanel.add(leftLevelPanel);
        
        // Add property change listener for left level finish
        leftGameplayPanel.addPropertyChangeListener("gameFinished", evt -> {
            leftPlayResult = LevelPlayResult.fromMarioResult(leftGameplayPanel.getResult());
            setState(State.LEFT_FINISHED_WAITING_RIGHT);
            // Update labels and focus
            leftLabel.setText("LEFT LEVEL (1/2) - Finished!");
            rightLabel.setText("RIGHT LEVEL (2/2) - Press SPACE to start");
            setStatus("Left level finished! Press SPACE in right panel to play Level 2");
            // Give focus to right panel so SPACE works
            SwingUtilities.invokeLater(() -> {
                rightGameplayPanel.requestFocusInWindow();
            });
        });
        
        // === RIGHT LEVEL === (Phase 2: GameplayPanel)
        JPanel rightLevelPanel = new JPanel(new BorderLayout());
        rightLabel = new JLabel("RIGHT LEVEL", SwingConstants.CENTER);
        rightLabel.setFont(new Font("SansSerif", Font.BOLD, 12));
        rightGameplayPanel = new GameplayPanel();
        rightLevelPanel.add(rightLabel, BorderLayout.NORTH);
        rightLevelPanel.add(rightGameplayPanel, BorderLayout.CENTER);
        levelsPanel.add(rightLevelPanel);
        
        // Add property change listener for right level finish
        rightGameplayPanel.addPropertyChangeListener("gameFinished", evt -> {
            rightPlayResult = LevelPlayResult.fromMarioResult(rightGameplayPanel.getResult());
            
            // Check if left was played - if not, something went wrong (right started first)
            if (leftPlayResult == null && leftGameplayPanel.getState() == GameplayPanel.State.WAITING_TO_START) {
                // Right started before left - this shouldn't happen, but recover by starting left
                setState(State.BATTLE_LOADED_WAITING_LEFT);
                rightLabel.setText("RIGHT LEVEL (2/2) - Wait for left level");
                leftLabel.setText("LEFT LEVEL (1/2) - Press SPACE to start");
                setStatus("Left level not played yet! Press SPACE in left panel to play Level 1");
                SwingUtilities.invokeLater(() -> {
                    leftGameplayPanel.requestFocusInWindow();
                });
            } else {
                // Normal flow - both levels finished
                setState(State.BOTH_FINISHED_READY_TO_VOTE);
                rightLabel.setText("RIGHT LEVEL (2/2) - Finished!");
                setStatus("Both levels finished! Vote now");
            }
        });
        
        centerPanel.add(levelsPanel);
        
        // Add spacing
        centerPanel.add(Box.createRigidArea(new Dimension(0, 10)));
        
        // === TAG PANELS (HORIZONTAL LAYOUT) ===
        JPanel tagsPanel = new JPanel(new GridLayout(1, 2, 10, 0));
        
        // === LEFT LEVEL TAGS ===
        JPanel leftTagPanel = new JPanel(new FlowLayout(FlowLayout.LEFT));
        leftTagPanel.add(new JLabel("Left level tags (max 3):"));
        leftTagCheckboxes = new HashMap<>();
        for (String tag : ALLOWED_TAGS) {
            JCheckBox cb = new JCheckBox(tag);
            cb.addActionListener(e -> enforceMaxTags(leftTagCheckboxes));
            leftTagCheckboxes.put(tag, cb);
            leftTagPanel.add(cb);
        }
        tagsPanel.add(leftTagPanel);
        
        // === RIGHT LEVEL TAGS ===
        JPanel rightTagPanel = new JPanel(new FlowLayout(FlowLayout.LEFT));
        rightTagPanel.add(new JLabel("Right level tags (max 3):"));
        rightTagCheckboxes = new HashMap<>();
        for (String tag : ALLOWED_TAGS) {
            JCheckBox cb = new JCheckBox(tag);
            cb.addActionListener(e -> enforceMaxTags(rightTagCheckboxes));
            rightTagCheckboxes.put(tag, cb);
            rightTagPanel.add(cb);
        }
        tagsPanel.add(rightTagPanel);
        
        centerPanel.add(tagsPanel);
        
        // Add spacing
        centerPanel.add(Box.createRigidArea(new Dimension(0, 10)));
        
        // === VOTE BUTTONS ===
        JPanel voteButtonsPanel = new JPanel(new FlowLayout());
        leftButton = new JButton("Left Better");
        rightButton = new JButton("Right Better");
        tieButton = new JButton("Tie");
        skipButton = new JButton("Skip");
        leftButton.addActionListener(e -> vote("LEFT"));
        rightButton.addActionListener(e -> vote("RIGHT"));
        tieButton.addActionListener(e -> vote("TIE"));
        skipButton.addActionListener(e -> vote("SKIP"));
        voteButtonsPanel.add(leftButton);
        voteButtonsPanel.add(rightButton);
        voteButtonsPanel.add(tieButton);
        voteButtonsPanel.add(skipButton);
        centerPanel.add(voteButtonsPanel);
        
        // === ACTION BUTTONS ===
        JPanel actionPanel = new JPanel(new FlowLayout());
        nextBattleButton = new JButton("Next Battle");
        nextBattleButton.addActionListener(e -> fetchBattle());
        retryButton = new JButton("Retry Submit");
        retryButton.addActionListener(e -> retryVote());
        retryButton.setVisible(false);
        actionPanel.add(nextBattleButton);
        actionPanel.add(retryButton);
        centerPanel.add(actionPanel);
        
        // Wrap in scroll pane
        JScrollPane centerScroll = new JScrollPane(centerPanel);
        centerScroll.setHorizontalScrollBarPolicy(JScrollPane.HORIZONTAL_SCROLLBAR_NEVER);
        add(centerScroll, BorderLayout.CENTER);
        
        // Bottom: Leaderboard
        leaderboardPanel = new LeaderboardPanel();
        add(leaderboardPanel, BorderLayout.SOUTH);
        
        updateUIState();
    }
    
    /**
     * Perform health check and initial setup.
     */
    public void start() {
        SwingUtilities.invokeLater(() -> {
            try {
                setStatus("Checking backend health...");
                apiClient.health();
                setStatus("Backend OK - Loading first battle...");
                
                // Auto-fetch first leaderboard and battle
                fetchLeaderboard();
                fetchBattle();
            } catch (ArenaApiException e) {
                logger.error("Health check failed", e);
                if ("PROTOCOL_MISMATCH".equals(e.getErrorCode())) {
                    showFatalError("Protocol Mismatch", e.getMessage());
                } else {
                    showFatalError("Backend Unreachable", 
                        "Cannot connect to backend at " + config.getBaseUrl() + "\n\n" + e.getMessage());
                }
            }
        });
    }
    
    /**
     * Fetch next battle.
     */
    private void fetchBattle() {
        setState(State.READY_NO_BATTLE);
        setStatus("Fetching battle...");
        
        new Thread(() -> {
            try {
                BattleResponse response = apiClient.nextBattle(config.getSessionId());
                SwingUtilities.invokeLater(() -> {
                    currentBattle = response.getBattle();
                    battleIdLabel.setText("Battle: " + currentBattle.getBattleId());
                    displayBattle(currentBattle);
                    clearTags();
                    // Phase 2: Reset telemetry
                    leftPlayResult = null;
                    rightPlayResult = null;
                    // Phase 2: Transition to waiting for left level play
                    setStatus("Press SPACE in left panel to play Level 1");
                    setState(State.BATTLE_LOADED_WAITING_LEFT);
                });
            } catch (ArenaApiException e) {
                SwingUtilities.invokeLater(() -> handleApiError(e, "fetch battle"));
            }
        }).start();
    }
    
    /**
     * Display a battle (Phase 2: Load into GameplayPanels).
     */
    private void displayBattle(BattleResponse.Battle battle) {
        try {
            // Load right level first (without focus) to avoid focus race
            String rightTilemap = battle.getRight().getLevelPayload().getTilemap();
            rightGameplayPanel.loadLevel(rightTilemap, false);
            rightLabel.setText("RIGHT LEVEL (2/2) - Wait for left level to finish");
            
            // Load left level last WITH focus - this ensures left panel gets focus
            String leftTilemap = battle.getLeft().getLevelPayload().getTilemap();
            leftGameplayPanel.loadLevel(leftTilemap, true);
            leftLabel.setText("LEFT LEVEL (1/2) - Press SPACE to start");
            
            // Ensure left panel has focus (double-check)
            SwingUtilities.invokeLater(() -> {
                leftGameplayPanel.requestFocusInWindow();
            });
            
        } catch (Exception e) {
            clearBattleDisplay();
            throw new RuntimeException("Failed to display battle: " + e.getMessage(), e);
        }
    }
    
    /**
     * Reveal generator names after voting.
     */
    private void revealGenerators() {
        if (currentBattle == null) return;
        
        BattleResponse.Generator leftGen = currentBattle.getLeft().getGenerator();
        String leftGenId = leftGen.getGeneratorId();
        String leftGenIdShort = leftGenId.length() >= 8 ? leftGenId.substring(0, 8) : leftGenId;
        leftLabel.setText(String.format("LEFT: %s v%s (ID: %s)", 
            leftGen.getName(), 
            leftGen.getVersion(),
            leftGenIdShort));
        
        BattleResponse.Generator rightGen = currentBattle.getRight().getGenerator();
        String rightGenId = rightGen.getGeneratorId();
        String rightGenIdShort = rightGenId.length() >= 8 ? rightGenId.substring(0, 8) : rightGenId;
        rightLabel.setText(String.format("RIGHT: %s v%s (ID: %s)", 
            rightGen.getName(), 
            rightGen.getVersion(),
            rightGenIdShort));
    }
    
    /**
     * Clear battle display (Phase 2: No-op, panels reset on load).
     */
    private void clearBattleDisplay() {
        // Phase 2: GameplayPanel resets when loadLevel is called
        leftLabel.setText("LEFT LEVEL");
        rightLabel.setText("RIGHT LEVEL");
    }
    
    /**
     * Submit a vote.
     */
    private void vote(String result) {
        if (currentBattle == null) {
            return;
        }
        
        List<String> selectedLeftTags = getSelectedTags(leftTagCheckboxes);
        List<String> selectedRightTags = getSelectedTags(rightTagCheckboxes);
        pendingVote = new VoteRequest(config.getSessionId(), currentBattle.getBattleId(), result, selectedLeftTags, selectedRightTags);
        
        setState(State.SUBMITTING_VOTE);
        setStatus("Submitting vote...");
        
        new Thread(() -> {
            try {
                // Phase 2: Build telemetry
                Map<String, Object> telemetry = new HashMap<>();
                
                Map<String, Object> leftTelemetry = new HashMap<>();
                if (leftPlayResult != null) {
                    leftPlayResult.addToTelemetry(leftTelemetry);
                }
                telemetry.put("left", leftTelemetry);
                
                Map<String, Object> rightTelemetry = new HashMap<>();
                if (rightPlayResult != null) {
                    rightPlayResult.addToTelemetry(rightTelemetry);
                }
                telemetry.put("right", rightTelemetry);
                
                VoteResponse response = apiClient.submitVote(
                    pendingVote.sessionId,
                    pendingVote.battleId,
                    pendingVote.result,
                    pendingVote.leftTags,
                    pendingVote.rightTags,
                    telemetry  // Phase 2: Include telemetry
                );
                
                SwingUtilities.invokeLater(() -> {
                    // Reveal generator names after voting
                    revealGenerators();
                    
                    setStatus(String.format("Vote accepted! Vote ID: %s", response.getVoteId()));
                    setState(State.VOTED_SHOW_RESULT);
                    pendingVote = null;
                    
                    // Show rating changes if available
                    if (response.getLeaderboardPreview() != null) {
                        showRatingChanges(response.getLeaderboardPreview());
                    }
                    
                    // Fetch updated leaderboard
                    fetchLeaderboard();
                });
            } catch (ArenaApiException e) {
                SwingUtilities.invokeLater(() -> handleVoteError(e));
            }
        }).start();
    }
    
    /**
     * Retry a failed vote submission.
     */
    private void retryVote() {
        if (pendingVote == null) {
            return;
        }
        
        setState(State.SUBMITTING_VOTE);
        setStatus("Retrying vote...");
        retryButton.setVisible(false);
        
        new Thread(() -> {
            try {
                // Phase 2: Build telemetry
                Map<String, Object> telemetry = new HashMap<>();
                
                Map<String, Object> leftTelemetry = new HashMap<>();
                if (leftPlayResult != null) {
                    leftPlayResult.addToTelemetry(leftTelemetry);
                }
                telemetry.put("left", leftTelemetry);
                
                Map<String, Object> rightTelemetry = new HashMap<>();
                if (rightPlayResult != null) {
                    rightPlayResult.addToTelemetry(rightTelemetry);
                }
                telemetry.put("right", rightTelemetry);
                
                VoteResponse response = apiClient.submitVote(
                    pendingVote.sessionId,
                    pendingVote.battleId,
                    pendingVote.result,
                    pendingVote.leftTags,
                    pendingVote.rightTags,
                    telemetry  // Phase 2: Include telemetry
                );
                
                SwingUtilities.invokeLater(() -> {
                    revealGenerators();
                    setStatus(String.format("Vote accepted! Vote ID: %s", response.getVoteId()));
                    setState(State.VOTED_SHOW_RESULT);
                    pendingVote = null;
                    fetchLeaderboard();
                });
            } catch (ArenaApiException e) {
                SwingUtilities.invokeLater(() -> handleVoteError(e));
            }
        }).start();
    }
    
    /**
     * Fetch leaderboard.
     */
    private void fetchLeaderboard() {
        new Thread(() -> {
            try {
                LeaderboardResponse response = apiClient.leaderboard();
                SwingUtilities.invokeLater(() -> leaderboardPanel.updateLeaderboard(response));
            } catch (ArenaApiException e) {
                logger.warn("Failed to fetch leaderboard", e);
            }
        }).start();
    }
    
    /**
     * Handle API errors.
     */
    private void handleApiError(ArenaApiException e, String context) {
        logger.error("API error during {}: {}", context, e.getMessage());
        
        String errorCode = e.getErrorCode();
        
        if ("NO_BATTLE_AVAILABLE".equals(errorCode)) {
            setStatus("No battles available - Try again in a few seconds");
            setState(State.ERROR_RECOVERABLE);
            // Auto-enable next battle after a delay
            new Timer(3000, ev -> setState(State.READY_NO_BATTLE)).start();
        } else {
            setStatus("Error: " + e.getMessage());
            setState(State.ERROR_RECOVERABLE);
        }
    }
    
    /**
     * Handle vote submission errors.
     */
    private void handleVoteError(ArenaApiException e) {
        logger.error("Vote submission error: {}", e.getMessage());
        
        String errorCode = e.getErrorCode();
        
        if ("BATTLE_NOT_FOUND".equals(errorCode) || "BATTLE_ALREADY_VOTED".equals(errorCode)) {
            setStatus("Error: " + e.getMessage() + " - Fetch next battle");
            setState(State.READY_NO_BATTLE);
            pendingVote = null;
        } else if ("DUPLICATE_VOTE_CONFLICT".equals(errorCode)) {
            setStatus("Vote already recorded - Fetch next battle");
            setState(State.READY_NO_BATTLE);
            pendingVote = null;
        } else if ("INVALID_TAG".equals(errorCode)) {
            setStatus("Invalid tags - Please reselect and try again");
            clearTags();
            setState(State.BATTLE_LOADED_PENDING_VOTE);
            pendingVote = null;
        } else if (e.isRetryable()) {
            setStatus("Network error - Click Retry or fetch next battle");
            setState(State.ERROR_RECOVERABLE);
            retryButton.setVisible(true);
        } else {
            setStatus("Error: " + e.getMessage());
            setState(State.READY_NO_BATTLE);
            pendingVote = null;
        }
    }
    
    /**
     * Show fatal error and exit.
     */
    private void showFatalError(String title, String message) {
        setState(State.ERROR_FATAL);
        JOptionPane.showMessageDialog(this, message, title, JOptionPane.ERROR_MESSAGE);
        System.exit(1);
    }
    
    /**
     * Show leaderboard preview from vote response.
     */
    private void showRatingChanges(VoteResponse.LeaderboardPreview preview) {
        if (preview.getGenerators() == null || preview.getGenerators().isEmpty()) {
            logger.info("Vote accepted. Leaderboard updated at: {}", preview.getUpdatedAtUtc());
            return;
        }
        
        StringBuilder message = new StringBuilder("Top Generators:\n\n");
        int count = Math.min(5, preview.getGenerators().size());
        for (int i = 0; i < count; i++) {
            VoteResponse.LeaderboardGeneratorPreview gen = preview.getGenerators().get(i);
            message.append(String.format("%d. %s - Rating: %.1f (Games: %d)\n", 
                i + 1, gen.getName(), gen.getRating(), gen.getGamesPlayed()));
        }
        
        logger.info("Vote accepted. {}", message.toString().replace("\n", " "));
    }
    
    /**
     * Update UI based on current state.
     */
    private void updateUIState() {
        // Phase 2: Can vote when both levels are finished
        boolean canVote = currentState == State.BOTH_FINISHED_READY_TO_VOTE || 
                          currentState == State.BATTLE_LOADED_PENDING_VOTE; // Phase 1 compatibility
        boolean canFetchBattle = currentState == State.READY_NO_BATTLE || currentState == State.VOTED_SHOW_RESULT;
        
        leftButton.setEnabled(canVote);
        rightButton.setEnabled(canVote);
        tieButton.setEnabled(canVote);
        skipButton.setEnabled(true); // Skip always available
        nextBattleButton.setEnabled(canFetchBattle);
        
        for (JCheckBox cb : leftTagCheckboxes.values()) {
            cb.setEnabled(canVote);
        }
        for (JCheckBox cb : rightTagCheckboxes.values()) {
            cb.setEnabled(canVote);
        }
    }
    
    /**
     * Set current state and update UI.
     */
    private void setState(State newState) {
        currentState = newState;
        updateUIState();
    }
    
    /**
     * Set status message.
     */
    private void setStatus(String message) {
        statusLabel.setText("Status: " + message);
    }
    
    /**
     * Get selected tags.
     */
    private List<String> getSelectedTags(Map<String, JCheckBox> checkboxes) {
        List<String> selected = new ArrayList<>();
        for (Map.Entry<String, JCheckBox> entry : checkboxes.entrySet()) {
            if (entry.getValue().isSelected()) {
                selected.add(entry.getKey());
            }
        }
        return selected;
    }
    
    /**
     * Clear tag selection.
     */
    private void clearTags() {
        for (JCheckBox cb : leftTagCheckboxes.values()) {
            cb.setSelected(false);
        }
        for (JCheckBox cb : rightTagCheckboxes.values()) {
            cb.setSelected(false);
        }
    }
    
    /**
     * Enforce max tag count for a specific checkbox map.
     */
    private void enforceMaxTags(Map<String, JCheckBox> checkboxes) {
        List<String> selected = getSelectedTags(checkboxes);
        if (selected.size() > MAX_TAGS) {
            // Find the checkbox that was just selected and deselect it
            for (Map.Entry<String, JCheckBox> entry : checkboxes.entrySet()) {
                if (entry.getValue().isSelected() && !selected.subList(0, MAX_TAGS).contains(entry.getKey())) {
                    entry.getValue().setSelected(false);
                    break;
                }
            }
            JOptionPane.showMessageDialog(this, 
                "Maximum " + MAX_TAGS + " tags allowed per level", 
                "Too Many Tags", 
                JOptionPane.WARNING_MESSAGE);
        }
    }
}
