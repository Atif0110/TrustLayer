import type { ReactElement } from "react";

import { api } from "../../api/client";
import { useAsync } from "../../hooks/use-async";
import { navigate } from "../../lib/router";
import { Card } from "../../components/primitives/card";
import { EmptyState, ErrorState, LoadingState } from "../../components/states/screen-states";

export function DashboardPage(): ReactElement {
  const { state, reload } = useAsync(async () => {
    const [agents, policies, approvals, audit] = await Promise.all([
      api.listAgents(),
      api.listPolicies(),
      api.listApprovals(),
      api.listAuditEvents(),
    ]);
    return { agents, policies, approvals, audit };
  }, []);

  if (state.status === "loading") {
    return <LoadingState label="Loading overview" />;
  }
  if (state.status === "error") {
    return <ErrorState message={state.message} onRetry={reload} />;
  }

  const { agents, policies, approvals, audit } = state.data;
  const latest = [...audit].reverse().slice(0, 8);

  return (
    <div className="stack">
      <div className="stat-row">
        <button className="stat" type="button" onClick={() => navigate("/agents")}>
          <span className="stat__label">Agents</span>
          <span className="stat__value">{agents.length}</span>
        </button>
        <button className="stat" type="button" onClick={() => navigate("/policies")}>
          <span className="stat__label">Policies</span>
          <span className="stat__value">{policies.length}</span>
        </button>
        <button className="stat" type="button" onClick={() => navigate("/approvals")}>
          <span className="stat__label">Pending approvals</span>
          <span className="stat__value">{approvals.length}</span>
        </button>
        <button className="stat" type="button" onClick={() => navigate("/audit")}>
          <span className="stat__label">Audit events</span>
          <span className="stat__value">{audit.length}</span>
        </button>
      </div>
      <Card title="Latest audit events">
        {latest.length === 0 ? (
          <EmptyState title="No audit events yet" detail="Authorization checks will appear here." />
        ) : (
          <ul className="event-list">
            {latest.map((event) => (
              <li key={`${event.request_id}-${event.created_at}-${event.action}`}>
                <code>{event.request_id}</code>
                <span>{event.decision}</span>
                <span>{event.action}</span>
              </li>
            ))}
          </ul>
        )}
      </Card>
      <Card title="Machine API key">
        <p className="hint">
          Agent keys are now managed per agent. Open an agent detail page to rotate or revoke its machine key.
        </p>
      </Card>
    </div>
  );
}
