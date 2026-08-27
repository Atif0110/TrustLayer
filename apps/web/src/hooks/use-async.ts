import { useEffect, useRef, useState } from "react";

import { ApiError } from "../api/client";

export type AsyncState<T> =
  | { status: "loading" }
  | { status: "error"; message: string }
  | { status: "ready"; data: T };

export function useAsync<T>(loader: () => Promise<T>, deps: ReadonlyArray<unknown>): {
  state: AsyncState<T>;
  reload: () => void;
} {
  const [nonce, setNonce] = useState(0);
  const [state, setState] = useState<AsyncState<T>>({ status: "loading" });
  const loaderRef = useRef(loader);
  loaderRef.current = loader;

  useEffect(() => {
    let cancelled = false;
    setState({ status: "loading" });
    loaderRef
      .current()
      .then((data) => {
        if (!cancelled) {
          setState({ status: "ready", data });
        }
      })
      .catch((error: unknown) => {
        if (cancelled) {
          return;
        }
        const message = error instanceof ApiError ? error.message : "Unable to load data";
        setState({ status: "error", message });
      });
    return () => {
      cancelled = true;
    };
  }, [...deps, nonce]);

  return {
    state,
    reload: () => {
      setNonce((value) => value + 1);
    },
  };
}
