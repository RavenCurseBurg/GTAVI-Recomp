# ADR 0003: Build on AnyPS5's relinker and system libraries

- **Status:** Accepted
- **Date:** 2026-11-21
- **Deciders:** project maintainer
- **Supersedes:** [ADR 0002](0002-ps5-to-pc-library-translation.md)
- **Related:** `README.md`, `TODO.md`, `third_party/AnyPS5`,
  [AnyPS5 architecture](https://github.com/boykopovar/AnyPS5/blob/15826135019b8c7de27f42661a850a1dd9750932/docs/dev/ARCHITECTURE.md)

## Context

ADR 0002 chose library-level translation and planned for this project to write
its own loader, which would resolve the game's imports while it runs and send
them to libraries this project implements.

Since then, the project has reviewed [AnyPS5](https://github.com/boykopovar/AnyPS5),
an open-source project that already does this for PS5 titles in general:

- Its **relinker** converts a PS5 executable ahead of time into a native Linux
  ELF or Windows PE program. Imports are bound by NID, the hash PS5 executables
  use to name system functions, through the host's own dynamic loader. Nothing is
  intercepted at run time and nothing is emulated.
- It implements **413 system libraries** as host shared libraries. At the pinned
  commit, AnyPS5's own tool counts 17,749 of 39,253 declared functions as
  implemented.
- Its **shader recompiler** translates PS5 GPU shaders to SPIR-V for Vulkan. It
  handles every RDNA 2 reference instruction form, and 1,484 of 1,560 forms in
  the gfx1013 reference.
- It is licensed **GPL-2.0-only**, has its own test suites, and builds for Windows
  (MinGW-w64 GCC) and Linux.

Writing a separate loader and library set would repeat years of work that
AnyPS5 already has. The model that fits this project is the one bbport used for
Bloodborne: a runtime for one game, built on an existing general project, that
adds only what that game needs.

## Decision

1. **AnyPS5 is the translation layer.** The project uses AnyPS5's relinker,
   system libraries and shader recompiler, pinned as a git submodule at
   `third_party/AnyPS5`. The runtime loader and dispatch table that ADR 0002
   planned will not be written.
2. **General work goes upstream; GTA VI work stays here.** A fix or library
   implementation that any PS5 title could use is contributed to AnyPS5. This
   repository holds what is specific to GTA VI: its compatibility notes and
   research, game patch files in AnyPS5's patch format, configuration, test
   procedures, and progress tracking.
3. **License.** The project is GPL-2.0-only to match AnyPS5, whose code it uses.
   Code under incompatible licences, including GPLv3-only code, is not accepted.
4. **Users supply their own game.** AnyPS5's relinker needs an extracted,
   decrypted executable. The project does not provide, link to, or explain how
   to obtain decryption tools, keys or game files.
5. **Converted executables are never distributed.** A relinked GTA VI executable
   is derived from the game. It is produced on the user's own machine and is
   never committed, published or shared by the project.
6. **The repository's content rules from ADR 0002 stand.** It never contains
   Sony code, SDK material, system files, decryption keys, entitlements, game
   content, or extracted assets.

## What this implies

- **No loader or dispatch code here.** `src/loader/` and `src/libraries/`, which
  ADR 0002 planned, are dropped.
- **Two toolchains.** AnyPS5 builds with MinGW-w64 GCC on Windows. The MSVC build
  in this repository covers only this repository's own code.
- **The existing scaffolding is off the runtime path.** `gtavi/error.h`,
  `gtavi/log.h`, `gtavi/path.h` and `gtavi-probe` remain and their tests still
  run, but the game never calls them. Whether to keep them as project tooling or
  retire them is left open.
- **Updating AnyPS5 is a deliberate step.** The submodule is bumped on purpose,
  then the AnyPS5 progress numbers are re-measured
  (`scripts/update_progress.py --refresh-anyps5`).
- **The roadmap credits AnyPS5.** `TODO.md` checks items AnyPS5 provides and
  names where they live. A checked AnyPS5 item means it exists and is tested
  there, not that it works with GTA VI.

## Answers to ADR 0002's open questions

1. **Container format, and whether loading needs keys.** PS5 executables are ELF
   files, usually wrapped in SELF containers. AnyPS5 handles both, but only
   after decryption. Loading is not possible without material the project
   cannot legitimately obtain, so it relies on users supplying their own
   decrypted executable (decision 4).
2. **Graphics path.** The low-level AGC command stream is translated to Vulkan,
   and shaders are recompiled to SPIR-V (AnyPS5 `libSceAgcDriver` and
   `core/shader/recompiler`).
3. **Which host first.** Both. AnyPS5 targets Windows and Linux from one codebase.
4. **How much guest OS behaviour the host can provide.** AnyPS5 implements guest
   memory, threading and file behaviour in its `libkernel` on top of host APIs.
   It documents where the console's behaviour has not been measured, for
   example the register state at the main-module entry point.
5. **Minimum library set for a first frame.** Still unknown. Answering it needs
   GTA VI's import list, which needs the game files.

## Consequences

**Positive**

- The project starts from a working relinker, 413 libraries and a shader
  recompiler instead of from nothing.
- Fixes made for GTA VI that apply to all PS5 titles help AnyPS5's other users,
  and their fixes help GTA VI.
- This repository stays small and focused on one game.

**Negative**

- The project depends on AnyPS5's direction, pace and code review. A change
  GTA VI needs may wait on upstream.
- GPL-2.0-only rules out code from projects under incompatible licences.
- Contributors who build the runtime need a second toolchain (MinGW-w64).
- Every finding about GTA VI's actual behaviour still waits on lawful access to
  the game files.

**Neutral**

- The research and progress work done so far carries over unchanged.

## Follow-ups

- [ ] Build AnyPS5 locally and in CI at the pinned commit.
- [ ] Read AnyPS5's `CONTRIBUTING.md` and conventions before the first upstream
      pull request.
- [ ] Decide whether to keep the `gtavi` scaffolding as tooling or retire it.
- [ ] Once GTA VI files can be researched lawfully: enumerate its imports and map
      them to AnyPS5's libraries.
