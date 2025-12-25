package arena.api;

import arena.api.models.*;
import arena.config.ClientConfig;
import arena.util.JsonUtil;
import arena.util.LoggerUtil;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.net.URI;
import java.net.URL;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.time.Duration;
import java.util.List;
import java.util.Map;

/**
 * HTTP client for the Arena API.
 * Handles all communication with the backend.
 */
public class ArenaApiClient {
    private static final Logger logger = LoggerFactory.getLogger(ArenaApiClient.class);
    
    private final String baseUrl;
    private final HttpClient httpClient;
    
    public ArenaApiClient(String baseUrl) {
        this.baseUrl = baseUrl;
        // Force HTTP/1.1 - HTTP/2 causes "Unsupported upgrade request" with Uvicorn
        this.httpClient = HttpClient.newBuilder()
            .version(HttpClient.Version.HTTP_1_1)
            .connectTimeout(Duration.ofSeconds(5))
            .build();
    }
    
    /**
     * Health check - verifies backend is reachable and protocol matches.
     */
    public HealthResponse health() throws ArenaApiException {
        try {
            LoggerUtil.logRequest("GET", "/health");
            
            HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create(baseUrl + "/health"))
                .GET()
                .timeout(Duration.ofSeconds(5))
                .build();
            
            HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());
            LoggerUtil.logResponse("GET", "/health", response.statusCode());
            
            if (response.statusCode() != 200) {
                throw new ArenaApiException("Health check failed with status " + response.statusCode());
            }
            
            HealthResponse healthResponse = JsonUtil.fromJson(response.body(), HealthResponse.class);
            verifyProtocol(healthResponse.getProtocolVersion());
            
            return healthResponse;
        } catch (ArenaApiException e) {
            throw e;
        } catch (Exception e) {
            logger.error("Health check failed", e);
            throw new ArenaApiException("Backend unreachable: " + e.getMessage(), e);
        }
    }
    
    /**
     * Request next battle.
     */
    public BattleResponse nextBattle(String sessionId) throws ArenaApiException {
        BattleRequest request = new BattleRequest(ClientConfig.CLIENT_VERSION, sessionId);
        // Use the literal colon - the backend handles both :next and %3Anext
        String path = "/v1/battles:next";
        
        try {
            LoggerUtil.logRequest("POST", path);
            String responseBody = sendJson("POST", path, JsonUtil.toJson(request));
            
            // Check if it's an error response
            if (responseBody.contains("\"error\"")) {
                ErrorResponse errorResponse = JsonUtil.fromJson(responseBody, ErrorResponse.class);
                verifyProtocol(errorResponse.getProtocolVersion());
                throw createException(errorResponse);
            }
            
            BattleResponse battleResponse = JsonUtil.fromJson(responseBody, BattleResponse.class);
            verifyProtocol(battleResponse.getProtocolVersion());
            
            LoggerUtil.logBattle(battleResponse.getBattle().getBattleId());
            return battleResponse;
        } catch (ArenaApiException e) {
            throw e;
        } catch (Exception e) {
            logger.error("Failed to fetch battle", e);
            throw new ArenaApiException("Failed to fetch battle: " + e.getMessage(), e);
        }
    }
    
    /**
     * Submit a vote.
     */
    public VoteResponse submitVote(String sessionId, String battleId, String result, 
                                   List<String> tags, Map<String, Object> telemetry) 
            throws ArenaApiException {
        VoteRequest request = new VoteRequest(
            ClientConfig.CLIENT_VERSION, 
            sessionId, 
            battleId, 
            result, 
            tags, 
            telemetry
        );
        String path = "/v1/votes";
        
        try {
            LoggerUtil.logRequest("POST", path);
            String responseBody = sendJson("POST", path, JsonUtil.toJson(request));
            
            // Check if it's an error response
            if (responseBody.contains("\"error\"")) {
                ErrorResponse errorResponse = JsonUtil.fromJson(responseBody, ErrorResponse.class);
                verifyProtocol(errorResponse.getProtocolVersion());
                throw createException(errorResponse);
            }
            
            VoteResponse voteResponse = JsonUtil.fromJson(responseBody, VoteResponse.class);
            verifyProtocol(voteResponse.getProtocolVersion());
            
            LoggerUtil.logVote(battleId, result, voteResponse.getVoteId());
            return voteResponse;
        } catch (ArenaApiException e) {
            throw e;
        } catch (Exception e) {
            logger.error("Failed to submit vote", e);
            throw new ArenaApiException("Failed to submit vote: " + e.getMessage(), e);
        }
    }
    
    /**
     * Fetch leaderboard.
     */
    public LeaderboardResponse leaderboard() throws ArenaApiException {
        String path = "/v1/leaderboard";
        
        try {
            LoggerUtil.logRequest("GET", path);
            
            HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create(baseUrl + path))
                .GET()
                .timeout(Duration.ofSeconds(5))
                .build();
            
            HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());
            LoggerUtil.logResponse("GET", path, response.statusCode());
            
            if (response.statusCode() != 200) {
                throw new ArenaApiException("Leaderboard request failed with status " + response.statusCode());
            }
            
            LeaderboardResponse leaderboardResponse = JsonUtil.fromJson(response.body(), LeaderboardResponse.class);
            verifyProtocol(leaderboardResponse.getProtocolVersion());
            
            return leaderboardResponse;
        } catch (ArenaApiException e) {
            throw e;
        } catch (Exception e) {
            logger.error("Failed to fetch leaderboard", e);
            throw new ArenaApiException("Failed to fetch leaderboard: " + e.getMessage(), e);
        }
    }
    
    /**
     * Send a JSON request and return the response body.
     */
    private String sendJson(String method, String path, String jsonBody) throws Exception {
        String fullUrl = baseUrl + path;
        logger.debug("Sending {} request to: {}", method, fullUrl);
        logger.debug("Request body: {}", jsonBody);
        
        // Build URI using URL first to properly handle special characters like colons
        URL url = new URL(fullUrl);
        URI uri = new URI(url.getProtocol(), null, url.getHost(), url.getPort(), url.getPath(), url.getQuery(), null);
        
        HttpRequest.Builder builder = HttpRequest.newBuilder()
            .uri(uri)
            .header("Content-Type", "application/json; charset=utf-8")
            .header("Accept", "application/json")
            .timeout(Duration.ofSeconds(5));
        
        if ("POST".equals(method)) {
            builder.POST(HttpRequest.BodyPublishers.ofString(jsonBody, java.nio.charset.StandardCharsets.UTF_8));
        } else {
            builder.GET();
        }
        
        HttpRequest request = builder.build();
        HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());
        
        LoggerUtil.logResponse(method, path, response.statusCode());
        logger.debug("Response body length: {}", response.body() != null ? response.body().length() : 0);
        
        if (response.statusCode() < 200 || response.statusCode() >= 300) {
            // Try to parse as error response
            if (response.body() != null && !response.body().isEmpty()) {
                return response.body();
            }
            throw new ArenaApiException("HTTP " + response.statusCode());
        }
        
        return response.body();
    }
    
    /**
     * Verify protocol version matches expected.
     */
    private void verifyProtocol(String protocolVersion) throws ArenaApiException {
        if (!ClientConfig.PROTOCOL_VERSION.equals(protocolVersion)) {
            throw new ArenaApiException(
                "PROTOCOL_MISMATCH",
                String.format("Incompatible backend protocol: expected %s, got %s", 
                    ClientConfig.PROTOCOL_VERSION, protocolVersion),
                false
            );
        }
    }
    
    /**
     * Create exception from error response.
     */
    private ArenaApiException createException(ErrorResponse errorResponse) {
        ErrorResponse.ErrorInfo error = errorResponse.getError();
        LoggerUtil.logError("API", "request", error.getCode(), error.getMessage());
        return new ArenaApiException(error.getCode(), error.getMessage(), error.isRetryable());
    }
}

