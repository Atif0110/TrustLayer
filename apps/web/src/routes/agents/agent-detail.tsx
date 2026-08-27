import { type ReactElement, useState } from "react";

import { api } from "../../api/client";
import { useAsync } from "../../hooks/use-async";
import { formatTimestamp } from "../../lib/format";
import { navigate } from "../../lib/router";
import { Badge } from "../../components/primitives/badge";
import { Button } from "../../components/primitives/button";
import { Card } from "../../components/primitives/card";
import { EmptyState, ErrorState, LoadingState } from "../../components/states/screen-states";

type AgentDetailPageProps = {
  id: string;
};

export function AgentDetailPage({ id }: AgentDetailPageProps): ReactElement {
  const [rawKey, setRawKey] = useState<string | null>(null);
  const [keyError, setKeyError] = useState<string | null>(null);
  const [rotating, setRotating] = useState(false);
  const { state, reload } = useAsync(async () => {
    const [agent, keys] = await Promise.all([api.getAgent(id), api.listAgentKeys(id)]);
    return { agent, keys };
  }, [id]);

  if (state.status === "loading") {
    return <LoadingState label="Loading agent" />;
  }
  if (state.status === "error") {
    return <ErrorState message={state.message} onRetry={reload} />;
  }

  async function onRotate(): Promise<void> {
    setRotating(true);
    setKeyError(null);
    try {
      const response = await api.rotateAgentKey(id);
      setRawKey(response.api_key);
      reload();
    } catch (caught) {
      setKeyError(caught instanceof Error ? caught.message : "Unable to rotate key");
    } finally {
      setRotating(false);
    }
  }

  async function onRevoke(keyId: string): Promise<void> {
    setKeyError(null);
    try {
      await api.revokeAgentKey(id, keyId);
      reload();
    } catch (caught) {
      setKeyError(caught instanceof Error ? caught.message : "Unable to revoke key");
    }
  }

  const { agent, keys } = state.data;
  if (agent === undefined) {
    return (
      <Card>
        <EmptyState title="Agent not found" detail="This agent is not in the current organization." />
        <Button
          variant="secondary"
          onClick={() => {
            navigate("/agents");
          }}
        >
          Back to agents
        </Button>
      </Card>
    );
  }

  return (
    <Card
      title={agent.name}
      actions={
        <Button variant="ghost" onClick={() => navigate("/agents")}>
          All agents
        </Button>
      }
    >
      <dl className="meta-list">
        <div>
          <dt>ID</dt>
          <dd className="mono">{agent.id}</dd>
        </div>
        <div>
          <dt>Status</dt>
          <dd>
            <Badge>{agent.status}</Badge>
          </dd>
        </div>
        <div>
          <dt>Created</dt>
          <dd className="mono">{formatTimestamp(agent.created_at)}</dd>
        </div>
      </dl>
      <div className="agent-keys">
        <div className="form__actions">
          <Button onClick={() => void onRotate()} disabled={rotating}>
            {rotating ? "Rotating…" : "Rotate machine key"}
          </Button>
        </div>
        {rawKey !== null ? <pre className="code-block">{rawKey}</pre> : null}
        {keyError !== null ? <p className="field__error">{keyError}</p> : null}
        {keys.length === 0 ? (
          <EmptyState title="No keys yet" detail="Rotate a key to create the first machine credential for this agent." />
        ) : (
          <div className="table-wrap">
            <table className="table">
              <thead>
                <tr>
                  <th>Prefix</th>
                  <th>Hint</th>
                  <th>Created</th>
                  <th>Last used</th>
                  <th>Revoked</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                {keys.map((key) => (
                  <tr key={key.id}>
                    <td className="table__cell--mono">{key.key_prefix}</td>
                    <td className="table__cell--mono">{formatTimestamp(key.created_at)}</td>
                    <td className="table__cell--mono">{key.last_used_at ? formatTimestamp(key.last_used_at) : "never"}</td>
                    <td className="table__cell--mono">{key.revoked_at ? formatTimestamp(key.revoked_at) : "active"}</td>
                    <td>
                      {key.revoked_at === null ? (
                        <Button variant="ghost" onClick={() => void onRevoke(key.id)}>
                          Revoke
                        </Button>
                      ) : null}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </Card>
  );
}
