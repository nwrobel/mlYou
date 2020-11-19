# Python project deployment script for Windows OSs - Powershell script
#
# After cloning the project repo from Github and saving it in the directory of choice, run this script
# to setup the project so it can be used. 
#
# DEPENDENCIES
# This script should always be located in the project root (most parent) folder.
# requirements.txt should also be present in project root
#
# Please refer to the README.md for additional info
#


function Deploy-PythonProject {
    [CmdletBinding()]
    param ()

    $pythonVenvDir = Join-Path $PSScriptRoot -ChildPath 'py-venv-windows'
    $pipRequirementsFilepath = Join-Path $PSScriptRoot -ChildPath 'requirements.txt'

    # Remove pre-exisitng path of the projects virtual environment, if it exists
    Remove-VenvIfExists -VenvDir $pythonVenvDir

    # Create virtual env. and activate it if the version check passes
    if (Test-VenvPythonVersionIsCorrect) {
        Write-Host "Python version requirement check passed!" -ForegroundColor Cyan
        Install-PythonPackages -VenvDir $pythonVenvDir -PipReqsFilepath $pipRequirementsFilepath

    # If the version check fails, print out troubleshooting steps to guide user 
    # and allow user to specifiy the full path to virtualenv.exe, if they choose to
    } else {
        Write-Host "Version requirement check failed!" -ForegroundColor Red
        Write-Host "This project requires that python version 3.7 or higher be installed, so that a virtual environment can be created using python3.7 interpreter" -ForegroundColor Red

        Write-Host "`nTo fix this error, exit this script and do the following steps:" -ForegroundColor Magenta
        Write-Host "    - Ensure that the latest version of python3 is installed and updated on your system" 
        Write-Host "    - Ensure that your system's PATH variable includes the installation directory for python3, and that it is listed BEFORE any other python installation directories"
        Write-Host "    - Ensure that the 'virtualenv' command points to the correct executable by running 'Get-Command virtualenv' and checking the Source property"
        Write-Host "    - Run this script again, after ensuring the above"

        Write-Host "`nAlternative setup method:" -ForegroundColor Magenta 
        Write-Host "If you don't want to modify your system PATH variable, input the path to your 'virtualenv.exe' program, located in the 'Scripts' directory of your python3 installation directory,
        and I will try to create the virtual environment using this executable. To try this, input 'P' when prompted to do so."
        
        Write-Host "`nIf none of the above steps succeed, please refer to the documentation in the README to set up the project manually." -ForegroundColor Magenta

        # Try to use a non-default virtualenv path that the user enters
        do {
            $continue = Read-Host -Prompt "`nTo proceed, enter 'P' to input the path to the Python 3 'virtualenv.exe' on this system, or enter 'Q' to quit"

            if ($continue -eq 'q') {
                throw "Exiting due to choice of user"
            
            } elseif ($continue -ne 'p') {
                Write-Host "Incorrect response: Enter P or Q" -ForegroundColor Red
            }
        
        } while ($continue -ne 'p') 

        $venvExeCustomPath = Read-Host -Prompt "Please enter the path of the python3 'virtualenv.exe' program installed on your system"
        Write-Host "Attempting to use virtualenv.exe at $venvExeCustomPath" -ForegroundColor Cyan

        # Check that the path is valid and that this new virtualenv.exe uses correct python version
=        if (Test-Path -Path $venvExeCustomPath) {
            if (Test-VenvPythonVersionIsCorrect -VenvExePath $venvExeCustomPath) {
                Install-PythonPackages -VenvDir $pythonVenvDir -PipReqsFilepath $pipRequirementsFilepath -VenvExePath $venvExeCustomPath
            
            } else {
                throw "Error: Version requirement check failed. $venvExeCustomPath does not use the required version of python for this project."
            }

        } else {
            throw "Error: Specified virtualenv executable file not found: $venvExeCustomPath"
        }
    }
    
}

function Test-VenvPythonVersionIsCorrect {
    param(
        [Parameter(Mandatory=$false)]
        [string]$VenvExePath
    )

    if ($VenvExePath) {
        $VenvGetCommandResult = (Get-Command $VenvExePath)
    } else {
        $VenvGetCommandResult = (Get-Command virtualenv)
    }

    # Get the "python path" that the system's 'virtualenv' command is using:
    # find the directory of 'virtualenv', then look in its parent directory, which should contain the python executables
    $defaultVirtualenvPythonPath = ($VenvGetCommandResult | Select-Object -ExpandProperty Source | Get-Item).Directory.Parent.Fullname
    $defaultPythonVirtualenvVersion = [System.Diagnostics.FileVersionInfo]::GetVersionInfo("$defaultVirtualenvPythonPath\python.exe").FileVersion

    if ($defaultPythonVirtualenvVersion -ge '3.7') { 
        Write-Host "System command 'virtualenv' refers to a virtualenv.exe that uses python version 3.7 or higher...version correct!" -ForegroundColor Cyan
        return $true
    
    } else {
        Write-Host "System command 'virtualenv' refers to a virtualenv.exe that uses python version lower than (python3.7)...version incorrect!" -ForegroundColor Cyan
        return $false
    }
}

function Remove-VenvIfExists {
    [CmdletBinding()]
    param (
        [Parameter()]
        [string]$VenvDir
    )

    # Remove existing folder of same venv name, if present in project dir
    if (Test-Path -Path $VenvDir) {
        Write-Host 'Python virtual environment already exists: we need to remove it to install this project from scratch' -ForegroundColor Cyan
        Write-Host "WARNING: The directory named 'py-venv-windows' inside this project directory will be removed" -ForegroundColor Yellow

        do {
            $continue = Read-Host -Prompt "Proceed with removing 'py-venv'? [Y/N]"

            if ($continue -eq 'n') {
                throw "Exiting due to choice of user"
            
            } elseif ($continue -ne 'y') {
                Write-Host "Incorrect response: Enter Y or N" -ForegroundColor Red
            }
        
        } while ($continue -ne 'y') 
        
        Remove-Item -Path $VenvDir -Recurse -Force
    } 
}

function Install-PythonPackages {
    param(
        [Parameter()]
        [string]$VenvDir,

        [Parameter()]
        [string]$PipReqsFilepath,

        [Parameter(Mandatory=$false)]
        [string]$VenvExePath
    )

    Write-Host "Creating virtual environment 'py-venv-windows', in which the Python project dependencies will be installed" -ForegroundColor Cyan

    # run the virtualenv command to make the virtual env.
    # Use the virtualenv exe specified, or use the default one if none is specified
    if ($VenvExePath) {
        & $VenvExePath $VenvDir
    } else {
        virtualenv $VenvDir     
    }

    if (Test-Path -Path $VenvDir) {
        Write-Host "Virtual environment 'py-venv-windows' exists: creation successfully" -ForegroundColor Cyan
        # Write-Host "Activating virtual environment 'py-venv-windows'" -ForegroundColor Cyan
        # & "$VenvDir\Scripts\activate" # run the 'activate' script to activate the virtual env.
    
    } else {
        throw "Error: Virtual environment 'py-venv-windows' was not found...there was an issue creating this env"
    } 

    Write-Host "Updating pip.exe for new virtualenv"
    $venvPythonExePath = Join-Path $VenvDir -ChildPath "Scripts\python.exe"
    & $venvPythonExePath -m pip install --upgrade pip

    Write-Host "Installing Python Pip packages into virtual environment" -ForegroundColor Cyan
    $venvPipFilepath = Join-Path $VenvDir -ChildPath 'Scripts\pip.exe'

    Write-Host "Using Pip executable of the Venv" -ForegroundColor Cyan
    & $venvPipFilepath install -r $PipReqsFilepath
}

Deploy-PythonProject