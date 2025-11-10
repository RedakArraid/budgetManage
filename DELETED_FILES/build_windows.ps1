# Script PowerShell pour générer l'exécutable Windows
# build_windows.ps1

Write-Host "🪟 Build BudgetManage Windows Executable" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green

# Vérifier Python et PyInstaller
Write-Host "🔍 Vérification des dépendances..." -ForegroundColor Yellow
python --version
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Python non trouvé" -ForegroundColor Red
    exit 1
}

pip show pyinstaller > $null
if ($LASTEXITCODE -ne 0) {
    Write-Host "📦 Installation de PyInstaller..." -ForegroundColor Yellow
    pip install pyinstaller
}

# Nettoyer les builds précédents
Write-Host "🧹 Nettoyage des builds précédents..." -ForegroundColor Yellow
if (Test-Path "dist") { Remove-Item -Recurse -Force "dist" }
if (Test-Path "build") { Remove-Item -Recurse -Force "build" }
if (Test-Path "BudgetManage-Portable") { Remove-Item -Recurse -Force "BudgetManage-Portable" }

# Créer le spec file
Write-Host "📝 Création du fichier .spec..." -ForegroundColor Yellow
python scripts/build_windows.py

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Exécutable créé avec succès!" -ForegroundColor Green
    Write-Host "📁 Fichiers disponibles:" -ForegroundColor Cyan
    Write-Host "  - dist/BudgetManage.exe" -ForegroundColor White
    Write-Host "  - BudgetManage-Portable/" -ForegroundColor White
    
    # Créer le ZIP
    Write-Host "🗜️ Création de l'archive ZIP..." -ForegroundColor Yellow
    Compress-Archive -Path "BudgetManage-Portable\*" -DestinationPath "BudgetManage-Windows-v1.0.0.zip" -Force
    
    $size = [math]::Round((Get-Item "dist/BudgetManage.exe").Length / 1MB, 1)
    Write-Host "📊 Taille de l'exécutable: $size MB" -ForegroundColor Cyan
    
    Write-Host "🎉 Build terminé avec succès!" -ForegroundColor Green
    Write-Host "💡 Pour distribuer: partagez BudgetManage-Windows-v1.0.0.zip" -ForegroundColor Cyan
    
    # Proposer de tester
    $test = Read-Host "🧪 Voulez-vous tester l'exécutable maintenant? (y/N)"
    if ($test -eq "y" -or $test -eq "Y") {
        Write-Host "🚀 Lancement du test..." -ForegroundColor Yellow
        Start-Process -FilePath "BudgetManage-Portable\start.bat" -WorkingDirectory "BudgetManage-Portable"
    }
} else {
    Write-Host "❌ Erreur lors du build" -ForegroundColor Red
    exit 1
}
