import type { ReactElement } from "react";

import type { AuditDecision } from "../../api/types";
import { Badge, type BadgeTone } from "../primitives/badge";

function toneForDecision(decision: AuditDecision): BadgeTone {
  if (decision === "ALLOW" || decision === "APPROVED") {
    return "allow";
  }
  if (decision === "DENY" || decision === "DENIED") {
    return "deny";
  }
  return "approval";
}

type DecisionBadgeProps = {
  decision: AuditDecision;
};

export function DecisionBadge({ decision }: DecisionBadgeProps): ReactElement {
  return <Badge tone={toneForDecision(decision)}>{decision}</Badge>;
}
