# **Project manager**

Package to list and manage available projects.

## Installation

Check the [repository tags](https://github.com/stanislavsabev/pm/tags) for latest version

```shell
pip install git+https://github.com/stanislavsabev/pm.git@v0.1.2
```


## Usage

Run `pm init` to create default configuration and database.

```sh
$ pm --help
Usage: pm [-h] COMMAND [FLAGS] PROJECT [WORKTREE]
  Calling `pm` without args, lists managed projects.

  Commands
        ls      List projects / project worktrees, [-a] for all
        cd      Navigate to project
      open      Open project
       add      Add managed project
      init      Init pm

  -h --help     Show this message and exit.
  -V --version  Show package version
```

```sh
$ pm ls -h
Usage: ls [FLAGS] [PROJECT [WORKTREE]]
  List projects.
  If PROJECT is defined, list worktrees / branches

  PROJECT       Optional project name
  WORKTREE      Optional worktree or folder name

  -h --help     Show this message and exit.
  -a --all      List all projects, including non-managed.
                  If PROJECT, list all worktrees / branches, including remote.

$ pm
> Projects:
--------------------------------------------------------
wake wake         b *main variables         
  qs qspreadsheet b *main v1                
 dot .dotfiles      *main                   
  pm pm           b commands-to-flags develop fix-add
                    *main                   
  vb vba-parser   b *main                   
--------------------------------------------------------
```
