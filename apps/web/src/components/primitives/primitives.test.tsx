import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";

import { Badge } from "./badge";
import { Button } from "./button";
import { Card } from "./card";
import { Input } from "./input";
import { Table } from "./table";
import { DecisionBadge } from "../decision-badge/decision-badge";

afterEach(() => {
  cleanup();
});

describe("primitives", () => {
  it("renders a primary button", () => {
    render(<Button>Save</Button>);
    expect(screen.getByRole("button", { name: "Save" }).className).toContain("btn--primary");
  });

  it("renders input labels", () => {
    render(<Input label="Email" name="email" />);
    expect(screen.getByLabelText("Email")).toBeTruthy();
  });

  it("renders a table row", () => {
    render(
      <Table
        columns={[{ key: "name", header: "Name" }]}
        rows={[{ id: "1", name: "ops-bot" }]}
        getRowKey={(row: { id: string }) => row.id}
      />,
    );
    expect(screen.getByText("ops-bot")).toBeTruthy();
  });

  it("renders a card title", () => {
    render(<Card title="Agents">body</Card>);
    expect(screen.getByText("Agents")).toBeTruthy();
  });

  it("maps ALLOW to the reserved allow tone", () => {
    render(<DecisionBadge decision="ALLOW" />);
    expect(screen.getByText("ALLOW").className).toContain("badge--allow");
  });

  it("keeps decision colors off the default badge", () => {
    render(<Badge>active</Badge>);
    expect(screen.getByText("active").className).toContain("badge--neutral");
  });
});
