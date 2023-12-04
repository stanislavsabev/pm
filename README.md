# **Project manager**

List and manage available projects.

## installation

```shell
> pip install git+https://github.com/stanislavsabev/pm.git@main
```

## Usage

First execution will create default configuration file and database file.

```shell
$ pm --help

    Usage: pm [-h] COMMAND [FLAGS] PROJECT [WORKTREE]

    Calling `pm`
      > without args, lists managed projects (`ls` command).
      > with project [worktree], opens a project (`open` command).

    Commands
           ls        List managed projects, [-a] for all
           cd        Navigate to project
         open        Open project
          add        Add managed project

    Flags
    -h --help        Show this message and exit.

```

```shell
$ pm ls -h

    Usage: pm ls [FLAGS]

    List projects

    Flags
    -a --all        List all projects, including from PROJECTS_DIR
    -h --help        Show this message and exit.

$ pm

> Projects:

     dot | .dotfiles                : (*main)
      pm | pm                       : (*main) (own-argparse)
      qs | qspreadsheet             : (*main) (v1)
    wake | wake                     : (*main) (testing)
```