Set WshShell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")

If fso.FileExists("VibePad.exe") Then
    WshShell.Run "VibePad.exe", 0, False
Else
    WshShell.Run "pythonw VibePad.py", 0, False
End If
WshShell.Run "pythonw ""F:\Artificial Intelligence (Ai)\VibePad_v2.3.0\VibePad.py""", 0, False 
