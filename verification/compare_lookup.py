import hashlib
import json
import statistics
import subprocess
import sys


def measure(binary):
    rows = {}
    for line in subprocess.check_output([binary], text=True).splitlines():
        case, ns, allocations, checksum = line.split()
        rows[case] = (float(ns), float(allocations), int(checksum))
    return rows


def main(baseline, candidate):
    paths = [baseline, candidate]
    transcripts = [subprocess.check_output([path, "compare"]) for path in paths]
    if transcripts[0] != transcripts[1]:
        raise ValueError("Path lookup or a public error message changed")
    print(f"Identical {len(transcripts[0].splitlines())} results: {hashlib.sha256(transcripts[0]).hexdigest()}")
    for path in paths:
        measure(path)
    samples = [[], []]
    for iteration in range(10):
        for index in ((0, 1) if iteration % 2 == 0 else (1, 0)):
            samples[index].append(measure(paths[index]))
    for case in samples[0][0]:
        medians = [statistics.median(row[case][0] for row in runs) for runs in samples]
        allocation_counts = [sorted({row[case][1] for row in runs}) for runs in samples]
        if len({row[case][2] for runs in samples for row in runs}) != 1:
            raise ValueError(f"Translation checksum mismatch for {case}")
        print(json.dumps({"case": case, "old_ns": medians[0], "new_ns": medians[1],
                          "allocations_per_translation": allocation_counts}))


if __name__ == "__main__":
    main(*sys.argv[1:])
