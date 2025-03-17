set PATH="C:\Program Files\MySQL\MySQL Server 8.3\bin";%PATH%
set dt=%date:~6,4%%date:~3,2%%date:~0,2%_%time:~0,2%%time:~3,2%%time:~6,2%
mysqldump.exe -u root -pVijayam1952 -B accounts -r "C:\Users\vpvij\OneDrive\Documents\mysql_backup\mysql_dump_"%dt%