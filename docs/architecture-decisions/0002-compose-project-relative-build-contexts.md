# 0002 - Resolve Compose build contexts from the project directory

Docker Compose resolves relative build contexts from the supplied project directory in this local workflow. The API and web contexts therefore use `./apps/...`, keeping the one-command startup reliable from the repository root.
