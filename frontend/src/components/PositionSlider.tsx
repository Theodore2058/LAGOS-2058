interface Props {
  dimension: string;
  value: number;
  description?: string;
  onChange: (value: number) => void;
}

export default function PositionSlider({ dimension, value, description, onChange }: Props) {
  const color = value > 0 ? `rgba(59,130,246,${Math.abs(value) / 5})` : value < 0 ? `rgba(239,68,68,${Math.abs(value) / 5})` : 'transparent';

  return (
    <div className="flex items-center gap-3 py-1 group" title={description}>
      <span className="w-48 text-xs text-text-secondary truncate">{dimension}</span>
      <input
        type="range"
        min={-5}
        max={5}
        step={0.1}
        value={value}
        onChange={(e) => onChange(parseFloat(e.target.value))}
        className="flex-1 h-1.5 accent-accent cursor-pointer"
        style={{ background: `linear-gradient(to right, #ef4444 0%, #374151 50%, #3b82f6 100%)` }}
      />
      <input
        type="number"
        min={-5}
        max={5}
        step={0.1}
        value={value}
        onChange={(e) => onChange(Math.max(-5, Math.min(5, parseFloat(e.target.value) || 0)))}
        className="w-16 bg-bg-tertiary border border-bg-tertiary rounded px-2 py-0.5 text-xs text-center"
      />
      <div className="w-3 h-3 rounded-sm" style={{ backgroundColor: color }} />
    </div>
  );
}
