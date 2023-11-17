# TODO

## MVP

### Goals

    In the beginning only support `cmd`

### Non goals

    ...

### Tasks

#001 Variables

- [ ] Read variable with below requirements:

  - lower/upper case letters and underscores, optional numbers after first char.
    - Cannot be underscores only
    - Cannot have hyphens
  - equals sign
    - in the future can support `:=`
  - rhs, any non-whitespace char
    - except %
    - < len 1000

- [ ] Read `shell` as special variable

#002 Production labels with below requirements

- lowercase letters and underscores or hyphens, optional numbers after first char.
  - No leading/trailing underscores
  - No subsequent underscores and hyphens
- optional `/` separator to define shortcut. Example: `s/string`
- labels end with `::`
