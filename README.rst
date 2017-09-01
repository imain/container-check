Container Check
===============

This is a simple script that checks your yum repos vs a list of containers.  It can
then tell you which containers need updating and optionaly update them if the --update
argument is passed.

Notes
-----

- It mounts in your local /etc/yum configuration for updates.
- It uses a process pool to run containers in parallel.
- It commits the containers back with the same tag.
