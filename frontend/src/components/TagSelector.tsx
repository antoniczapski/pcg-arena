/**
 * Stage 5: Tag Selector Component
 * 
 * Displays hoverable tag options for level feedback.
 * Allows selecting up to 3 tags per level.
 */

import './TagSelector.css';

// Available tags matching backend ALLOWED_TAGS
export const AVAILABLE_TAGS = [
  { id: 'fun', label: '😄 Fun', color: '#22c55e' },
  { id: 'boring', label: '😴 Boring', color: '#6b7280' },
  { id: 'creative', label: '✨ Creative', color: '#a855f7' },
  { id: 'good_flow', label: '🌊 Good Flow', color: '#3b82f6' },
  { id: 'too_hard', label: '💀 Too Hard', color: '#ef4444' },
  { id: 'too_easy', label: '🍼 Too Easy', color: '#fbbf24' },
  { id: 'unfair', label: '😤 Unfair', color: '#f97316' },
  { id: 'confusing', label: '❓ Confusing', color: '#8b5cf6' },
  { id: 'not_mario_like', label: '🚫 Not Mario-like', color: '#64748b' },
];

const MAX_TAGS = 3;

interface TagSelectorProps {
  selectedTags: string[];
  onTagsChange: (tags: string[]) => void;
  disabled?: boolean;
}

export function TagSelector({ selectedTags, onTagsChange, disabled = false }: TagSelectorProps) {
  const toggleTag = (tagId: string) => {
    if (disabled) return;
    
    if (selectedTags.includes(tagId)) {
      // Remove tag
      onTagsChange(selectedTags.filter(t => t !== tagId));
    } else if (selectedTags.length < MAX_TAGS) {
      // Add tag if under limit
      onTagsChange([...selectedTags, tagId]);
    }
  };

  return (
    <div className="tag-selector">
      <div className="tag-selector-header">
        <span>Tag this level</span>
        <span className="tag-count">{selectedTags.length}/{MAX_TAGS}</span>
      </div>
      <div className="tag-options">
        {AVAILABLE_TAGS.map(tag => {
          const isSelected = selectedTags.includes(tag.id);
          const isDisabled = !isSelected && selectedTags.length >= MAX_TAGS;
          
          return (
            <button
              key={tag.id}
              className={`tag-option ${isSelected ? 'selected' : ''} ${isDisabled ? 'disabled' : ''}`}
              style={{ 
                '--tag-color': tag.color,
                borderColor: isSelected ? tag.color : undefined,
                backgroundColor: isSelected ? `${tag.color}20` : undefined,
              } as React.CSSProperties}
              onClick={() => toggleTag(tag.id)}
              disabled={disabled || isDisabled}
              type="button"
            >
              {tag.label}
            </button>
          );
        })}
      </div>
    </div>
  );
}

/**
 * Hoverable level card with tag selector overlay
 */
interface TaggableLevelPreviewProps {
  children: React.ReactNode;
  selectedTags: string[];
  onTagsChange: (tags: string[]) => void;
  disabled?: boolean;
}

export function TaggableLevelPreview({
  children,
  selectedTags,
  onTagsChange,
  disabled = false
}: TaggableLevelPreviewProps) {
  const hasTags = selectedTags.length > 0;

  return (
    <div className={`taggable-level-preview ${hasTags ? 'has-tags' : ''}`}>
      <div className="level-content">
        {children}
      </div>

      {/* Tag overlay - visible ONLY on hover via CSS */}
      <div className="tag-overlay">
        <TagSelector
          selectedTags={selectedTags}
          onTagsChange={onTagsChange}
          disabled={disabled}
        />
      </div>

      {/* Selected tags badge (hidden on hover via CSS) */}
      {hasTags && (
        <div className="selected-tags-badge">
          {selectedTags.length} tag{selectedTags.length > 1 ? 's' : ''} selected
        </div>
      )}
    </div>
  );
}

