# ADR 0001: Fresh repo bootstrap for TrustLayer

## Context

The workspace already contained unrelated files and an unrelated application structure.

## Decision

Create a fresh `trustlayer/` directory that exactly follows the repository structure in the TrustLayer build spec instead of retrofitting an unrelated codebase.

## Consequences

The build stays aligned with the spec and avoids mixing concerns from an existing project.
