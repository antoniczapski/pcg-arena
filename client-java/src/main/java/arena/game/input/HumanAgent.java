package arena.game.input;

import arena.game.core.MarioAgent;
import arena.game.core.MarioForwardModel;
import arena.game.core.MarioTimer;
import arena.game.helper.MarioActions;

import java.awt.event.KeyAdapter;
import java.awt.event.KeyEvent;

public class HumanAgent extends KeyAdapter implements MarioAgent {
    private boolean[] actions;

    @Override
    public void initialize(MarioForwardModel model, MarioTimer timer) {
        actions = new boolean[MarioActions.numberOfActions()];
    }

    @Override
    public boolean[] getActions(MarioForwardModel model, MarioTimer timer) {
        return actions;
    }

    @Override
    public String getAgentName() {
        return "HumanPlayer";
    }

    @Override
    public void keyPressed(KeyEvent e) {
        toggleKey(e.getKeyCode(), true);
    }

    @Override
    public void keyReleased(KeyEvent e) {
        toggleKey(e.getKeyCode(), false);
    }

    private void toggleKey(int keyCode, boolean isPressed) {
        if (actions == null) return;
        switch (keyCode) {
            case KeyEvent.VK_LEFT:
                actions[MarioActions.LEFT.getValue()] = isPressed;
                break;
            case KeyEvent.VK_RIGHT:
                actions[MarioActions.RIGHT.getValue()] = isPressed;
                break;
            case KeyEvent.VK_DOWN:
                actions[MarioActions.DOWN.getValue()] = isPressed;
                break;
            case KeyEvent.VK_S:
                actions[MarioActions.JUMP.getValue()] = isPressed;
                break;
            case KeyEvent.VK_A:
                actions[MarioActions.SPEED.getValue()] = isPressed;
                break;
        }
    }
}

