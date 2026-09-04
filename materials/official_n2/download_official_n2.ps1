[CmdletBinding()]
param(
    [switch]$Force
)

$ErrorActionPreference = 'Stop'
$downloadRoot = Join-Path $PSScriptRoot 'downloads'
$checksumPath = Join-Path $PSScriptRoot 'checksums.local.sha256'

$files = @(
    @{ Version = '2012'; Name = 'N2V.pdf';      Url = 'https://www.jlpt.jp/samples/sample2012/pdf/N2V.pdf' },
    @{ Version = '2012'; Name = 'N2G.pdf';      Url = 'https://www.jlpt.jp/samples/sample2012/pdf/N2G.pdf' },
    @{ Version = '2012'; Name = 'N2R.pdf';      Url = 'https://www.jlpt.jp/samples/sample2012/pdf/N2R.pdf' },
    @{ Version = '2012'; Name = 'N2L.pdf';      Url = 'https://www.jlpt.jp/samples/sample2012/pdf/N2L.pdf' },
    @{ Version = '2012'; Name = 'N2sheet.pdf';  Url = 'https://www.jlpt.jp/samples/sample2012/pdf/N2sheet.pdf' },
    @{ Version = '2012'; Name = 'N2answer.pdf'; Url = 'https://www.jlpt.jp/samples/sample2012/pdf/N2answer.pdf' },
    @{ Version = '2012'; Name = 'N2script.pdf'; Url = 'https://www.jlpt.jp/samples/sample2012/pdf/N2script.pdf' },
    @{ Version = '2012'; Name = 'N2Q1.mp3';     Url = 'https://www.jlpt.jp/samples/sample2012/mp3/N2Q1.mp3' },
    @{ Version = '2012'; Name = 'N2Q2.mp3';     Url = 'https://www.jlpt.jp/samples/sample2017/mp3/N2Q2.mp3' },
    @{ Version = '2012'; Name = 'N2Q3.mp3';     Url = 'https://www.jlpt.jp/samples/sample2012/mp3/N2Q3.mp3' },
    @{ Version = '2012'; Name = 'N2Q4.mp3';     Url = 'https://www.jlpt.jp/samples/sample2012/mp3/N2Q4.mp3' },
    @{ Version = '2012'; Name = 'N2Q5.mp3';     Url = 'https://www.jlpt.jp/samples/sample2012/mp3/N2Q5.mp3' },
    @{ Version = '2018'; Name = 'N2V.pdf';      Url = 'https://www.jlpt.jp/samples/sample2018/pdf/N2V.pdf' },
    @{ Version = '2018'; Name = 'N2G.pdf';      Url = 'https://www.jlpt.jp/samples/sample2018/pdf/N2G.pdf' },
    @{ Version = '2018'; Name = 'N2R.pdf';      Url = 'https://www.jlpt.jp/samples/sample2018/pdf/N2R.pdf' },
    @{ Version = '2018'; Name = 'N2L.pdf';      Url = 'https://www.jlpt.jp/samples/sample2018/pdf/N2L.pdf' },
    @{ Version = '2018'; Name = 'N2sheet.pdf';  Url = 'https://www.jlpt.jp/samples/sample2018/pdf/N2sheet.pdf' },
    @{ Version = '2018'; Name = 'N2answer.pdf'; Url = 'https://www.jlpt.jp/samples/sample2018/pdf/N2answer.pdf' },
    @{ Version = '2018'; Name = 'N2script.pdf'; Url = 'https://www.jlpt.jp/samples/sample2018/pdf/N2script.pdf' },
    @{ Version = '2018'; Name = 'N2Q1.mp3';     Url = 'https://www.jlpt.jp/samples/sample2018/mp3/N2Q1.mp3' },
    @{ Version = '2018'; Name = 'N2Q2.mp3';     Url = 'https://www.jlpt.jp/samples/sample2018/mp3/N2Q2.mp3' },
    @{ Version = '2018'; Name = 'N2Q3.mp3';     Url = 'https://www.jlpt.jp/samples/sample2018/mp3/N2Q3.mp3' },
    @{ Version = '2018'; Name = 'N2Q4.mp3';     Url = 'https://www.jlpt.jp/samples/sample2018/mp3/N2Q4.mp3' },
    @{ Version = '2018'; Name = 'N2Q5.mp3';     Url = 'https://www.jlpt.jp/samples/sample2018/mp3/N2Q5.mp3' }
)

foreach ($file in $files) {
    $versionDir = Join-Path $downloadRoot $file.Version
    New-Item -ItemType Directory -Force -Path $versionDir | Out-Null
    $target = Join-Path $versionDir $file.Name
    $partialTarget = "$target.part"

    if ((-not $Force) -and (Test-Path -LiteralPath $target)) {
        Write-Host "Exists: $($file.Version)/$($file.Name)"
        continue
    }

    Write-Host "Downloading: $($file.Version)/$($file.Name)"
    if (Test-Path -LiteralPath $partialTarget) {
        Remove-Item -LiteralPath $partialTarget -Force
    }
    Invoke-WebRequest -UseBasicParsing -Uri $file.Url -OutFile $partialTarget

    if ((Get-Item -LiteralPath $partialTarget).Length -eq 0) {
        throw "Downloaded file is empty: $partialTarget"
    }
    Move-Item -LiteralPath $partialTarget -Destination $target -Force
}

$hashLines = foreach ($file in $files) {
    $relativePath = "$($file.Version)/$($file.Name)"
    $target = Join-Path $downloadRoot $relativePath
    $hash = Get-FileHash -Algorithm SHA256 -LiteralPath $target
    "$($hash.Hash.ToLowerInvariant())  $relativePath"
}

$hashLines | Set-Content -Encoding utf8 -LiteralPath $checksumPath
Write-Host "Downloaded $($files.Count) files to $downloadRoot"
Write-Host "Checksums written to $checksumPath"
