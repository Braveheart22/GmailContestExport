@echo off
cd /d C:\GmailContestExport

echo =============================== >> export_log.txt
echo Run started: %date% %time% >> export_log.txt

C:\Users\John.LOOP\AppData\Local\Programs\Python\Python314\python.exe C:\GmailContestExport\export_contest_entries.py >> export_log.txt 2>&1

echo Run ended: %date% %time% >> export_log.txt
echo =============================== >> export_log.txt