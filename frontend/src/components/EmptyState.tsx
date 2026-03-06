interface Props {
  /** SVG path for the icon */
  icon?: string;
  title: string;
  description?: string;
  /** Optional action button */
  action?: { label: string; onClick: () => void };
}

export default function EmptyState({ icon, title, description, action }: Props) {
  return (
    <div className="flex flex-col items-center justify-center py-16 text-center px-4">
      {icon && (
        <svg className="w-12 h-12 text-text-secondary/20 mb-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.5} strokeLinecap="round" strokeLinejoin="round">
          <path d={icon} />
        </svg>
      )}
      <p className="text-text-secondary mb-1">{title}</p>
      {description && <p className="text-xs text-text-secondary/60 max-w-xs">{description}</p>}
      {action && (
        <button onClick={action.onClick}
          className="mt-4 px-4 py-1.5 text-sm bg-accent rounded hover:bg-accent-hover text-bg-primary font-medium btn-accent">
          {action.label}
        </button>
      )}
    </div>
  );
}
