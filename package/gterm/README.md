GTerm - A Special Purpose Terminal Emulator
===========================================

GTerm is a fairly simple terminal emulator written in Python for
a very specific purpose: to provide a decent environment for using
the GPLOT program and APL running on simulated CDC Cyber computers
under the NOS 2.8.7 operating system.

The intended audience for this software is very small ...

Features
--------

- Provides colour vector graphics for GPLOT.
- Vector graphics can be saved in SVG format.
- Zooming into the displayed graphics is supported.
- Supports the APL character set used by CDC APL 2.
- APL character input is via a virtual keyboard with key hints.
- Provides local command line recall and editing.
- Command line editing works with APL symbols too. This makes
  using APL much more convenient than using only the original
  APL 2 editing functionality.
- The displayed output can be scrolled through a fairly
  long history buffer (1000 lines).
- Text cut and paste is supported (mouse select for cut of
  any 2D visible region, ALT-V for paste into the current
  input line).
- Telnet functionality is built in.
- It is a "pure Python" application intended for use in a
  Python environment.
- Linux (at least Debian 12 and Ubuntu 22) and macOSX (at least 11.x)
  are supported.

Drawbacks
---------

- There is no character cell addressability. A "glass teletype"
  model is implemented for text entry and display.
- It can only be used with systems that have a Telnet server to
  which it can connect.
- The graphics command formats are unique to GTerm and GPLOT.
  (APL code can also generate these graphics commands).
- Installation requires a Python environment.
- It is definitely not intended to replace "normal" terminal
  emulators for general use.
- Windows (any version) is not supported.

Installation on Debian/Ubuntu Linux
-----------------------------------

For a completely "empty" machine:

- python3 --version (note version, must be 3.10 or newer)
- sudo apt install python3-pip
- sudo apt install python3.xx-venv (replace xx with version)
- sudo apt install portaudio19-dev
- sudo apt install python-all-dev
- sudo apt install pkg-config
- sudo apt install libcairo2-dev
- python3 -m venv ~/gtermenv
- source ~/gtermenv/bin/activate
- python -m pip install --upgrade pip
- git clone ...
- bash pippack.sh

This will install GTerm and also create a ZIP file, gterm.zip,
in the `package` subdirectory, which can also be used for
installation using: `pip install gterm.zip`

The number of binary packages that must be installed by APT is
disappointing, but PyCairo and PyAudio wheels are not
"self contained". This can cause version mismatch problems
between the binary libraries and the Python components, but
that is how it is.

Running
-------

- Ensure the gtermenv venv is active.
- Typing gterm in a CLI will launch GTerm.

Configuration
-------------

The only configuration file is a list of known hosts read from
the file: `~/gtermhostinfo.txt`. This defines one known host per line,
with four space separated fields as follows:
```
gui-name ip-address port-number system-type
```

- `gui-name` is a string identifying the host that will appear in a
  popup list control.
- `ip-address` is the IPV4 dotted decimal address of the host.
- `port-number` is the port to connect to on that host.
- `system-type` identifies the type of system to which the connection
  will be made. This sets things such as the erase character and some
  telnet interaction details.

The allowed system type values are:

- `nosapl` : For use with CDC NOS when using the APL application.
- `nos` : For use with CDC NOS when using GPLOT or for general use.
- `vms` : For use with DEC VAX/VMS systems.
- `unix` : For use with Unix-like systems and the usual GTerm graphics
  commands (as used by GPLOT).
- `unixalt` : For use with Unix-like systems, but interpreting the
  alternative graphics commands added for APL.
- `windows` : For use with Windows systems, but not tested with any
  version newer than Windows 7.

Extras
------

