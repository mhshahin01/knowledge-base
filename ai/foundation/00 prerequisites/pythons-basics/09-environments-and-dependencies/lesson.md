# Chunk 09: Environments and Dependencies

## Goal

By the end of this chunk, you will be able to:

- explain why virtual environments are useful;
- create and activate a virtual environment;
- install packages with `pip`;
- recreate dependencies from `requirements.txt`;
- check which Python and package versions are running.

## 1. Projects need isolated environments

A **dependency** is code your project uses but does not define itself. Pydantic and Pydantic AI are dependencies for later chunks.

Different projects may need different dependency versions. A **virtual environment** gives one project its own Python executable and installed packages. The usual folder name is `.venv`.

Open PowerShell in the course root and create the environment:

```powershell
py -m venv .venv
```

This creates files; it does not activate the environment yet.

Virtual environments are disposable and should not contain your own project code. The course's `.gitignore` excludes `.venv` from version control.

## 2. Activating the environment

Activation makes `python` and `pip` point to the environment in the current terminal:

```powershell
.venv\Scripts\Activate.ps1
```

Your prompt normally begins with `(.venv)` afterward. Confirm the interpreter:

```powershell
python --version
python 09-environments-and-dependencies/examples/01_environment_info.py
```

The first example displays the Python version, whether an environment is active, and the current executable path. The exact path will differ by computer.

Run [01_environment_info.py](examples/01_environment_info.py).

Look for:

```text
Python: 3.14.x
Virtual environment: True
Executable: ...\.venv\Scripts\python.exe
```

Activation is optional. You can always target the environment directly:

```powershell
.venv\Scripts\python.exe 09-environments-and-dependencies/examples/01_environment_info.py
```

## 3. Installing dependencies

Use `python -m pip` so the selected Python interpreter performs the installation. The course root contains a `requirements.txt` file with versions tested together.

After activation, install them:

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

`-r` tells `pip` to read package requirements from the file.

Exact versions use `==`, such as `pydantic==2.13.5`. Pinning versions makes installation repeatable. When deliberately upgrading, update the versions and rerun all affected examples.

## 4. Distribution names and import names

The name installed by `pip` can differ from the name imported by Python:

| Installed distribution | Python import |
|---|---|
| `pydantic` | `pydantic` |
| `pydantic-ai` | `pydantic_ai` |
| `httpx` | `httpx` |

The next example asks Python's package metadata for each installed distribution's version.

Run [02_dependency_versions.py](examples/02_dependency_versions.py) after installation.

Expected output:

```text
pydantic: 2.13.5
pydantic-ai: 2.39.0
httpx: 0.28.1
```

## 5. Leaving and recreating an environment

Leave the activated environment with:

```powershell
deactivate
```

Do not move or copy a `.venv` folder to a new location because its internal paths may no longer work. Recreate it there from `requirements.txt` instead.

When you run a command, verify these three things if behavior is surprising:

1. Which Python executable is running?
2. Is the intended environment active?
3. Is the needed package installed in that environment?

## Practice

1. Create `.venv` in the course root.
2. Activate it.
3. Install `requirements.txt`.
4. Run both examples.
5. Deactivate it.
6. Run `01_environment_info.py` again and observe what changed.

### Optional challenge

Without activating the environment, use `.venv\Scripts\python.exe` to run `02_dependency_versions.py`.

## Check your understanding

1. Why does each project benefit from its own environment?
2. Does activating an environment create it?
3. Why use `python -m pip`?
4. What does `==` mean in `requirements.txt`?
5. Should a virtual environment be moved with the project?

Answers: (1) to isolate dependency versions; (2) no; (3) it installs with the chosen interpreter; (4) install that exact version; (5) no, recreate it from dependency records.

## You are ready for Chunk 10 when...

You can create an environment, install `requirements.txt`, and identify the Python executable that runs your code.

Official reference: [Python virtual environments](https://docs.python.org/3.14/library/venv.html).
