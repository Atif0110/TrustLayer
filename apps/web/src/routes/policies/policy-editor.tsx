import { type FormEvent, type ReactElement, useState } from "react";

import { api } from "../../api/client";
import type { Decision, PolicyRule } from "../../api/types";
import { navigate } from "../../lib/router";
import { Button } from "../../components/primitives/button";
import { Card } from "../../components/primitives/card";
import { Input } from "../../components/primitives/input";

type DraftRule = {
  key: string;
  action: string;
  amountMode: "none" | "lte" | "gt";
  amount: string;
  then: Decision;
};

function newDraft(): DraftRule {
  return {
    key: crypto.randomUUID(),
    action: "",
    amountMode: "none",
    amount: "",
    then: "ALLOW",
  };
}

function toPolicyRules(drafts: DraftRule[]): PolicyRule[] {
  return drafts.map((draft) => {
    const condition: PolicyRule["if"] = { action: draft.action.trim() };
    if (draft.amountMode !== "none" && draft.amount !== "") {
      const amount = Number(draft.amount);
      if (draft.amountMode === "lte") {
        condition.amount_lte = amount;
      } else {
        condition.amount_gt = amount;
      }
    }
    return { if: condition, then: draft.then };
  });
}

export function PolicyEditorPage(): ReactElement {
  const [name, setName] = useState("");
  const [rules, setRules] = useState<DraftRule[]>([newDraft()]);
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  function updateRule(key: string, patch: Partial<DraftRule>): void {
    setRules((current) => current.map((rule) => (rule.key === key ? { ...rule, ...patch } : rule)));
  }

  async function onSubmit(event: FormEvent<HTMLFormElement>): Promise<void> {
    event.preventDefault();
    const parsed = toPolicyRules(rules).filter((rule) => rule.if.action.length > 0);
    if (parsed.length === 0) {
      setError("Add at least one rule with an action");
      return;
    }
    setSubmitting(true);
    setError(null);
    try {
      await api.createPolicy({ name, rules: parsed });
      navigate("/policies");
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Unable to create policy");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <Card title="New policy">
      <p className="hint">
        Rules are evaluated top to bottom. First match wins. If nothing matches, the engine denies.
      </p>
      <form className="form" onSubmit={(event) => void onSubmit(event)}>
        <Input
          label="Policy name"
          name="policyName"
          required
          value={name}
          onChange={(event) => {
            setName(event.target.value);
          }}
        />
        <div className="rule-list">
          {rules.map((rule, index) => (
            <fieldset className="rule" key={rule.key}>
              <legend>Rule {index + 1}</legend>
              <Input
                label="Action"
                name={`action-${rule.key}`}
                placeholder="refund.create"
                required
                value={rule.action}
                onChange={(event) => {
                  updateRule(rule.key, { action: event.target.value });
                }}
              />
              <label className="field">
                <span className="field__label">Amount condition</span>
                <select
                  className="input"
                  value={rule.amountMode}
                  onChange={(event) => {
                    updateRule(rule.key, { amountMode: event.target.value as DraftRule["amountMode"] });
                  }}
                >
                  <option value="none">None</option>
                  <option value="lte">amount ≤</option>
                  <option value="gt">amount &gt;</option>
                </select>
              </label>
              {rule.amountMode !== "none" ? (
                <Input
                  label="Amount"
                  name={`amount-${rule.key}`}
                  type="number"
                  required
                  value={rule.amount}
                  onChange={(event) => {
                    updateRule(rule.key, { amount: event.target.value });
                  }}
                />
              ) : null}
              <label className="field">
                <span className="field__label">Then</span>
                <select
                  className="input"
                  value={rule.then}
                  onChange={(event) => {
                    updateRule(rule.key, { then: event.target.value as Decision });
                  }}
                >
                  <option value="ALLOW">ALLOW</option>
                  <option value="REQUIRE_APPROVAL">REQUIRE_APPROVAL</option>
                  <option value="DENY">DENY</option>
                </select>
              </label>
              {rules.length > 1 ? (
                <Button
                  variant="ghost"
                  onClick={() => {
                    setRules((current) => current.filter((item) => item.key !== rule.key));
                  }}
                >
                  Remove
                </Button>
              ) : null}
            </fieldset>
          ))}
        </div>
        <div className="form__actions">
          <Button
            variant="secondary"
            onClick={() => {
              setRules((current) => [...current, newDraft()]);
            }}
          >
            Add rule
          </Button>
          <Button type="submit" disabled={submitting}>
            {submitting ? "Saving…" : "Save policy"}
          </Button>
          <Button variant="ghost" onClick={() => navigate("/policies")}>
            Cancel
          </Button>
        </div>
        {error !== null ? <p className="field__error">{error}</p> : null}
      </form>
    </Card>
  );
}
