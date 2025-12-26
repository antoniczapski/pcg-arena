import { useState } from 'react';

export interface VoteData {
  result: 'LEFT' | 'RIGHT' | 'TIE' | 'SKIP';
  leftTags: string[];
  rightTags: string[];
}

interface VotingPanelProps {
  onVote: (vote: VoteData) => void;
}

export function VotingPanel({ onVote }: VotingPanelProps) {
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleVote = (result: VoteData['result']) => {
    if (isSubmitting) return;
    setIsSubmitting(true);
    
    // Submit vote with empty tags for simplicity
    onVote({
      result,
      leftTags: [],
      rightTags: [],
    });
  };

  return (
    <div className="voting-panel">
      <h3>Which level did you prefer?</h3>
      
      <div className="vote-buttons">
        <button
          onClick={() => handleVote('LEFT')}
          className="vote-button left"
          disabled={isSubmitting}
        >
          ← Left Better
        </button>
        <button
          onClick={() => handleVote('TIE')}
          className="vote-button tie"
          disabled={isSubmitting}
        >
          = Tie
        </button>
        <button
          onClick={() => handleVote('RIGHT')}
          className="vote-button right"
          disabled={isSubmitting}
        >
          Right Better →
        </button>
      </div>
      
      <div className="skip-section">
        <button
          onClick={() => handleVote('SKIP')}
          className="vote-button skip"
          disabled={isSubmitting}
        >
          Skip (can't decide)
        </button>
      </div>
    </div>
  );
}
