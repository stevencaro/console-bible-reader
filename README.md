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
bible-reader -h
usage: bible-reader.py [-h] [left] [right] [book] [chapter]

side-by-side bible reader

positional arguments:
  left        version on left screen
  right       version on right screen
  book        bible book to display
  chapter     chapter to display

optional arguments:
  -h, --help  show this help message and exit


## Dependencies

Depends on the Urwid Library (http://urwid.org/)

