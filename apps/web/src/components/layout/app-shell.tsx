import type { ReactElement, ReactNode } from "react";

import type { AppRoute } from "../../lib/router";
import { titleForRoute } from "../../lib/router";
import { Sidebar } from "./sidebar";
import { Topbar } from "./topbar";

type AppShellProps = {
  route: AppRoute;
  email: string;
  onSignOut: () => void;
  children: ReactNode;
};

export function AppShell({ route, email, onSignOut, children }: AppShellProps): ReactElement {
  return (
    <div className="shell">
      <Sidebar current={route} />
      <div className="shell__main">
        <Topbar title={titleForRoute(route)} email={email} onSignOut={onSignOut} />
        <main className="shell__content">{children}</main>
      </div>
    </div>
  );
}
