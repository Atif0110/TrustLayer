import { type ReactElement, useEffect, useState } from "react";

import { api } from "./api/client";
import type { AuthSession } from "./api/types";
import { AppShell } from "./components/layout/app-shell";
import { EmptyState } from "./components/states/screen-states";
import { clearSession, readSession } from "./lib/auth-storage";
import { type AppRoute, navigate, parsePath } from "./lib/router";
import { AgentDetailPage } from "./routes/agents/agent-detail";
import { AgentListPage } from "./routes/agents/agent-list";
import { ApprovalQueuePage } from "./routes/approvals/approval-queue";
import { AuditLogPage } from "./routes/audit/audit-log";
import { LoginPage } from "./routes/auth/login";
import { SignupPage } from "./routes/auth/signup";
import { DashboardPage } from "./routes/dashboard/dashboard";
import { PolicyEditorPage } from "./routes/policies/policy-editor";
import { PolicyListPage } from "./routes/policies/policy-list";

function routeFromLocation(): AppRoute {
  return parsePath(window.location.pathname);
}

function Screen({ route }: { route: AppRoute }): ReactElement {
  switch (route.name) {
    case "dashboard":
      return <DashboardPage />;
    case "agents":
      return <AgentListPage />;
    case "agent-detail":
      return <AgentDetailPage id={route.id} />;
    case "policies":
      return <PolicyListPage />;
    case "policy-editor":
      return <PolicyEditorPage />;
    case "approvals":
      return <ApprovalQueuePage />;
    case "audit":
      return <AuditLogPage />;
    case "not-found":
      return <EmptyState title="Not found" detail="That route does not exist." />;
    default:
      return <DashboardPage />;
  }
}

export function App(): ReactElement {
  const [route, setRoute] = useState<AppRoute>(routeFromLocation);
  const [session, setSession] = useState<AuthSession | null>(readSession);

  useEffect(() => {
    function onPopState(): void {
      setRoute(routeFromLocation());
      setSession(readSession());
    }
    window.addEventListener("popstate", onPopState);
    return () => {
      window.removeEventListener("popstate", onPopState);
    };
  }, []);

  const isAuthRoute = route.name === "login" || route.name === "signup";

  if (session === null && !isAuthRoute) {
    return <LoginPage />;
  }

  if (session !== null && isAuthRoute) {
    return (
      <AppShell
        route={{ name: "dashboard" }}
        email={session.email}
        onSignOut={() => {
          void api.logout().catch(() => undefined);
          clearSession();
          setSession(null);
          navigate("/login");
        }}
      >
        <DashboardPage />
      </AppShell>
    );
  }

  if (session === null) {
    return route.name === "signup" ? <SignupPage /> : <LoginPage />;
  }

  return (
    <AppShell
      route={route}
      email={session.email}
      onSignOut={() => {
        void api.logout().catch(() => undefined);
        clearSession();
        setSession(null);
        navigate("/login");
      }}
    >
      <Screen route={route} />
    </AppShell>
  );
}
