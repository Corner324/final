$root = "$PSScriptRoot/services"
Get-ChildItem -Path $root -Directory | ForEach-Object {
    Write-Host "Locking $($_.Name) ..."
    Push-Location $_.FullName
    poetry add 'faststream[rabbit]'
    poetry lock
    poetry install
    Pop-Location
}
Write-Host "Done!" 