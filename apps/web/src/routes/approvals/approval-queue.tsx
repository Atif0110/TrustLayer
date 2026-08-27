import type { ReactElement } from "react";

import { api } from "../../api/client";
import { useAsync } from "../../hooks/use-async";
import { formatTimestamp } from "../../lib/format";
import { Button } from "../../components/primitives/button";
import { Card } from "../../components/primitives/card";
import { Table } from "../../components/primitives/table";
import { EmptyState, ErrorState, LoadingState } from "../../components/states/screen-states";

export function ApprovalQueuePage(): ReactElement {
  const { state, reload } = useAsync(() => api.listApprovals(), []);

  async function decide(id: string, action: "approve" | "deny"): Promise<void> {
    if (action === "approve") {
      await api.approve(id);
    } else {
      await api.deny(id);
    }
    reload();
  }

  if (state.status === "loading") {
    return <LoadingState label="Loading approvals" />;
  }
  if (state.status === "error") {
    return <ErrorState message={state.message} onRetry={reload} />;
  }

  return (
    <Card title="Pending approvals">
      {state.data.length === 0 ? (
        <EmptyState title="No pending approvals" detail="REQUIRE_APPROVAL decisions will queue here." />
      ) : (
        <Table
          columns={[
            { key: "request_id", header: "Request", mono: true },
            { key: "action", header: "Action", mono: true },
            { key: "resource", header: "Resource", mono: true },
            {
              key: "expires_at",
              header: "Expires",
              mono: true,
              render: (row) => formatTimestamp(row.expires_at),
            },
            {
              key: "id",
              header: "",
              render: (row) => (
                <div className="row-actions">
                  <Button
                    onClick={() => {
                      void decide(row.id, "approve");
                    }}
                  >
                    Approve
                  </Button>
                  <Button
                    variant="danger"
                    onClick={() => {
                      void decide(row.id, "deny");
                    }}
                  >
                    Deny
                  </Button>
                </div>
              ),
            },
          ]}
          rows={state.data}
          getRowKey={(row) => row.id}
        />
      )}
    </Card>
  );
}
