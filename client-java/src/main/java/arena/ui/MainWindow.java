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
    
    // Allowed tags from spec
    private static final String[] ALLOWED_TAGS = {
        "too_easy", "too_hard", "boring", "unfair", 
        "interesting", "creative", "broken", "unplayable"
    };
    private static final int MAX_TAGS = 3;
    
    // UI state
    private enum State {
        STARTING,
        READY_NO_BATTLE,
        BATTLE_LOADED_PENDING_VOTE,
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
    
    private BattlePanel battlePanel;
    private LeaderboardPanel leaderboardPanel;
    
    private JButton leftButton;
    private JButton rightButton;
    private JButton tieButton;
    private JButton skipButton;
    private JButton nextBattleButton;
    private JButton retryButton;
    
    private Map<String, JCheckBox> tagCheckboxes;
    
    // State
    private BattleResponse.Battle currentBattle;
    private VoteRequest pendingVote;
    
    // Inner class to hold retry info
    private static class VoteRequest {
        String sessionId;
        String battleId;
        String result;
        List<String> tags;
        
        VoteRequest(String sessionId, String battleId, String result, List<String> tags) {
            this.sessionId = sessionId;
            this.battleId = battleId;
            this.result = result;
            this.tags = new ArrayList<>(tags);
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
        
        // Center: Battle display
        battlePanel = new BattlePanel();
        add(battlePanel, BorderLayout.CENTER);
        
        // Bottom: Controls and leaderboard
        JPanel bottomPanel = new JPanel(new BorderLayout());
        
        // Voting controls
        JPanel controlsPanel = new JPanel(new GridLayout(4, 1, 5, 5));
        
        // Vote buttons
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
        controlsPanel.add(voteButtonsPanel);
        
        // Tag selection
        JPanel tagPanel = new JPanel(new FlowLayout(FlowLayout.LEFT));
        tagPanel.add(new JLabel("Tags (max 3):"));
        tagCheckboxes = new HashMap<>();
        for (String tag : ALLOWED_TAGS) {
            JCheckBox cb = new JCheckBox(tag);
            cb.addActionListener(e -> enforceMaxTags());
            tagCheckboxes.put(tag, cb);
            tagPanel.add(cb);
        }
        controlsPanel.add(tagPanel);
        
        // Action buttons
        JPanel actionPanel = new JPanel(new FlowLayout());
        nextBattleButton = new JButton("Next Battle");
        nextBattleButton.addActionListener(e -> fetchBattle());
        retryButton = new JButton("Retry Submit");
        retryButton.addActionListener(e -> retryVote());
        retryButton.setVisible(false);
        actionPanel.add(nextBattleButton);
        actionPanel.add(retryButton);
        controlsPanel.add(actionPanel);
        
        bottomPanel.add(controlsPanel, BorderLayout.NORTH);
        
        // Leaderboard
        leaderboardPanel = new LeaderboardPanel();
        bottomPanel.add(leaderboardPanel, BorderLayout.CENTER);
        
        add(bottomPanel, BorderLayout.SOUTH);
        
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
                setStatus("Backend OK - Ready");
                setState(State.READY_NO_BATTLE);
                
                // Auto-fetch first leaderboard
                fetchLeaderboard();
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
                    battlePanel.displayBattle(currentBattle);
                    clearTags();
                    setStatus("Battle loaded - Vote now");
                    setState(State.BATTLE_LOADED_PENDING_VOTE);
                });
            } catch (ArenaApiException e) {
                SwingUtilities.invokeLater(() -> handleApiError(e, "fetch battle"));
            }
        }).start();
    }
    
    /**
     * Submit a vote.
     */
    private void vote(String result) {
        if (currentBattle == null) {
            return;
        }
        
        List<String> selectedTags = getSelectedTags();
        pendingVote = new VoteRequest(config.getSessionId(), currentBattle.getBattleId(), result, selectedTags);
        
        setState(State.SUBMITTING_VOTE);
        setStatus("Submitting vote...");
        
        new Thread(() -> {
            try {
                VoteResponse response = apiClient.submitVote(
                    pendingVote.sessionId,
                    pendingVote.battleId,
                    pendingVote.result,
                    pendingVote.tags,
                    new HashMap<>() // Empty telemetry for Phase 1
                );
                
                SwingUtilities.invokeLater(() -> {
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
                VoteResponse response = apiClient.submitVote(
                    pendingVote.sessionId,
                    pendingVote.battleId,
                    pendingVote.result,
                    pendingVote.tags,
                    new HashMap<>()
                );
                
                SwingUtilities.invokeLater(() -> {
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
        boolean canVote = currentState == State.BATTLE_LOADED_PENDING_VOTE;
        boolean canFetchBattle = currentState == State.READY_NO_BATTLE || currentState == State.VOTED_SHOW_RESULT;
        
        leftButton.setEnabled(canVote);
        rightButton.setEnabled(canVote);
        tieButton.setEnabled(canVote);
        skipButton.setEnabled(canVote);
        nextBattleButton.setEnabled(canFetchBattle);
        
        for (JCheckBox cb : tagCheckboxes.values()) {
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
    private List<String> getSelectedTags() {
        List<String> selected = new ArrayList<>();
        for (Map.Entry<String, JCheckBox> entry : tagCheckboxes.entrySet()) {
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
        for (JCheckBox cb : tagCheckboxes.values()) {
            cb.setSelected(false);
        }
    }
    
    /**
     * Enforce max tag count.
     */
    private void enforceMaxTags() {
        List<String> selected = getSelectedTags();
        if (selected.size() > MAX_TAGS) {
            // Find the checkbox that was just selected and deselect it
            for (Map.Entry<String, JCheckBox> entry : tagCheckboxes.entrySet()) {
                if (entry.getValue().isSelected() && !selected.subList(0, MAX_TAGS).contains(entry.getKey())) {
                    entry.getValue().setSelected(false);
                    break;
                }
            }
            JOptionPane.showMessageDialog(this, 
                "Maximum " + MAX_TAGS + " tags allowed", 
                "Too Many Tags", 
                JOptionPane.WARNING_MESSAGE);
        }
    }
}

