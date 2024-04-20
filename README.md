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
- Installation requires a Python environment (a "con" as well
  as a "pro").
- It is definitely not intended to replace "normal" terminal
  emulators for general use.
- No version of the Windows operating system is supported.

Installation on Debian/Ubuntu Linux
-----------------------------------

For a completely "empty" machine:

1. Install system wide binary pre-requisites with APT.
- `python3 --version` (note version, must be 3.10 or newer)
- `sudo apt install python3-pip`
- `sudo apt install python3.xx-venv` (replace `xx` with version)
- `./aptinstalls.sh`

2. Create a Python virtual environment for running GTerm.
- `python3 -m venv ~/gtermenv`
- `source ~/gtermenv/bin/activate`
- `python -m pip install --upgrade pip`

3. Install GTerm in that virtual environment.
- `pip install .`

The number of binary packages that must be installed by APT is
disappointing, but the PyCairo and PyAudio wheels are not
"self contained". This can cause version mismatch problems
between the binary libraries and the Python components, but
that is how it is.

It should be straightforward to install GTerm on any other Linux
distribution using the packages listed in `aptinstalls.sh` as a
guide.

Installation on macOS
---------------------

For a completely empty machine but with Homebrew already installed:

1. Install binary pre-requisites with Homebrew.
- `brew install portaudio`
- `brew install pkg-config`
- `brew install cairo`

2. Create a Python virtual environment for running GTerm.
- `python3 -m venv ~/gtermenv`
- `source ~/gtermenv/bin/activate`
- `python -m pip install --upgrade pip`

3. Install GTerm in that virtual environment.
- `pip install .`

Running
-------

GTerm should be run from a "shell" in a terminal window.

- Ensure the gtermenv venv is active, for example with:
  `source ~/gtermenv/bin/activate`
- Typing `gterm` will then launch GTerm.

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

Two directories contain things related to GTerm.

The tools directory contains programs useful for modifying GTerm
for other purposes. See the documentation in the Documents
subdirectory for more information.

The ctelnet directory contains a very barebones telnet client that
does all that needs to be done for retrocomputing applications. The
telnet client supplied with modern systems (if any) has many complex
features that are really not needed for talking to simulators over
a LAN. It also has tricky configuration files and is often buggy
as telnet clients are very low priority and frowned on for
security reasons.

The ctelnet program is intended for use with terminal emulators other than
GTerm (which has a telnet client built in) such as XTerm or iTerm2.
It is simple enough to build it on any Linux or macOS system using the
`build.sh` script.
```
ctelnet hostname_or_IP port_number
```
will connect to a telnet server on a host at a given port. There
are other options, but they are not normally needed. When starting
a terminal emulator, ctelnet should be given as the command for
the emulator to execute.

Documentation
-------------

The main GTerm documentation is the PDF file: `gterm.pdf` in
the `Documentation` subdirectory.

This can be rebuilt from LaTeX source using the `build.sh` script
in that directory. A complete TeX/LaTeX installation must be present
to do this though.

Screenshots
-----------
![gterm-apl-ss](https://github.com/nickglazzard1959/gterm/assets/27016608/f38eb8f9-5c1b-4c1a-9495-a52533cee774)

![gterm-gplot-text](https://github.com/nickglazzard1959/gterm/assets/27016608/f54519e0-0f90-4c9d-bba2-32726c327345)

![gterm-gplot-graphics](https://github.com/nickglazzard1959/gterm/assets/27016608/38b64e75-b387-4565-b260-3390168d1b56)



