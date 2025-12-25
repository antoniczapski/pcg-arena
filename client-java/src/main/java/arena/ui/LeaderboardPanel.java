package arena.ui;

import arena.api.models.LeaderboardResponse;

import javax.swing.*;
import javax.swing.table.DefaultTableModel;
import java.awt.*;
import java.util.List;

/**
 * Panel displaying the leaderboard.
 */
public class LeaderboardPanel extends JPanel {
    private final DefaultTableModel tableModel;
    private final JTable table;
    private final JLabel ratingSystemLabel;
    
    public LeaderboardPanel() {
        setLayout(new BorderLayout());
        
        // Title
        JLabel titleLabel = new JLabel("Leaderboard (Top 10)", SwingConstants.CENTER);
        titleLabel.setFont(new Font("SansSerif", Font.BOLD, 14));
        add(titleLabel, BorderLayout.NORTH);
        
        // Table
        String[] columnNames = {"Rank", "Name", "Rating", "W", "L", "T", "Battles"};
        tableModel = new DefaultTableModel(columnNames, 0) {
            @Override
            public boolean isCellEditable(int row, int column) {
                return false;
            }
        };
        table = new JTable(tableModel);
        table.setFont(new Font("Monospaced", Font.PLAIN, 11));
        table.getTableHeader().setFont(new Font("SansSerif", Font.BOLD, 11));
        
        JScrollPane scrollPane = new JScrollPane(table);
        scrollPane.setPreferredSize(new Dimension(600, 200));
        add(scrollPane, BorderLayout.CENTER);
        
        // Rating system info
        ratingSystemLabel = new JLabel("Rating system: -", SwingConstants.CENTER);
        ratingSystemLabel.setFont(new Font("SansSerif", Font.PLAIN, 10));
        add(ratingSystemLabel, BorderLayout.SOUTH);
    }
    
    /**
     * Update leaderboard display.
     */
    public void updateLeaderboard(LeaderboardResponse response) {
        // Clear existing rows
        tableModel.setRowCount(0);
        
        // Add top 10 rankings
        List<LeaderboardResponse.GeneratorRanking> generators = response.getGenerators();
        int limit = Math.min(10, generators.size());
        
        for (int i = 0; i < limit; i++) {
            LeaderboardResponse.GeneratorRanking generator = generators.get(i);
            Object[] row = {
                generator.getRank(),
                generator.getName(),
                String.format("%.1f", generator.getRating()),
                generator.getWins(),
                generator.getLosses(),
                generator.getTies(),
                generator.getGamesPlayed()
            };
            tableModel.addRow(row);
        }
        
        // Update rating system label
        LeaderboardResponse.RatingSystem ratingSystem = response.getRatingSystem();
        if (ratingSystem != null) {
            ratingSystemLabel.setText(String.format(
                "Rating: %s | Initial: %.0f | K-factor: %d",
                ratingSystem.getName(),
                ratingSystem.getInitialRating(),
                ratingSystem.getKFactor()
            ));
        }
    }
    
    /**
     * Clear leaderboard.
     */
    public void clear() {
        tableModel.setRowCount(0);
        ratingSystemLabel.setText("Rating system: -");
    }
}

