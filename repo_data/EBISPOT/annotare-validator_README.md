# Annotare validator
A validation script to ensure Annotare are informed of any important term changes, for example: Key terms being obsoleted in EFO.

## To use:
- Clone this repository
- Run `bash annotare.sh` from your local copy on the command line
- If the script displays an error or failure message rather than diplaying the complete message (100%), this means there is a term that is violating the tests, is obsolete and used as a core term by annotare.
- If the script diplays the complete message (100%) there is no violation of the tests.
