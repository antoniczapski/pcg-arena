package arena;

import arena.api.ArenaApiClient;
import arena.config.ClientConfig;
import arena.ui.MainWindow;
import arena.util.LoggerUtil;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import javax.swing.*;

/**
 * Main entry point for the PCG Arena Java client.
 */
public class App {
    private static final Logger logger = LoggerFactory.getLogger(App.class);
    
    public static void main(String[] args) {
        // Ensure log directory exists
        LoggerUtil.ensureLogDirectory();
        
        logger.info("=== PCG Arena Client Starting ===");
        logger.info("Version: {}", ClientConfig.CLIENT_VERSION);
        logger.info("Protocol: {}", ClientConfig.PROTOCOL_VERSION);
        
        try {
            // Load configuration
            ClientConfig config = ClientConfig.load(args);
            
            // Create API client
            ArenaApiClient apiClient = new ArenaApiClient(config.getBaseUrl());
            
            // Create and show main window
            SwingUtilities.invokeLater(() -> {
                try {
                    // Set system look and feel
                    UIManager.setLookAndFeel(UIManager.getSystemLookAndFeelClassName());
                } catch (Exception e) {
                    logger.warn("Could not set system look and feel", e);
                }
                
                MainWindow window = new MainWindow(config, apiClient);
                window.setVisible(true);
                
                // Perform health check and initialization
                window.start();
            });
            
        } catch (Exception e) {
            logger.error("Fatal error during startup", e);
            System.err.println("Fatal error: " + e.getMessage());
            e.printStackTrace();
            System.exit(1);
        }
    }
}

