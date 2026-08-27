import { type FormEvent, type ReactElement, useState } from "react";

import { api } from "../../api/client";
import { writeSession } from "../../lib/auth-storage";
import { navigate } from "../../lib/router";
import { Button } from "../../components/primitives/button";
import { Card } from "../../components/primitives/card";
import { Input } from "../../components/primitives/input";

export function LoginPage(): ReactElement {
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [organizationName, setOrganizationName] = useState("");
    const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  async function onSubmit(event: FormEvent<HTMLFormElement>): Promise<void> {
    event.preventDefault();
    setSubmitting(true);
    setError(null);
    try {
      const response = await api.login({
        email,
        password,
        organization_name: organizationName.length > 0 ? organizationName : undefined,
      });
      writeSession({
        accessToken: response.access_token,
        email: response.email,
        organizationId: response.organization_id,
      });
      navigate("/");
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Unable to sign in");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="auth">
      <Card title="Sign in">
        <form className="form" onSubmit={(event) => void onSubmit(event)}>
          <Input
            label="Email"
            name="email"
            type="email"
            autoComplete="email"
            required
            value={email}
            onChange={(event) => {
              setEmail(event.target.value);
            }}
          />
          <Input
            label="Password"
            name="password"
            type="password"
            autoComplete="current-password"
            required
            value={password}
            onChange={(event) => {
              setPassword(event.target.value);
              }}
          />
          <Input
            label="Organization name"
            name="organizationName"
            autoComplete="organization"
            value={organizationName}
            onChange={(event) => {
              setOrganizationName(event.target.value);
            }}
          />
          {error !== null ? <p className="field__error">{error}</p> : null}
          <div className="form__actions">
            <Button type="submit" disabled={submitting}>
              {submitting ? "Signing in…" : "Sign in"}
            </Button>
            <Button
              variant="ghost"
              onClick={() => {
                navigate("/signup");
              }}
            >
              Create organization
            </Button>
          </div>
        </form>
      </Card>
    </div>
  );
}
