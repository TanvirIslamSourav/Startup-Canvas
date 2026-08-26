import * as ToastPrimitive from '@radix-ui/react-toast';
import { X } from 'lucide-react';
import * as React from 'react';
import { cn } from '@/utils/cn';

export const ToastProvider = ToastPrimitive.Provider;

export const ToastViewport = React.forwardRef<
  React.ElementRef<typeof ToastPrimitive.Viewport>,
  React.ComponentPropsWithoutRef<typeof ToastPrimitive.Viewport>
>(({ className, ...props }, ref) => (
  <ToastPrimitive.Viewport
    ref={ref}
    className={cn(
      'fixed bottom-4 right-4 z-[100] flex max-h-screen w-full max-w-sm flex-col gap-2',
      className,
    )}
    {...props}
  />
));
ToastViewport.displayName = ToastPrimitive.Viewport.displayName;

interface ToastProps
  extends Omit<
    React.ComponentPropsWithoutRef<typeof ToastPrimitive.Root>,
    'title'
  > {
  title?: React.ReactNode;
  description?: React.ReactNode;
  variant?: 'default' | 'destructive' | 'success';
}

export const Toast = React.forwardRef<
  React.ElementRef<typeof ToastPrimitive.Root>,
  ToastProps
>(({ className, title, description, variant = 'default', ...props }, ref) => (
  <ToastPrimitive.Root
    ref={ref}
    className={cn(
      'pointer-events-auto flex w-full items-start gap-3 rounded-md border p-4 shadow-lg',
      variant === 'default' && 'border-border bg-background text-foreground',
      variant === 'destructive' && 'border-destructive bg-destructive text-destructive-foreground',
      variant === 'success' && 'border-emerald-500 bg-emerald-600 text-white',
      className,
    )}
    {...props}
  >
    <div className="flex-1 space-y-1">
      {title ? <ToastPrimitive.Title className="text-sm font-semibold">{title}</ToastPrimitive.Title> : null}
      {description ? (
        <ToastPrimitive.Description className="text-sm opacity-90">
          {description}
        </ToastPrimitive.Description>
      ) : null}
    </div>
    <ToastPrimitive.Close className="rounded p-1 opacity-70 transition-opacity hover:opacity-100">
      <X className="h-4 w-4" />
    </ToastPrimitive.Close>
  </ToastPrimitive.Root>
));
Toast.displayName = 'Toast';

/** Tiny imperative API. Use via `useToast()` hook below. */
type ToastItem = { id: number; title?: string; description?: string; variant?: ToastProps['variant'] };

interface ToastContextValue {
  toast: (msg: { title?: string; description?: string; variant?: ToastProps['variant'] }) => void;
}

const ToastContext = React.createContext<ToastContextValue | null>(null);

export function ToastBus({ children }: { children: React.ReactNode }) {
  const [items, setItems] = React.useState<ToastItem[]>([]);

  const toast = React.useCallback<ToastContextValue['toast']>((msg) => {
    const id = Date.now() + Math.random();
    setItems((prev) => [...prev, { id, ...msg }]);
    setTimeout(() => setItems((prev) => prev.filter((t) => t.id !== id)), 4000);
  }, []);

  return (
    <ToastContext.Provider value={{ toast }}>
      <ToastProvider duration={4000}>
        {children}
        {items.map((t) => (
          <Toast key={t.id} variant={t.variant} title={t.title} description={t.description} />
        ))}
        <ToastViewport />
      </ToastProvider>
    </ToastContext.Provider>
  );
}

export function useToast(): ToastContextValue {
  const ctx = React.useContext(ToastContext);
  if (!ctx) throw new Error('useToast must be used within ToastBus');
  return ctx;
}