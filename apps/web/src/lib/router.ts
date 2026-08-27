export type AppRoute =
  | { name: "login" }
  | { name: "signup" }
  | { name: "dashboard" }
  | { name: "agents" }
  | { name: "agent-detail"; id: string }
  | { name: "policies" }
  | { name: "policy-editor" }
  | { name: "approvals" }
  | { name: "audit" }
  | { name: "not-found" };

export function parsePath(pathname: string): AppRoute {
  const path = pathname.replace(/\/+$/, "") || "/";
  if (path === "/login") {
    return { name: "login" };
  }
  if (path === "/signup") {
    return { name: "signup" };
  }
  if (path === "/" || path === "/dashboard") {
    return { name: "dashboard" };
  }
  if (path === "/agents") {
    return { name: "agents" };
  }
  const agentMatch = /^\/agents\/([^/]+)$/.exec(path);
  if (agentMatch !== null) {
    return { name: "agent-detail", id: decodeURIComponent(agentMatch[1]) };
  }
  if (path === "/policies") {
    return { name: "policies" };
  }
  if (path === "/policies/new") {
    return { name: "policy-editor" };
  }
  if (path === "/approvals") {
    return { name: "approvals" };
  }
  if (path === "/audit") {
    return { name: "audit" };
  }
  return { name: "not-found" };
}

export function toPath(route: AppRoute): string {
  switch (route.name) {
    case "login":
      return "/login";
    case "signup":
      return "/signup";
    case "dashboard":
      return "/";
    case "agents":
      return "/agents";
    case "agent-detail":
      return `/agents/${encodeURIComponent(route.id)}`;
    case "policies":
      return "/policies";
    case "policy-editor":
      return "/policies/new";
    case "approvals":
      return "/approvals";
    case "audit":
      return "/audit";
    case "not-found":
      return "/404";
  }
}

export function navigate(path: string): void {
  window.history.pushState({}, "", path);
  window.dispatchEvent(new PopStateEvent("popstate"));
}

export function titleForRoute(route: AppRoute): string {
  switch (route.name) {
    case "login":
      return "Sign in";
    case "signup":
      return "Create organization";
    case "dashboard":
      return "Overview";
    case "agents":
      return "Agents";
    case "agent-detail":
      return "Agent";
    case "policies":
      return "Policies";
    case "policy-editor":
      return "New policy";
    case "approvals":
      return "Approvals";
    case "audit":
      return "Audit log";
    case "not-found":
      return "Not found";
  }
}
