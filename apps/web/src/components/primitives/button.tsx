import type { ButtonHTMLAttributes, ReactElement, ReactNode } from "react";

type ButtonVariant = "primary" | "secondary" | "danger" | "ghost";

type ButtonProps = {
  children: ReactNode;
  variant?: ButtonVariant;
} & ButtonHTMLAttributes<HTMLButtonElement>;

export function Button({
  children,
  variant = "primary",
  type = "button",
  className,
  ...props
}: ButtonProps): ReactElement {
  const classes = ["btn", `btn--${variant}`, className].filter(Boolean).join(" ");
  return (
    <button className={classes} type={type} {...props}>
      {children}
    </button>
  );
}
