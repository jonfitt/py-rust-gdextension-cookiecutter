#Requires -Version 5.1
param(
    [string]$RepoPath = ".",
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$RemainingArgs
)

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$BashScript = Join-Path $ScriptDir "..\github-protection\apply.sh"

if (-not (Test-Path -LiteralPath $BashScript)) {
    throw "Missing script: $BashScript"
}

$Bash = Get-Command bash -ErrorAction SilentlyContinue
if (-not $Bash) {
    throw "bash is required (Git for Windows or WSL). Install Git for Windows or run from WSL."
}

$ResolvedRepoPath = Resolve-Path -LiteralPath $RepoPath
$UnixRepoPath = & "$($Bash.Source)" -lc "wslpath -a '$($ResolvedRepoPath.Path)'" 2>$null
if (-not $UnixRepoPath) {
    $Drive = $ResolvedRepoPath.Path.Substring(0, 1).ToLowerInvariant()
    $Tail = $ResolvedRepoPath.Path.Substring(2) -replace '\\', '/'
    $UnixRepoPath = "/mnt/$Drive$Tail"
}

$ArgsList = @("--repo-path", $UnixRepoPath) + $RemainingArgs
& "$($Bash.Source)" $BashScript @ArgsList
