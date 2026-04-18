#!/usr/bin/env python3
#
# "make format" for easy clang-format

import multiprocessing
import os
import shutil
import sys
import subprocess

extensions = (
    ".c", ".cc", ".cpp", ".cxx",
    ".h", ".hh", ".hpp", ".hxx",
    ".osl", ".glsl", ".cu", ".cl"
)

ignore_files = {
    "src/render/sobol.cpp",  # Too heavy for clang-format
}

def _find_clang_format():
    """Return the clang-format executable path.

    Search order:
    1. ``CLANG_FORMAT`` environment variable.
    2. ``clang-format`` on PATH.
    3. Versioned variants ``clang-format-18`` … ``clang-format-14``.
    """
    env_override = os.environ.get("CLANG_FORMAT")
    if env_override:
        return env_override

    candidate = shutil.which("clang-format")
    if candidate:
        return candidate

    for version in range(18, 13, -1):
        candidate = shutil.which(f"clang-format-{version}")
        if candidate:
            return candidate

    sys.stderr.write(
        "clang-format not found. Install it or set the CLANG_FORMAT "
        "environment variable to its full path.\n"
    )
    sys.exit(1)

def source_files_from_git(paths):
    cmd = ("git", "ls-tree", "-r", "HEAD", *paths, "--name-only", "-z")
    files = subprocess.check_output(cmd).split(b'\0')
    return [f.decode('ascii') for f in files]

def clang_format_file(files):
    cmd = [_find_clang_format(), "-i", "-verbose"] + files
    return subprocess.check_output(cmd, stderr=subprocess.STDOUT)

def clang_print_output(output):
    print(output.decode('utf8', errors='ignore').strip())

def clang_format(files):
    pool = multiprocessing.Pool()

    # Process in chunks to reduce overhead of starting processes.
    cpu_count = multiprocessing.cpu_count()
    chunk_size = min(max(len(files) // cpu_count // 2, 1), 32)
    for i in range(0, len(files), chunk_size):
        files_chunk = files[i:i+chunk_size];
        pool.apply_async(clang_format_file, args=[files_chunk], callback=clang_print_output)

    pool.close()
    pool.join()

def main():
    os.chdir(os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "..")))

    files = [
        f for f in source_files_from_git(["src"])
        if f.endswith(extensions)
        if f not in ignore_files
    ]

    clang_format(files)

if __name__ == "__main__":
    main()
