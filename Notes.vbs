Dim shell, dir, pythonw, cmd
Set shell = CreateObject("WScript.Shell")

' Diretório do script
dir = CreateObject("Scripting.FileSystemObject").GetParentFolderName(WScript.ScriptFullName)

' Tenta pythonw da venv primeiro
pythonw = dir & "\venv\Scripts\pythonw.exe"
If Not CreateObject("Scripting.FileSystemObject").FileExists(pythonw) Then
    ' Tenta pythonw do sistema
    pythonw = "pythonw"
End If

cmd = """" & pythonw & """ """ & dir & "\app.py"""

' Executa sem janela (0 = oculto, False = não aguarda)
shell.Run cmd, 0, False
