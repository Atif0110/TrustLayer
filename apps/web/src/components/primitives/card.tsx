import type { ReactElement, ReactNode } from "react";

type CardProps = {
  title?: string;
  actions?: ReactNode;
  children: ReactNode;
};

export function Card({ title, actions, children }: CardProps): ReactElement {
  return (
    <section className="card">
      {title !== undefined || actions !== undefined ? (
        <header className="card__header">
          {title !== undefined ? <h2 className="card__title">{title}</h2> : <span />}
          {actions !== undefined ? <div className="card__actions">{actions}</div> : null}
        </header>
      ) : null}
      <div className="card__body">{children}</div>
    </section>
  );
}
