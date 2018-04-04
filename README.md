# console-bible-reader

A console application that lets you read books of the Bible side-by-side.

The application includes the following translations of the Bible:

 * Vulgate (Latin)
 * Neo vulgate (Latin)
 * New International Version (English)
 * King James (English)
 * New King James Version (English)
 * Nueva Version Internacional (Spanish)
 * Luther (German)

## Usage

### To display usage information, run bible-reader -h at the command line:

usage: bible-reader.py [-h] [left] [right] [book] [chapter]

read the bible with translations side-by-side

positional arguments:
  left        version on left screen
  right       version on right screen
  book        bible book to display
  chapter     chapter to display

optional arguments:
  -h, --help  show this help message and exit

versions available: nvi lu niv kj vulg nv nkj

### To start the application with the New King James and Luther versions:

bible-reader nkj lu

## Dependencies

Depends on the Urwid Library (http://urwid.org/)

