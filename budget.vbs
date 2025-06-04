Set WshShell = CreateObject("WScript.Shell")
WshShell.Run "budget.bat", 0
WshShell.Popup "Lancement de l'application en cours", 3, "Budget", 64