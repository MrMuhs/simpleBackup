# simpleBackup
 
Well, as the name says - simple scripting to generate backups around 7z

## Required
- Python (tested on 3.8.5 (tags/v3.8.5:580fbb0, Jul 20 2020, 15:43:08) [MSC v.1926 32 bit (Intel)] on win32)
- 7-Zip installation available to be executed on commandline -> https://www.7-zip.org/

## simpleBackup.py
- creates backups for a folder
- running script will keep runing and schedule backups
- their are full and incremental backups
- their is a configurable time interval after backups gets deleted
- their is a small log file
