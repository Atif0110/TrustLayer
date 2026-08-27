import type { ReactElement } from "react";

import { api } from "../../api/client";
import { useAsync } from "../../hooks/use-async";
import { navigate } from "../../lib/router";
import { Badge } from "../../components/primitives/badge";
import { Button } from "../../components/primitives/button";
import { Card } from "../../components/primitives/card";
import { Table } from "../../components/primitives/table";
import { EmptyState, ErrorState, LoadingState } from "../../components/states/screen-states";

export function PolicyListPage(): ReactElement {
  const { state, reload } = useAsync(() => api.listPolicies(), []);

  if (state.status === "loading") {
    return <LoadingState label="Loading policies" />;
  }
  if (state.status === "error") {
    return <ErrorState message={state.message} onRetry={reload} />;
  }

  return (
    <Card
      title="Policies"
      actions={
        <Button onClick={() => navigate("/policies/new")}>New policy</Button>
      }
    >
      {state.data.length === 0 ? (
        <EmptyState title="No policies yet" detail="Create a policy with form-based rules. Default is DENY." />
      ) : (
        <Table
          columns={[
            { key: "name", header: "Name" },
            { key: "version", header: "Version", mono: true },
            {
              key: "is_active",
              header: "Active",
              render: (row) => <Badge tone={row.is_active ? "allow" : "neutral"}>{row.is_active ? "yes" : "no"}</Badge>,
            },
            {
              key: "rules",
              header: "Rules",
              mono: true,
              render: (row) => String(row.rules.length),
            },
          ]}
          rows={state.data}
          getRowKey={(row) => row.id}
        />
      )}
    </Card>
  );
}
