import { useEffect, useRef } from 'react';

interface Props {
  open: boolean;
  title: string;
  message: string;
  confirmLabel?: string;
  confirmDanger?: boolean;
  onConfirm: () => void;
  onCancel: () => void;
}

export default function ConfirmModal({ open, title, message, confirmLabel = 'Confirm', confirmDanger = false, onConfirm, onCancel }: Props) {
  const confirmRef = useRef<HTMLButtonElement>(null);

  useEffect(() => {
    if (open) {
      confirmRef.current?.focus();
      const handleKey = (e: KeyboardEvent) => {
        if (e.key === 'Escape') onCancel();
      };
      document.addEventListener('keydown', handleKey);
      return () => document.removeEventListener('keydown', handleKey);
    }
  }, [open, onCancel]);

  if (!open) return null;

  return (
    <div className="fixed inset-0 z-[9998] flex items-center justify-center" role="dialog" aria-modal="true">
      {/* Backdrop */}
      <div className="absolute inset-0 bg-black/50 backdrop-blur-sm" onClick={onCancel} />
      {/* Modal */}
      <div className="relative bg-bg-secondary border border-bg-tertiary rounded-lg p-5 shadow-xl shadow-black/30 max-w-sm w-full mx-4">
        <h3 className="text-sm font-semibold mb-2">{title}</h3>
        <p className="text-xs text-text-secondary mb-4 leading-relaxed">{message}</p>
        <div className="flex justify-end gap-2">
          <button onClick={onCancel}
            className="px-3 py-1.5 text-xs bg-bg-tertiary rounded hover:bg-bg-quaternary/50 transition-colors">
            Cancel
          </button>
          <button ref={confirmRef} onClick={onConfirm}
            className={`px-3 py-1.5 text-xs rounded font-medium transition-colors ${
              confirmDanger
                ? 'bg-danger/90 hover:bg-danger text-white'
                : 'bg-accent hover:bg-accent-hover text-bg-primary'
            }`}>
            {confirmLabel}
          </button>
        </div>
      </div>
    </div>
  );
}
