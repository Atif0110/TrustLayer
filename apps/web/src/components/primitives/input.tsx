import type { InputHTMLAttributes, ReactElement } from "react";

type InputProps = {
  label: string;
  error?: string;
} & InputHTMLAttributes<HTMLInputElement>;

export function Input({ label, error, id, className, ...props }: InputProps): ReactElement {
  const inputId = id ?? props.name;
  return (
    <label className="field" htmlFor={inputId}>
      <span className="field__label">{label}</span>
      <input id={inputId} className={["input", className].filter(Boolean).join(" ")} {...props} />
      {error !== undefined ? <span className="field__error">{error}</span> : null}
    </label>
  );
}
