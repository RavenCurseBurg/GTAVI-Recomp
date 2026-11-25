# Documentation

| Document | Purpose |
| --- | --- |
| [build.md](build.md) | Prerequisites, build commands, test commands, project layout |
| [testing-anyps5.md](testing-anyps5.md) | Run the pinned filesystem, audio and controller tests with synthetic inputs |
| [adr/0003-build-on-anyps5-relinker.md](adr/0003-build-on-anyps5-relinker.md) | **Accepted:** build on AnyPS5's relinker and system libraries |
| [adr/0002-ps5-to-pc-library-translation.md](adr/0002-ps5-to-pc-library-translation.md) | Superseded: library translation with this project's own runtime loader |
| [adr/0001-project-scope.md](adr/0001-project-scope.md) | Superseded: earlier translation-vs-recompilation framing |
| [research/phase-1-research-report.md](research/phase-1-research-report.md) | Phase 1 research findings and evidence standard |
| [research/related-projects.md](research/related-projects.md) | Related projects (AnyPS5, americas-recomp, Leonida), their licences and what may be reused |
| [community/discord.md](community/discord.md) | Discord server layout, roles, rules, welcome message, FAQ and update webhooks |
| [research/limitations-and-risks.md](research/limitations-and-risks.md) | What stands between the project and GTA VI running, from AnyPS5's code and docs |

## Conventions

- **Architecture decisions** are recorded as ADRs in `adr/`, numbered
  sequentially. An ADR is never edited to change its decision; supersede it with
  a new one.
- **Research** lives in `research/` and follows the evidence standard defined in
  the Phase 1 report. Confirmed findings must be reproducible.
- **Nothing in this directory may contain game files, assets, PS5 system files,
  decryption keys, or leaked material.**
