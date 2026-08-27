import { type FormEvent, type ReactElement, useState } from "react";

import { api } from "../../api/client";
import { writeSession } from "../../lib/auth-storage";
import { navigate } from "../../lib/router";
import { Button } from "../../components/primitives/button";
import { Card } from "../../components/primitives/card";
import { Input } from "../../components/primitives/input";

export function SignupPage(): ReactElement {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  async function onSubmit(event: FormEvent<HTMLFormElement>): Promise<void> {
    event.preventDefault();
    if (password.length < 12) {
      setError("password must be at least 12 characters");
      return;
    }
    setSubmitting(true);
    setError(null);
    try {
      const response = await api.signup({ name, email, password });
      writeSession({
        accessToken: response.access_token,
        email: response.email,
        organizationId: response.organization_id,
      });
      navigate("/");
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Unable to create organization");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="auth">
      <Card title="Create organization">
        <form className="form" onSubmit={(event) => void onSubmit(event)}>
          <Input
            label="Organization name"
            name="name"
            required
            value={name}
            onChange={(event) => {
              setName(event.target.value);
            }}
          />
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
            autoComplete="new-password"
            minLength={12}
            required
            value={password}
            onChange={(event) => {
              setPassword(event.target.value);
            }}
          />
          {error !== null ? <p className="field__error">{error}</p> : null}
          <div className="form__actions">
            <Button type="submit" disabled={submitting}>
              {submitting ? "Creating…" : "Create and sign in"}
            </Button>
            <Button
              variant="ghost"
              onClick={() => {
                navigate("/login");
              }}
            >
              Already have an account
            </Button>
          </div>
        </form>
      </Card>
    </div>
  );
}
