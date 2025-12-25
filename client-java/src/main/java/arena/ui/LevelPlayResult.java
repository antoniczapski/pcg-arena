package arena.ui;

import arena.game.core.MarioResult;
import arena.game.helper.GameStatus;

import java.util.Map;

/**
 * DTO to hold telemetry from one level playthrough.
 * Converts MarioResult into a flat structure suitable for JSON serialization.
 */
public class LevelPlayResult {
    public boolean played;
    public boolean completed;
    public String gameStatus;
    public int durationTicks;
    public float durationSeconds;
    public float completionPercentage;
    public int deaths;
    public int lives;
    public int coins;
    public int remainingTime;
    public int marioFinalMode;
    public int killsTotal;
    public int killsStomp;
    public int killsFire;
    public int killsShell;
    public int killsFall;
    public int numJumps;
    public float maxXJump;
    public int maxAirTime;
    public int numCollectedMushrooms;
    public int numCollectedFireflower;
    public int numCollectedCoins;
    public int numDestroyedBricks;
    public int numHurt;

    /**
     * Create LevelPlayResult from MarioResult
     */
    public static LevelPlayResult fromMarioResult(MarioResult result) {
        LevelPlayResult r = new LevelPlayResult();
        r.played = true;
        r.completed = result.getGameStatus() == GameStatus.WIN;
        r.gameStatus = result.getGameStatus().toString();
        r.durationTicks = result.getWorld().currentTick;
        r.durationSeconds = r.durationTicks / 24f;
        r.completionPercentage = result.getCompletionPercentage();
        r.deaths = result.getGameStatus() == GameStatus.LOSE ? 1 : 0;
        r.lives = result.getCurrentLives();
        r.coins = result.getCurrentCoins();
        r.remainingTime = result.getRemainingTime() / 1000;
        r.marioFinalMode = result.getMarioMode();
        r.killsTotal = result.getKillsTotal();
        r.killsStomp = result.getKillsByStomp();
        r.killsFire = result.getKillsByFire();
        r.killsShell = result.getKillsByShell();
        r.killsFall = result.getKillsByFall();
        r.numJumps = result.getNumJumps();
        r.maxXJump = result.getMaxXJump();
        r.maxAirTime = result.getMaxJumpAirTime();
        r.numCollectedMushrooms = result.getNumCollectedMushrooms();
        r.numCollectedFireflower = result.getNumCollectedFireflower();
        r.numCollectedCoins = result.getNumCollectedTileCoins();
        r.numDestroyedBricks = result.getNumDestroyedBricks();
        r.numHurt = result.getMarioNumHurts();
        return r;
    }

    /**
     * Add telemetry to a map (for JSON serialization)
     */
    public void addToTelemetry(Map<String, Object> map) {
        map.put("played", played);
        map.put("completed", completed);
        map.put("game_status", gameStatus);
        map.put("duration_ticks", durationTicks);
        map.put("duration_seconds", durationSeconds);
        map.put("completion_percentage", completionPercentage);
        map.put("deaths", deaths);
        map.put("lives", lives);
        map.put("coins", coins);
        map.put("remaining_time", remainingTime);
        map.put("mario_final_mode", marioFinalMode);
        map.put("kills_total", killsTotal);
        map.put("kills_stomp", killsStomp);
        map.put("kills_fire", killsFire);
        map.put("kills_shell", killsShell);
        map.put("kills_fall", killsFall);
        map.put("num_jumps", numJumps);
        map.put("max_x_jump", maxXJump);
        map.put("max_air_time", maxAirTime);
        map.put("num_collected_mushrooms", numCollectedMushrooms);
        map.put("num_collected_fireflower", numCollectedFireflower);
        map.put("num_collected_coins", numCollectedCoins);
        map.put("num_destroyed_bricks", numDestroyedBricks);
        map.put("num_hurt", numHurt);
    }
}

