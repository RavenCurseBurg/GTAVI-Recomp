# Project Roadmap

This document tracks the development of the GTA VI Translation Layer, from
initial research and technical investigation through implementation, testing, and
release.

Tasks will be updated as development progresses.

An item is checked only when the implementation is committed and its tests
pass, either in this repository or in [AnyPS5](https://github.com/boykopovar/AnyPS5)
at the pinned submodule commit. Items AnyPS5 provides say so and name where.
Checking an AnyPS5 item means it exists and is tested there, not that it has
been shown to work with GTA VI. See [docs/build.md](docs/build.md) for building
and running this repository's test suite.

Items marked *(needs game files)* cannot start until GTA VI files can be
researched lawfully (see the README). Until then, work proceeds from public
research and from AnyPS5. Work that is not specific to GTA VI belongs upstream
in AnyPS5. The README's progress section and the
[progress page](https://jamescicada.github.io/GTAVI-Recomp/) are generated from
this file by `scripts/update_progress.py`; run it after changing a checkbox.
After updating the AnyPS5 submodule, run it with `--refresh-anyps5` to
re-measure AnyPS5's shader and library numbers.

## Phase 1: Research & Feasibility

Understand the PS5 build's requirements and determine what the translation layer
must provide. See [docs/research/phase-1-research-report.md](docs/research/phase-1-research-report.md)
for the evidence standard and the report itself.

### Guest Architecture Research

- [x] Identify the PS5 executable container and module format. (AnyPS5: ELF and
      SELF handling in `core/relinker`, `tools/unwrap_self.py`)
- [ ] Confirm the console's register contract at the main-module entry point.
      (AnyPS5 documents its host entry stubs but notes the console contract is
      not measured; `docs/dev/ARCHITECTURE.md`)
- [ ] Enumerate imported libraries and symbols. *(needs game files)*
- [ ] Identify lazily loaded libraries that a static import table does not show. *(needs game files)*
- [x] Research guest memory layout and allocation behaviour. (AnyPS5: allocators
      in `docs/dev/ARCHITECTURE.md`, `libkernel/DirectMemory`)
- [x] Research threading, scheduling, and synchronisation behaviour. (AnyPS5:
      `libkernel/Pthread`)
- [x] Research filesystem layout and mount-point semantics. (AnyPS5: `libkernel/File`)
- [x] Research graphics requirements (command buffers, shaders, synchronisation).
      (AnyPS5: `libSceAgcDriver`, `core/shader/recompiler`)
- [x] Research audio output requirements. (AnyPS5: `libSceAudioOut`)
- [x] Research input device requirements. (AnyPS5: `libScePad`)
- [ ] Identify the PSN and online calls GTA VI makes at startup even without an
      online mode, so they can report "not available". *(needs game files)*
- [ ] Investigate protection, encryption, and entitlement requirements. *(needs game files)*
- [ ] Identify potential compatibility obstacles. *(needs game files)*

### Host & Translation Research

- [ ] Map each imported library to its AnyPS5 implementation and list the gaps. *(needs game files)*
- [x] Review publicly documented behaviour of comparable translation projects for
      findings. Do not copy code unless its licence permits it. (AnyPS5 adopted,
      GPL-2.0-only; see the README)
- [x] Review AnyPS5's technical-debt list (`docs/dev/TechnicalDebt.md`) for
      behaviour that cannot yet be translated faithfully.
      (`docs/research/limitations-and-risks.md`)
- [x] Evaluate graphics translation targets (Vulkan, Direct3D 12). (AnyPS5: Vulkan,
      shaders compiled to SPIR-V)
- [x] Evaluate Windows and Linux host capability differences. (AnyPS5: separate
      Windows and Linux allocators and entry stubs)

### Technical Feasibility

- [ ] Determine the minimum library set required to reach a first frame. *(needs game files)*
- [x] Establish whether loading is possible without prohibited material. (No:
      AnyPS5's relinker needs an extracted, decrypted executable;
      `docs/user/USAGE.md`)
- [x] Document technical limitations and risks. (`docs/research/limitations-and-risks.md`)
- [x] Produce the initial research report. (`docs/research/phase-1-research-report.md`;
      GTA VI-specific sections remain blocked)

## Phase 2: Architecture & Design

Define the project's architecture before implementing the core components.

- [x] Record the move to AnyPS5's relinker in a new ADR, replacing the
      runtime-loader design in ADR 0002. (ADR 0003)
- [x] Define the loader interface and entry contract. (AnyPS5: relinker and entry
      stubs, `docs/dev/ARCHITECTURE.md`)
- [x] Define the library dispatch interface. (AnyPS5: exports renamed to NIDs and
      bound by the host OS loader, `core/libs/nid`)
- [x] Design guest mount-point translation. (AnyPS5: `libkernel/File`)
- [x] Design the graphics translation subsystem. (AnyPS5: `libSceAgcDriver` on Vulkan)
- [x] Design the audio subsystem. (AnyPS5: `libSceAudioOut` on SDL2)
- [x] Design the input subsystem. (AnyPS5: `libScePad` on SDL2, `docs/user/INPUT_MAPPING.md`)
- [x] Design the memory and threading compatibility layer. (AnyPS5: `libkernel`)
- [x] Define error handling and logging standards. (`gtavi/error.h`, `gtavi/log.h`)
- [x] Establish cross-platform coding conventions. (`.clang-format`, `.editorconfig`)
- [x] Select supported C++ standard. (C++20)
- [x] Configure CMake build system.
- [x] Document architectural decisions. (ADR 0003, accepted; supersedes ADR 0002)

## Phase 3: Development Environment

Prepare the development infrastructure.

- [x] Set up the CMake project structure.
- [x] Configure Windows development builds. (MSVC 19.51, verified locally)
- [x] Configure Linux development builds. (CI: GCC and Clang)
- [x] Set up automated compilation.
- [ ] Configure static analysis and formatting. (formatting configured; static analysis pending)
- [x] Integrate unit testing. (`tests/`, CTest, 53 cases)
- [x] Configure CI workflows. (`.github/workflows/ci.yml`)
- [x] Establish debugging and diagnostic tooling. (`gtavi-probe`)
- [x] Create development documentation. (`docs/build.md`)
- [ ] Build AnyPS5 locally (Windows needs the MinGW-w64 GCC toolchain;
      `third_party/AnyPS5/docs/dev/BUILD.md`).
- [x] Build AnyPS5 at the pinned commit in CI. (CI job `anyps5`: relinker-only
      mode with its test suite, `third_party/AnyPS5/docs/dev/BUILD.md`)

## Phase 4: Core Implementation

Implement the foundational translation layer.

### Core Runtime

- [x] Implement the loader. (AnyPS5: `core/relinker`)
- [x] Implement import resolution and the dispatch table. (AnyPS5: NID binding,
      `core/libs/nid`)
- [x] Implement module initialization and shutdown. (AnyPS5: deferred module
      start through `sceKernelLoadStartModule`)
- [x] Implement configuration management. (AnyPS5: environment variables,
      `anyps5-input.ini`)
- [x] Implement structured logging. (`gtavi/log.h`)
- [x] Implement error handling. (`gtavi/error.h`)
- [x] Implement runtime diagnostics. (`gtavi-probe`)

### Filesystem

- [x] Implement the guest filesystem abstraction. (AnyPS5: `libkernel/File`)
- [x] Implement `/app0` mount-point mapping. (AnyPS5: `libkernel/File`)
- [ ] Confirm which other mount points GTA VI uses (`/data`, `/savedata0`, ...)
      and that AnyPS5 maps them. *(needs game files)*
- [x] Implement host path translation. (`gtavi/path.h`, host-side only)
- [x] Handle host drive letters and mount points. (`DriveMap`, C: -> /mnt/c)
- [x] Implement file access compatibility. (AnyPS5: `libkernel/File`)
- [x] Implement directory and metadata handling. (AnyPS5:
      `libkernel/File/src/DirectoryDescriptor.cpp`)
- [ ] Handle permissions and access control differences.
- [x] Implement file operation testing. ([AnyPS5 `libkernel` tests](docs/testing-anyps5.md#filesystem)
      cover filesystem operations, timestamps, vectored I/O, mounts and Windows file locks.)

### Memory & Processes

- [x] Research and implement required memory compatibility mechanisms. (AnyPS5:
      Windows, macOS and Linux allocators)
- [x] Investigate virtual memory behaviour differences. (AnyPS5:
      `docs/dev/ARCHITECTURE.md`)
- [x] Implement process and thread management interfaces. (AnyPS5: `libkernel`)
- [x] Handle thread creation and synchronisation. (AnyPS5: `libkernel/Pthread`)
- [x] Implement required runtime compatibility mechanisms. (AnyPS5: relinker
      `--to-intel` lowers AMD-only instructions)

### Translated Libraries

- [x] Implement the library module template and registration. (AnyPS5:
      `core/libs/prx`, 413 libraries)
- [ ] Implement the highest-priority libraries from the import table. *(needs game files)*
- [x] Add per-library tests. (AnyPS5: a `tests/` directory per library)
- [ ] Fill the gaps in core libraries nearly every PS5 game uses, upstream in
      AnyPS5: user service (44/695 functions), system service (144/617), save
      data (58/119), display output (78/290). Current numbers are on the progress page.

## Phase 5: Host Platform Compatibility

Implement host-specific integrations and the dispatch mechanism.

### Windows

- [x] Implement Windows platform detection. (`gtavi/platform.h`)
- [x] Implement Windows-specific host interfaces. (AnyPS5: Windows PE output and
      host libraries)
- [x] Establish Windows build and testing pipeline. (CI: MSVC)
- [ ] Verify behaviour against native Windows APIs.

### Linux

- [x] Implement Linux platform detection. (`gtavi/platform.h`)
- [x] Implement POSIX host interfaces. (AnyPS5: Linux ELF output and host libraries)
- [x] Implement Linux-specific system integrations. (AnyPS5: audio and input
      through SDL2, graphics through Vulkan)
- [x] Establish Linux build and testing pipeline. (CI: GCC, Clang)
- [ ] Verify behaviour against native Linux interfaces.

### Library Dispatch

- [ ] Implement symbol resolution with clear errors for missing imports.
- [x] Implement stub reporting for unimplemented symbols. (AnyPS5:
      `NotImplemented_nid_no_patch` stubs)
- [x] Test dispatch against a table-driven harness. (AnyPS5: relinker test suite)

## Phase 6: Graphics, Audio & Input

Implement the guest's major subsystems.

### Graphics

- [x] Identify the command buffer and shader formats. (AnyPS5: APR and AMM
      command buffers, RDNA decoder)
- [x] Prototype command-stream translation. (AnyPS5: `libSceAgcDriver`)
- [x] Evaluate translation targets (Vulkan, Direct3D 12). (AnyPS5: Vulkan)
- [x] Translate GPU shaders. (AnyPS5: `core/shader/recompiler`, every RDNA 2
      reference instruction form)
- [ ] Translate the remaining gfx1013 reference instruction forms (1,484/1,560)
      and reduce the recompiler's unsupported cases.
- [ ] Complete the graphics driver (AnyPS5 `libSceAgcDriver`: 97/167 functions).
- [ ] Test rendering correctness.
- [ ] Investigate performance overhead.

### Audio

- [x] Identify audio output requirements. (AnyPS5: `libSceAudioOut`)
- [x] Implement basic audio output for Windows and Linux hosts. (AnyPS5:
      `libSceAudioOut` on SDL2)
- [ ] Complete the audio output library (78/219 functions).
- [x] Test device handling and format conversion. ([AnyPS5 audio fixtures](docs/testing-anyps5.md#audio-output)
      exercise simulated endpoints, PCM formats and Linux resampling.)

### Input

- [x] Implement basic controller input. (AnyPS5: `libScePad` on SDL2, with
      keyboard and mouse mapping)
- [ ] Complete the controller library (56/222 functions).
- [ ] Implement haptics and adaptive triggers where feasible. (AnyPS5 has rumble;
      adaptive triggers unverified)
- [x] Test input behaviour. ([AnyPS5 controller fixtures](docs/testing-anyps5.md#controller-input)
      exercise command files, scripted input and recorded controller state.)

## Phase 7: Integration & Compatibility

Bring the individual components together.

- [x] Integrate the translation subsystems. (AnyPS5)
- [x] Implement runtime initialization. (AnyPS5: entry stubs and module start-up)
- [ ] Implement dependency detection.
- [ ] Establish a game installation detection mechanism. *(needs game files)*
- [x] Implement diagnostic reporting. (AnyPS5: `anyps5-report.json` run report)
- [ ] Test individual subsystems against the guest. *(needs game files)*
- [ ] Test game startup. *(needs game files)*
- [ ] Investigate and resolve compatibility failures. *(needs game files)*
- [ ] Document known limitations.

## Phase 8: Testing & Optimization

Ensure correctness, stability, and acceptable performance.

- [ ] Expand unit test coverage.
- [ ] Add integration tests.
- [ ] Add regression tests.
- [ ] Test supported Windows versions.
- [ ] Test supported Linux distributions.
- [ ] Investigate memory leaks.
- [ ] Profile CPU and memory usage.
- [ ] Profile translation overhead. *(needs game files)*
- [ ] Optimize performance bottlenecks.
- [ ] Test long-running stability. *(needs game files)*
- [ ] Document hardware and software requirements.

## Phase 9: Documentation & Release Preparation

Prepare the project for public use.

- [ ] Write installation documentation.
- [ ] Write configuration documentation.
- [ ] Document supported platforms.
- [ ] Document known limitations.
- [ ] Publish build instructions.
- [ ] Finalize contribution guidelines.
- [x] Finalize licensing. (GPL-2.0-only, `LICENSE`, matching AnyPS5)
- [ ] Prepare release binaries where appropriate.
- [ ] Establish versioning conventions.
- [ ] Create release notes.
- [ ] Prepare the first public release.

## Phase 10: Post-Release Development

Continue improving compatibility and supporting contributors.

- [ ] Collect community bug reports.
- [ ] Investigate compatibility reports.
- [ ] Expand library coverage.
- [ ] Improve hardware compatibility.
- [ ] Address performance issues.
- [ ] Expand automated testing.
- [ ] Maintain compatibility documentation.
- [ ] Review and prioritize community contributions.

---

## Development Principles

1. Research before implementing undocumented behavior.
2. Prioritize correctness and stability over premature optimization.
3. Keep platform-specific code isolated.
4. Avoid unnecessary dependencies.
5. Prefer existing, well-tested compatibility technologies where appropriate.
6. Document technical decisions and implementation limitations.
7. Never claim compatibility without reproducible testing.
8. Never bypass protection mechanisms. If running the guest requires material the
   project cannot legitimately obtain, document the limitation instead.

**Note:** This roadmap is a development plan, not a statement that every listed capability is currently feasible or implemented. Tasks may be revised as research reveals the actual requirements.
