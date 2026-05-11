import type { ReactNode } from "react";

type Props = {
  title?: string;
  children: ReactNode;
  action?: ReactNode;
};

export function Panel({ title, children, action }: Props) {
  return (
    <section className="rounded-[28px] border border-black/10 bg-white/80 p-6 shadow-panel backdrop-blur">
      {(title || action) && (
        <div className="mb-4 flex items-center justify-between gap-4">
          {title ? <h2 className="font-display text-2xl">{title}</h2> : <span />}
          {action}
        </div>
      )}
      {children}
    </section>
  );
}
