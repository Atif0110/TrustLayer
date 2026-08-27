import type { ReactElement } from "react";

import type { AppRoute } from "../../lib/router";
import { navigate, toPath } from "../../lib/router";

type NavItem = {
  label: string;
  route: AppRoute;
};

const ITEMS: NavItem[] = [
  { label: "Overview", route: { name: "dashboard" } },
  { label: "Agents", route: { name: "agents" } },
  { label: "Policies", route: { name: "policies" } },
  { label: "Approvals", route: { name: "approvals" } },
  { label: "Audit log", route: { name: "audit" } },
];

function isActive(current: AppRoute, item: AppRoute): boolean {
  if (item.name === "agents") {
    return current.name === "agents" || current.name === "agent-detail";
  }
  if (item.name === "policies") {
    return current.name === "policies" || current.name === "policy-editor";
  }
  return current.name === item.name;
}

type SidebarProps = {
  current: AppRoute;
};

export function Sidebar({ current }: SidebarProps): ReactElement {
  return (
    <aside className="sidebar">
      <div className="sidebar__brand">
        <span className="sidebar__mark">TL</span>
        <span className="sidebar__name">TrustLayer</span>
      </div>
      <nav className="sidebar__nav" aria-label="Primary">
        {ITEMS.map((item) => {
          const href = toPath(item.route);
          const active = isActive(current, item.route);
          return (
            <a
              key={item.label}
              className={active ? "sidebar__link sidebar__link--active" : "sidebar__link"}
              href={href}
              aria-current={active ? "page" : undefined}
              onClick={(event) => {
                event.preventDefault();
                navigate(href);
              }}
            >
              {item.label}
            </a>
          );
        })}
      </nav>
    </aside>
  );
}
