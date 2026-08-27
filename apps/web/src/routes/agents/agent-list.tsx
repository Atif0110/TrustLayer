import { type FormEvent, type ReactElement, useState } from "react";

import { api } from "../../api/client";
import { useAsync } from "../../hooks/use-async";
import { formatTimestamp } from "../../lib/format";
import { navigate } from "../../lib/router";
import { Badge } from "../../components/primitives/badge";
import { Button } from "../../components/primitives/button";
import { Card } from "../../components/primitives/card";
import { Input } from "../../components/primitives/input";
import { Table } from "../../components/primitives/table";
import { EmptyState, ErrorState, LoadingState } from "../../components/states/screen-states";

export function AgentListPage(): ReactElement {
  const { state, reload } = useAsync(() => api.listAgents(), []);
  const [name, setName] = useState("");
  const [formError, setFormError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  async function onSubmit(event: FormEvent<HTMLFormElement>): Promise<void> {
    event.preventDefault();
    setSubmitting(true);
    setFormError(null);
    try {
      const created = await api.createAgent({ name });
      setName("");
      reload();
      navigate(`/agents/${created.id}`);
    } catch (caught) {
      setFormError(caught instanceof Error ? caught.message : "Unable to create agent");
    } finally {
      setSubmitting(false);
    }
  }

  if (state.status === "loading") {
    return <LoadingState label="Loading agents" />;
  }
  if (state.status === "error") {
    return <ErrorState message={state.message} onRetry={reload} />;
  }

  return (
    <div className="stack">
      <Card title="Create agent">
        <form className="form form--inline" onSubmit={(event) => void onSubmit(event)}>
          <Input
            label="Name"
            name="agentName"
            required
            value={name}
            onChange={(event) => {
              setName(event.target.value);
            }}
          />
          <Button type="submit" disabled={submitting}>
            {submitting ? "Creating…" : "Create"}
          </Button>
        </form>
        {formError !== null ? <p className="field__error">{formError}</p> : null}
      </Card>
      <Card title="Agents">
        {state.data.length === 0 ? (
          <EmptyState title="No agents yet" detail="Create an agent to authorize actions against a policy." />
        ) : (
          <Table
            columns={[
              {
                key: "name",
                header: "Name",
                render: (row) => (
                  <button className="link" type="button" onClick={() => navigate(`/agents/${row.id}`)}>
                    {row.name}
                  </button>
                ),
              },
              {
                key: "id",
                header: "ID",
                mono: true,
              },
              {
                key: "status",
                header: "Status",
                render: (row) => <Badge tone={row.status === "active" ? "neutral" : "deny"}>{row.status}</Badge>,
              },
              {
                key: "created_at",
                header: "Created",
                mono: true,
                render: (row) => formatTimestamp(row.created_at),
              },
            ]}
            rows={state.data}
            getRowKey={(row) => row.id}
          />
        )}
      </Card>
    </div>
  );
}
