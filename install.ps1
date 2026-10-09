$ErrorActionPreference = 'Stop'
$whExcelRoot = $PSScriptRoot
$whExcelId = 'excel-wheel-scroll-sheets'
$whExcelKey = 'HKLM:\SOFTWARE\Windhawk\Engine\Mods\excel-wheel-scroll-sheets'
$whExcelSource = Join-Path $whExcelRoot 'excel-wheel-scroll-sheets.wh.cpp'
$whExcelDll = Join-Path $whExcelRoot 'excel-wheel-scroll-sheets_0.5.1.dll'
$whExcelTargetSource = 'C:\ProgramData\Windhawk\ModsSource\excel-wheel-scroll-sheets.wh.cpp'
$whExcelTargetDll = 'C:\ProgramData\Windhawk\Engine\Mods\64\excel-wheel-scroll-sheets_0.5.1.dll'
$whExcelCreatedKey = $false
$whExcelCopiedSource = $false
$whExcelCopiedDll = $false
$whExcelResult = Join-Path $whExcelRoot 'installation-result.json'
try {
    $whExcelIdentity = [Security.Principal.WindowsIdentity]::GetCurrent()
    if (-not ([Security.Principal.WindowsPrincipal]::new($whExcelIdentity)).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
        throw 'Administrator permission is required.'
    }
    if (Test-Path -LiteralPath $whExcelKey) { throw 'The Excel mod already exists; preserve its configuration.' }
    if ((Test-Path -LiteralPath $whExcelTargetSource) -or (Test-Path -LiteralPath $whExcelTargetDll)) {
        throw 'Existing Excel mod files were found; preserve them.'
    }
    if ((Get-FileHash -LiteralPath $whExcelSource).Hash -ne '3B4D0B22EA176A984AAC3E9FF5ED1ABFBC1951BF0C20E9D32F49BE946D845456') { throw 'Source hash mismatch.' }
    if ((Get-FileHash -LiteralPath $whExcelDll).Hash -ne 'A4DAA3AD69A802C16ACB5D3161EDAD788FD5157B702FAD63D81FA45650EF1DF3') { throw 'DLL hash mismatch.' }
    Copy-Item -LiteralPath $whExcelSource -Destination $whExcelTargetSource
    $whExcelCopiedSource = $true
    Copy-Item -LiteralPath $whExcelDll -Destination $whExcelTargetDll
    $whExcelCopiedDll = $true
    New-Item -Path $whExcelKey | Out-Null
    $whExcelCreatedKey = $true
    foreach ($whExcelPair in @{
        LibraryFileName='excel-wheel-scroll-sheets_0.5.1.dll'
        Include='EXCEL.EXE'; Exclude=''; Architecture='x86-64'; Version='0.5.1'
    }.GetEnumerator()) {
        New-ItemProperty -LiteralPath $whExcelKey -Name $whExcelPair.Key -Value $whExcelPair.Value -PropertyType String | Out-Null
    }
    New-ItemProperty -LiteralPath $whExcelKey -Name Disabled -Value 0 -PropertyType DWord | Out-Null
    New-ItemProperty -LiteralPath $whExcelKey -Name SettingsChangeTime -Value ([int][DateTimeOffset]::UtcNow.ToUnixTimeSeconds()) -PropertyType DWord | Out-Null
    $whExcelSettings = $whExcelKey + '\Settings'
    New-Item -Path $whExcelSettings | Out-Null
    New-ItemProperty -LiteralPath $whExcelSettings -Name wheelAction -Value 'scroll' -PropertyType String | Out-Null
    foreach ($whExcelPair in @{ smoothAnimation=1; horizontalGestureMs=200; horizontalSwitching=1; reverseDirection=0; throttleMs=150; wrapAround=0 }.GetEnumerator()) {
        New-ItemProperty -LiteralPath $whExcelSettings -Name $whExcelPair.Key -Value $whExcelPair.Value -PropertyType DWord | Out-Null
    }
    if ((Get-FileHash -LiteralPath $whExcelTargetSource).Hash -ne (Get-FileHash -LiteralPath $whExcelSource).Hash) { throw 'Installed source verification failed.' }
    if ((Get-FileHash -LiteralPath $whExcelTargetDll).Hash -ne (Get-FileHash -LiteralPath $whExcelDll).Hash) { throw 'Installed DLL verification failed.' }
    # Windhawk watches mod configuration changes; new Excel processes load this
    # mod directly. Preserve the existing service and client sessions.
    if ((Get-Service Windhawk).Status -ne 'Running') { Start-Service -Name Windhawk }
    $whExcelReport = [ordered]@{
        Status='installed'; Version='0.5.1'; HorizontalSwitching=$true
        Source=$whExcelTargetSource; Dll=$whExcelTargetDll
        ServiceStatus=(Get-Service Windhawk).Status.ToString()
        InstalledAt=(Get-Date).ToString('o')
    }
    [IO.File]::WriteAllText($whExcelResult, ($whExcelReport | ConvertTo-Json), [Text.UTF8Encoding]::new($false))
} catch {
    $whExcelError = $_.Exception.Message
    # Only remove the new mod's exact paths created by this installer.
    if ($whExcelCreatedKey) { Remove-Item -LiteralPath $whExcelKey -Recurse -Force }
    if ($whExcelCopiedSource) { Remove-Item -LiteralPath $whExcelTargetSource -Force }
    if ($whExcelCopiedDll) { Remove-Item -LiteralPath $whExcelTargetDll -Force }
    [IO.File]::WriteAllText($whExcelResult, (@{Status='failed'; Error=$whExcelError} | ConvertTo-Json), [Text.UTF8Encoding]::new($false))
    exit 1
}
