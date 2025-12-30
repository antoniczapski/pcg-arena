import { useState } from 'react';

export interface VoteData {
  result: 'LEFT' | 'RIGHT' | 'TIE' | 'SKIP';
  leftTags: string[];
  rightTags: string[];
}

interface VotingPanelProps {
  onVote: (vote: VoteData) => void;
  /** Use A/B naming instead of Left/Right */
  useABNaming?: boolean;
  /** Tags already selected for left level */
  leftTags?: string[];
  /** Tags already selected for right level */
  rightTags?: string[];
}

export function VotingPanel({ 
  onVote, 
  useABNaming = false,
  leftTags = [],
  rightTags = [],
}: VotingPanelProps) {
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleVote = (result: VoteData['result']) => {
    if (isSubmitting) return;
    setIsSubmitting(true);
    
    // Submit vote with selected tags
    onVote({
      result,
      leftTags,
      rightTags,
    });
  };

  // Labels based on naming scheme
  const leftLabel = useABNaming ? 'A Better' : '← Left Better';
  const rightLabel = useABNaming ? 'B Better' : 'Right Better →';

  return (
    <div className="voting-panel">
      <h3>Which level did you prefer?</h3>
      
      <div className="vote-buttons">
        <button
          onClick={() => handleVote('LEFT')}
          className="vote-button left"
          disabled={isSubmitting}
        >
          {leftLabel}
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
          {rightLabel}
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
