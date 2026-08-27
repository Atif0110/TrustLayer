import type { ReactElement } from "react";

import { Button } from "../primitives/button";

type TopbarProps = {
  title: string;
  email: string;
  onSignOut: () => void;
};

export function Topbar({ title, email, onSignOut }: TopbarProps): ReactElement {
  return (
    <header className="topbar">
      <h1 className="topbar__title">{title}</h1>
      <div className="topbar__meta">
        <span className="topbar__email">{email}</span>
        <Button variant="ghost" onClick={onSignOut}>
          Sign out
        </Button>
      </div>
    </header>
  );
}
