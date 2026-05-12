Set WshShell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")
strPath = WshShell.CurrentDirectory

' Run only once
If fso.FileExists("VibePad.exe") Then
    WshShell.Run "VibePad.exe", 0, False
Else
    WshShell.Run "pythonw VibePad.py", 0, False
End If
WshShell.Run "pythonw ""F:\Artificial Intelligence (Ai)\VibePad_v2.4.0\VibePad.py""", 0, False
WshShell.Run "pythonw ""F:\Artificial Intelligence (Ai)\VibePad_v2.4.0\VibePad.py""", 0, False 
WshShell.Run "pythonw ""G:\Software\VibePad_v2.4.0\VibePad.py""", 0, False 
WshShell.Run "pythonw ""G:\Software\VibePad_v2.4.0\VibePad.py""", 0, False 
