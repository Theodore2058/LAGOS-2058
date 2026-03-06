interface Props {
  /** Message below spinner */
  message?: string;
  /** Use as fullscreen overlay with backdrop blur */
  overlay?: boolean;
  /** Size: 'sm' (w-6), 'md' (w-8, default), 'lg' (w-10) */
  size?: 'sm' | 'md' | 'lg';
}

const SIZES = { sm: 'w-6 h-6 border-[1.5px]', md: 'w-8 h-8 border-2', lg: 'w-10 h-10 border-[3px]' };

export default function LoadingSpinner({ message, overlay, size = 'md' }: Props) {
  const spinner = (
    <div className="text-center">
      <div className={`animate-spin ${SIZES[size]} border-accent border-t-transparent rounded-full mx-auto ${message ? 'mb-3' : ''}`} />
      {message && <p className="text-sm text-text-secondary font-medium">{message}</p>}
    </div>
  );

  if (overlay) {
    return (
      <div className="absolute inset-0 bg-bg-primary/60 backdrop-blur-sm z-20 flex items-center justify-center rounded-lg">
        {spinner}
      </div>
    );
  }

  return (
    <div className="flex items-center justify-center py-16">
      {spinner}
    </div>
  );
}
