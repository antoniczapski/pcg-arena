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
    
    private TilemapView topView;
    private TilemapView bottomView;
    private JLabel topLabel;
    private JLabel bottomLabel;
    
    private LeaderboardPanel leaderboardPanel;
    
    private JButton topButton;
    private JButton bottomButton;
    private JButton tieButton;
    private JButton skipButton;
    private JButton nextBattleButton;
    private JButton retryButton;
    
    private Map<String, JCheckBox> topTagCheckboxes;
    private Map<String, JCheckBox> bottomTagCheckboxes;
    
    // State
    private BattleResponse.Battle currentBattle;
    private VoteRequest pendingVote;
    
    // Inner class to hold retry info
    private static class VoteRequest {
        String sessionId;
        String battleId;
        String result;
        List<String> topTags;
        List<String> bottomTags;
        
        VoteRequest(String sessionId, String battleId, String result, List<String> topTags, List<String> bottomTags) {
            this.sessionId = sessionId;
            this.battleId = battleId;
            this.result = result;
            this.topTags = new ArrayList<>(topTags);
            this.bottomTags = new ArrayList<>(bottomTags);
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
        
        // Center: Main content with proper ordering (level, tags, level, tags, buttons)
        JPanel centerPanel = new JPanel();
        centerPanel.setLayout(new BoxLayout(centerPanel, BoxLayout.Y_AXIS));
        
        // === TOP LEVEL ===
        JPanel topLevelPanel = new JPanel(new BorderLayout());
        topLabel = new JLabel("TOP LEVEL", SwingConstants.CENTER);
        topLabel.setFont(new Font("SansSerif", Font.BOLD, 12));
        topView = new TilemapView();
        JScrollPane topScroll = new JScrollPane(topView, 
            JScrollPane.VERTICAL_SCROLLBAR_NEVER,
            JScrollPane.HORIZONTAL_SCROLLBAR_AS_NEEDED);
        topScroll.setPreferredSize(new Dimension(800, 80));
        topLevelPanel.add(topLabel, BorderLayout.NORTH);
        topLevelPanel.add(topScroll, BorderLayout.CENTER);
        centerPanel.add(topLevelPanel);
        
        // === TOP LEVEL TAGS ===
        JPanel topTagPanel = new JPanel(new FlowLayout(FlowLayout.LEFT));
        topTagPanel.add(new JLabel("Top level tags (max 3):"));
        topTagCheckboxes = new HashMap<>();
        for (String tag : ALLOWED_TAGS) {
            JCheckBox cb = new JCheckBox(tag);
            cb.addActionListener(e -> enforceMaxTags(topTagCheckboxes));
            topTagCheckboxes.put(tag, cb);
            topTagPanel.add(cb);
        }
        centerPanel.add(topTagPanel);
        
        // Add spacing
        centerPanel.add(Box.createRigidArea(new Dimension(0, 10)));
        
        // === BOTTOM LEVEL ===
        JPanel bottomLevelPanel = new JPanel(new BorderLayout());
        bottomLabel = new JLabel("BOTTOM LEVEL", SwingConstants.CENTER);
        bottomLabel.setFont(new Font("SansSerif", Font.BOLD, 12));
        bottomView = new TilemapView();
        JScrollPane bottomScroll = new JScrollPane(bottomView,
            JScrollPane.VERTICAL_SCROLLBAR_NEVER,
            JScrollPane.HORIZONTAL_SCROLLBAR_AS_NEEDED);
        bottomScroll.setPreferredSize(new Dimension(800, 80));
        bottomLevelPanel.add(bottomLabel, BorderLayout.NORTH);
        bottomLevelPanel.add(bottomScroll, BorderLayout.CENTER);
        centerPanel.add(bottomLevelPanel);
        
        // === BOTTOM LEVEL TAGS ===
        JPanel bottomTagPanel = new JPanel(new FlowLayout(FlowLayout.LEFT));
        bottomTagPanel.add(new JLabel("Bottom level tags (max 3):"));
        bottomTagCheckboxes = new HashMap<>();
        for (String tag : ALLOWED_TAGS) {
            JCheckBox cb = new JCheckBox(tag);
            cb.addActionListener(e -> enforceMaxTags(bottomTagCheckboxes));
            bottomTagCheckboxes.put(tag, cb);
            bottomTagPanel.add(cb);
        }
        centerPanel.add(bottomTagPanel);
        
        // Add spacing
        centerPanel.add(Box.createRigidArea(new Dimension(0, 10)));
        
        // === VOTE BUTTONS ===
        JPanel voteButtonsPanel = new JPanel(new FlowLayout());
        topButton = new JButton("Top Better");
        bottomButton = new JButton("Bottom Better");
        tieButton = new JButton("Tie");
        skipButton = new JButton("Skip");
        topButton.addActionListener(e -> vote("TOP"));
        bottomButton.addActionListener(e -> vote("BOTTOM"));
        tieButton.addActionListener(e -> vote("TIE"));
        skipButton.addActionListener(e -> vote("SKIP"));
        voteButtonsPanel.add(topButton);
        voteButtonsPanel.add(bottomButton);
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
                    setStatus("Battle loaded - Vote now");
                    setState(State.BATTLE_LOADED_PENDING_VOTE);
                });
            } catch (ArenaApiException e) {
                SwingUtilities.invokeLater(() -> handleApiError(e, "fetch battle"));
            }
        }).start();
    }
    
    /**
     * Display a battle.
     */
    private void displayBattle(BattleResponse.Battle battle) {
        try {
            // Parse and display top level
            String topTilemap = battle.getTop().getLevelPayload().getTilemap();
            char[][] topGrid = TilemapParser.parse(topTilemap);
            topView.setTilemap(topGrid);
            topLabel.setText("TOP LEVEL");
            
            // Parse and display bottom level
            String bottomTilemap = battle.getBottom().getLevelPayload().getTilemap();
            char[][] bottomGrid = TilemapParser.parse(bottomTilemap);
            bottomView.setTilemap(bottomGrid);
            bottomLabel.setText("BOTTOM LEVEL");
            
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
        
        BattleResponse.Generator topGen = currentBattle.getTop().getGenerator();
        String topGenId = topGen.getGeneratorId();
        String topGenIdShort = topGenId.length() >= 8 ? topGenId.substring(0, 8) : topGenId;
        topLabel.setText(String.format("TOP: %s v%s (ID: %s)", 
            topGen.getName(), 
            topGen.getVersion(),
            topGenIdShort));
        
        BattleResponse.Generator bottomGen = currentBattle.getBottom().getGenerator();
        String bottomGenId = bottomGen.getGeneratorId();
        String bottomGenIdShort = bottomGenId.length() >= 8 ? bottomGenId.substring(0, 8) : bottomGenId;
        bottomLabel.setText(String.format("BOTTOM: %s v%s (ID: %s)", 
            bottomGen.getName(), 
            bottomGen.getVersion(),
            bottomGenIdShort));
    }
    
    /**
     * Clear battle display.
     */
    private void clearBattleDisplay() {
        topView.clear();
        bottomView.clear();
        topLabel.setText("TOP LEVEL");
        bottomLabel.setText("BOTTOM LEVEL");
    }
    
    /**
     * Submit a vote.
     */
    private void vote(String result) {
        if (currentBattle == null) {
            return;
        }
        
        List<String> selectedTopTags = getSelectedTags(topTagCheckboxes);
        List<String> selectedBottomTags = getSelectedTags(bottomTagCheckboxes);
        pendingVote = new VoteRequest(config.getSessionId(), currentBattle.getBattleId(), result, selectedTopTags, selectedBottomTags);
        
        setState(State.SUBMITTING_VOTE);
        setStatus("Submitting vote...");
        
        new Thread(() -> {
            try {
                VoteResponse response = apiClient.submitVote(
                    pendingVote.sessionId,
                    pendingVote.battleId,
                    pendingVote.result,
                    pendingVote.topTags,
                    pendingVote.bottomTags,
                    new HashMap<>() // Empty telemetry for Phase 1
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
                VoteResponse response = apiClient.submitVote(
                    pendingVote.sessionId,
                    pendingVote.battleId,
                    pendingVote.result,
                    pendingVote.topTags,
                    pendingVote.bottomTags,
                    new HashMap<>()
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
        boolean canVote = currentState == State.BATTLE_LOADED_PENDING_VOTE;
        boolean canFetchBattle = currentState == State.READY_NO_BATTLE || currentState == State.VOTED_SHOW_RESULT;
        
        topButton.setEnabled(canVote);
        bottomButton.setEnabled(canVote);
        tieButton.setEnabled(canVote);
        skipButton.setEnabled(canVote);
        nextBattleButton.setEnabled(canFetchBattle);
        
        for (JCheckBox cb : topTagCheckboxes.values()) {
            cb.setEnabled(canVote);
        }
        for (JCheckBox cb : bottomTagCheckboxes.values()) {
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
        for (JCheckBox cb : topTagCheckboxes.values()) {
            cb.setSelected(false);
        }
        for (JCheckBox cb : bottomTagCheckboxes.values()) {
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
