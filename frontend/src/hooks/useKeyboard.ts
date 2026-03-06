import { useEffect } from 'react';

interface ShortcutMap {
  [key: string]: () => void;
}

/**
 * Register keyboard shortcuts. Keys use format: "ctrl+s", "ctrl+enter", "escape"
 * Modifiers: ctrl, shift, alt, meta
 */
export function useKeyboard(shortcuts: ShortcutMap, deps: unknown[] = []) {
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      const parts: string[] = [];
      if (e.ctrlKey || e.metaKey) parts.push('ctrl');
      if (e.shiftKey) parts.push('shift');
      if (e.altKey) parts.push('alt');
      parts.push(e.key.toLowerCase());
      const combo = parts.join('+');

      if (shortcuts[combo]) {
        e.preventDefault();
        shortcuts[combo]();
      }
    };

    document.addEventListener('keydown', handler);
    return () => document.removeEventListener('keydown', handler);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, deps);
}
