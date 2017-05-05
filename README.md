Package Check
=============

This is a simple python program that takes a list of containers and a list of rpms
and checks to see if any of the containers need updating based on the rpm lists.

If the --update argument is passed it will call yum update in the required containers.

Some notes:

- It uses a process pool to run containers in parallel.
- It's a little bit smart about which containers to update.
- It commits the containers back with the same tag.

