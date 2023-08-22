%1 mshta vbscript:CreateObject("Shell.Application").ShellExecute("cmd.exe","/c %~s0 ::","","runas",1)(window.close)&&exit
echo Loading....
IF NOT EXIST C:\control\* (
    net use \\172.26.6.167\tempshare\remoteControl /user:TEA PU11SE
    xcopy /E /I /Y /H \\172.26.6.167\tempshare\remoteControl C:\control\
    net use \\172.26.6.167\tempshare\remoteControl /delete
)

IF NOT EXIST C:\Python38\* (
    net use \\172.26.6.167\tempshare\Python38_clear /user:TEA PU11SE
    xcopy /E /I /Y /H \\172.26.6.167\tempshare\Python38_clear C:\Python38\
    net use \\172.26.6.167\tempshare\Python38_clear /delete
)


xcopy /E /I /Y /H C:\control\venv\Lib\site-packages C:\Python38\Lib\site-packages\


)

echo Run client....
IF EXIST C:\control\* (
    cd C:\control
    git fetch origin control && git reset --hard origin/control
    echo Update for git successed!
    C:\Python38\pythonw client.py
)

pause