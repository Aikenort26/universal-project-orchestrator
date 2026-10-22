<#
.SYNOPSIS
    Auditoria de salud de sincronizacion y bases de datos para el ecosistema multi-maquina.
.DESCRIPTION
    Detecta archivos de conflicto generados por Google Drive (* (1).*, etc.),
    valida la integridad de las bases de datos SQLite y su modo WAL,
    y verifica el estado de cerrojos inter-agente.
.EXAMPLE
    pwsh -File "G:\Mi unidad\00-scripts_admin\test-sync-health.ps1"
    pwsh -File "G:\Mi unidad\00-scripts_admin\test-sync-health.ps1" -Fix
#>
[CmdletBinding()]
param (
    [switch]$Fix,
    [string]$TargetDir = "G:\Mi unidad\BRAIN"
)

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "  AUDITORIA DE SALUD DE SINCRONIZACION Y ESTADO DISTRIBUIDO" -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "Directorio objetivo: $TargetDir" -ForegroundColor Gray
Write-Host ""

$issuesFound = 0

# 1. Deteccion de archivos de conflicto de sincronizacion
Write-Host "[1/3] Verificando archivos de conflicto de Google Drive..." -ForegroundColor Yellow
$conflictPatterns = @("* (1).*", "* (2).*", "* (3).*", "* (conflict*).*")
$conflictFiles = @()

foreach ($pattern in $conflictPatterns) {
    $found = Get-ChildItem -Path $TargetDir -Filter $pattern -Recurse -File -ErrorAction SilentlyContinue |
             Where-Object { $_.FullName -notmatch "\\\.git\\" }
    if ($found) {
        $conflictFiles += $found
    }
}

if ($conflictFiles.Count -gt 0) {
    Write-Host "  ALERTA: Se encontraron $($conflictFiles.Count) archivos de conflicto:" -ForegroundColor Red
    foreach ($file in $conflictFiles) {
        Write-Host "    - $($file.FullName) ($($file.Length) bytes)" -ForegroundColor Red
        $issuesFound++
    }

    if ($Fix) {
        $trashDir = Join-Path $TargetDir "_trash\sync_conflicts_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
        New-Item -ItemType Directory -Path $trashDir -Force | Out-Null
        Write-Host "  Moviendo archivos de conflicto a: $trashDir" -ForegroundColor Magenta
        foreach ($file in $conflictFiles) {
            Move-Item -Path $file.FullName -Destination $trashDir -Force
            Write-Host "    Movido: $($file.Name)" -ForegroundColor Gray
        }
        Write-Host "  Conflictos aislados de forma segura." -ForegroundColor Green
    } else {
        Write-Host "  Sugerencia: Ejecute con el parametro -Fix para aislar estos archivos en _trash." -ForegroundColor Yellow
    }
} else {
    Write-Host "  CORRECTO: No se encontraron archivos de conflicto de sincronizacion." -ForegroundColor Green
}

# 2. Verificacion de bases de datos SQLite y modo WAL
Write-Host ""
Write-Host "[2/3] Verificando integridad de bases de datos SQLite y modo WAL..." -ForegroundColor Yellow
$dbFiles = Get-ChildItem -Path $TargetDir -Filter "*.db" -Recurse -File -ErrorAction SilentlyContinue |
           Where-Object { $_.FullName -notmatch "\\\.git\\" -and $_.FullName -notmatch "\\node_modules\\" }

foreach ($db in $dbFiles) {
    $dbPath = $db.FullName
    $pyCheck = @"
import sqlite3, sys
path = sys.argv[1]
try:
    con = sqlite3.connect(path, timeout=5.0)
    cur = con.cursor()
    cur.execute('PRAGMA integrity_check;')
    res = cur.fetchone()[0]
    cur.execute('PRAGMA journal_mode;')
    mode = cur.fetchone()[0]
    con.close()
    print(res + '|' + mode)
except Exception as e:
    print('ERROR: ' + str(e))
"@
    $res = python -c "$pyCheck" "$dbPath"
    if ($res -match "ok\|wal") {
        Write-Host "  CORRECTO: $($db.Name) -> Integridad: OK, Modo: WAL" -ForegroundColor Green
    } elseif ($res -match "ok\|") {
        Write-Host "  AVISO: $($db.Name) -> Integridad: OK, Modo: $res (Se recomienda cambiar a WAL)" -ForegroundColor Yellow
        if ($Fix) {
            $fixWAL = @"
import sqlite3, sys
path = sys.argv[1]
con = sqlite3.connect(path)
con.execute('PRAGMA journal_mode=WAL;')
con.close()
print('WAL configurado')
"@
            python -c "$fixWAL" "$dbPath" | Out-Null
            Write-Host "    -> Actualizado a modo WAL." -ForegroundColor Green
        }
    } else {
        Write-Host "  ERROR: $($db.Name) -> $res" -ForegroundColor Red
        $issuesFound++
    }
}

# 3. Verificacion de cerrojos huerfanos inter-agente
Write-Host ""
Write-Host "[3/3] Verificando cerrojos inter-agente (.brain/locks/)..." -ForegroundColor Yellow
$locksDir = "G:\Mi unidad\BRAIN\.brain\locks"
if (Test-Path $locksDir) {
    $now = Get-Date
    $lockFiles = Get-ChildItem -Path $locksDir -Filter "*.lock" -File -ErrorAction SilentlyContinue
    if ($lockFiles.Count -gt 0) {
        foreach ($lock in $lockFiles) {
            $ageMinutes = ($now - $lock.LastWriteTime).TotalMinutes
            if ($ageMinutes -gt 15) {
                Write-Host "  AVISO: Cerrojo expirado (>15 min): $($lock.Name) (Edad: $([math]::Round($ageMinutes, 1)) min)" -ForegroundColor Yellow
                if ($Fix) {
                    Remove-Item -Path $lock.FullName -Force
                    Write-Host "    -> Cerrojo expirado eliminado." -ForegroundColor Green
                }
            } else {
                Write-Host "  ACTIVO: Cerrojo vigente: $($lock.Name) (Edad: $([math]::Round($ageMinutes, 1)) min)" -ForegroundColor Cyan
            }
        }
    } else {
        Write-Host "  CORRECTO: No hay cerrojos activos ni huerfanos." -ForegroundColor Green
    }
} else {
    Write-Host "  CORRECTO: Directorio de cerrojos limpio o no inicializado." -ForegroundColor Green
}

Write-Host ""
Write-Host "==========================================================" -ForegroundColor Cyan
if ($issuesFound -eq 0) {
    Write-Host "  ESTADO GENERAL: EXCELENTE (Cero problemas detectados)" -ForegroundColor Green
} else {
    Write-Host "  ESTADO GENERAL: REQUIERE ATENCION ($issuesFound observaciones)" -ForegroundColor Yellow
}
Write-Host "==========================================================" -ForegroundColor Cyan
