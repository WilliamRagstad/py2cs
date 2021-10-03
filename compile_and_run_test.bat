@echo off
py py2cs.py test.py test.cs
C:\Windows\Microsoft.NET\Framework\v3.5\csc.exe /t:exe /out:test.exe test.cs
echo ====== Running ======
test.exe