import type { ReactElement } from "react";

import { api } from "../../api/client";
import { useAsync } from "../../hooks/use-async";
import { formatTimestamp } from "../../lib/format";
import { DecisionBadge } from "../../components/decision-badge/decision-badge";
import { Card } from "../../components/primitives/card";
import { Table } from "../../components/primitives/table";
import { EmptyState, ErrorState, LoadingState } from "../../components/states/screen-states";

export function AuditLogPage(): ReactElement {
  const { state, reload } = useAsync(() => api.listAuditEvents(), []);

  if (state.status === "loading") {
    return <LoadingState label="Loading audit log" />;
  }
  if (state.status === "error") {
    return <ErrorState message={state.message} onRetry={reload} />;
  }

  return (
    <Card title="Audit events">
      {state.data.length === 0 ? (
        <EmptyState title="No audit events yet" detail="Every authorization decision is appended here." />
      ) : (
        <Table
          columns={[
            { key: "request_id", header: "Request", mono: true },
            {
              key: "decision",
              header: "Decision",
              render: (row) => <DecisionBadge decision={row.decision} />,
            },
            { key: "action", header: "Action", mono: true },
            { key: "resource", header: "Resource", mono: true },
            { key: "reason", header: "Reason" },
            { key: "policy_version", header: "Policy", mono: true },
            {
              key: "created_at",
              header: "Time",
              mono: true,
              render: (row) => formatTimestamp(row.created_at),
            },
          ]}
          rows={state.data}
          getRowKey={(row) => `${row.request_id}-${row.created_at}-${row.action}`}
        />
      )}
    </Card>
  );
}
