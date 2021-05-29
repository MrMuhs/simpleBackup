# simpleBackup
 
Well, as the name says - simple scripting to generate backups around 7z

## Required
- Python (tested on 3.8.5 (tags/v3.8.5:580fbb0, Jul 20 2020, 15:43:08) [MSC v.1926 32 bit (Intel)] on win32)
- 7-Zip installation available to be executed on commandline -> https://www.7-zip.org/

## simpleBackup.py
- creates backups for a folder
- default running script will keep runing and schedule backups
- their is a "oneShot" switch so the script exits after one run, so it can be used with e.g. Task Scheduler
- their are full and incremental backups
- their is a configurable time interval after backups gets deleted
- their is a small log file

## simpleBackupTimed.py
- creates backups for a folder, each day
- their is a time of day to define when backup shall be executed
- their is a day of week to define where full backup shall be created
- their will be incremental up backup, if the day is not full backup
- their is a configurable time interval after backups gets deleted
- their is a small log file

## simpleBackupTimedMulti.py
- creates backups for a configureable list of folders, each day
- each folder on the list has a configureable backupname that is add to the filename 
- their is a time of day to define when backup shall be executed
- their is a day of week to define where full backup shall be created
- their will be incremental up backup, if the day is not full backup
- their is a configurable time interval after backups gets deleted
- their is a small log file