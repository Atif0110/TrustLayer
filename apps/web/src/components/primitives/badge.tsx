import type { ReactElement, ReactNode } from "react";

export type BadgeTone = "neutral" | "allow" | "deny" | "approval";

type BadgeProps = {
  children: ReactNode;
  tone?: BadgeTone;
};

export function Badge({ children, tone = "neutral" }: BadgeProps): ReactElement {
  return <span className={`badge badge--${tone}`}>{children}</span>;
}
