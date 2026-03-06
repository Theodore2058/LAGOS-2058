import { createContext, useContext, useState, useCallback, useEffect, useRef } from 'react';
import type { ReactNode } from 'react';

type ToastType = 'success' | 'error' | 'info';

interface Toast {
  id: number;
  message: string;
  type: ToastType;
}

interface ToastContextValue {
  toast: (message: string, type?: ToastType) => void;
}

const ToastContext = createContext<ToastContextValue>({ toast: () => {} });

export const useToast = () => useContext(ToastContext);

export function ToastProvider({ children }: { children: ReactNode }) {
  const [toasts, setToasts] = useState<Toast[]>([]);
  const nextId = useRef(0);

  const toast = useCallback((message: string, type: ToastType = 'info') => {
    const id = nextId.current++;
    setToasts(prev => [...prev, { id, message, type }]);
  }, []);

  const remove = useCallback((id: number) => {
    setToasts(prev => prev.filter(t => t.id !== id));
  }, []);

  return (
    <ToastContext.Provider value={{ toast }}>
      {children}
      {/* Toast container */}
      <div className="fixed bottom-4 right-4 z-[9999] flex flex-col gap-2 pointer-events-none">
        {toasts.map(t => (
          <ToastItem key={t.id} toast={t} onDone={() => remove(t.id)} />
        ))}
      </div>
    </ToastContext.Provider>
  );
}

function ToastItem({ toast: t, onDone }: { toast: Toast; onDone: () => void }) {
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    requestAnimationFrame(() => setVisible(true));
    const timer = setTimeout(() => {
      setVisible(false);
      setTimeout(onDone, 200);
    }, 3000);
    return () => clearTimeout(timer);
  }, [onDone]);

  const colors = {
    success: 'bg-success/90 text-white',
    error: 'bg-danger/90 text-white',
    info: 'bg-bg-secondary text-text-primary border border-bg-tertiary',
  };

  const icons = {
    success: 'M5 13l4 4L19 7',
    error: 'M18 6L6 18M6 6l12 12',
    info: 'M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z',
  };

  return (
    <div className={`pointer-events-auto flex items-center gap-2 px-4 py-2.5 rounded-lg shadow-lg shadow-black/30 text-sm font-medium transition-all duration-200 ${colors[t.type]} ${visible ? 'opacity-100 translate-x-0' : 'opacity-0 translate-x-4'}`}>
      <svg className="w-4 h-4 shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round">
        <path d={icons[t.type]} />
      </svg>
      {t.message}
    </div>
  );
}
