import type { ReactElement } from "react";

export function LoadingState({ label = "Loading" }: { label?: string }): ReactElement {
  return (
    <p className="state state--muted" role="status">
      {label}…
    </p>
  );
}

export function EmptyState({ title, detail }: { title: string; detail?: string }): ReactElement {
  return (
    <div className="state">
      <p className="state__title">{title}</p>
      {detail !== undefined ? <p className="state__detail">{detail}</p> : null}
    </div>
  );
}

export function ErrorState({ message, onRetry }: { message: string; onRetry?: () => void }): ReactElement {
  return (
    <div className="state state--error" role="alert">
      <p className="state__title">Request failed</p>
      <p className="state__detail">{message}</p>
      {onRetry !== undefined ? (
        <button className="btn btn--secondary" type="button" onClick={onRetry}>
          Retry
        </button>
      ) : null}
    </div>
  );
}
