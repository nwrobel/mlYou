# MLU project deployment script for Windows OSs - Powershell script
#
# After cloning the MLU repo from Github and saving it in the directory of choice, run this script
# to setup the project so it can be used. 
#
# Please refer to the README.md on Github or in this directory for setup troubleshooting and for
# information on how to use the features of MLU!

param(
    [Parameter(Mandatory=$false)]
    [switch]$UseExistingVenv = $false
)

$pythonVenvLocation = '.\py-venv'

if (-not $UseExistingVenv) {

    # Remove existing folder of same venv name, if present in project dir
    if (Test-Path -Path $pythonVenvLocation) {
        Write-Host 'Python virtual environment seems to already exist...we need to remove it to install MLU fresh' -ForegroundColor Yellow
        Write-Host "The directory named 'py-venv' inside this project directory will be removed" -ForegroundColor Yellow
    
        do {
            $continue = Read-Host -Prompt "Proceed with removing 'py-venv'? [Y/N]"
    
            if ($continue -eq 'n') {
                throw "Exiting due to choice of user"
            
            } elseif ($continue -ne 'y') {
                Write-Host "Incorrect response: Enter Y or N" -ForegroundColor Red
            }
        
        } while ($continue -ne 'y') 
        
        Remove-Item -Path $pythonVenvLocation -Recurse -Force -WhatIf
    }

    # Check that virtualenv is using python3.7
    $defaultVirtualenvPythonPath = (Get-Command virtualenv | Select-Object -ExpandProperty Source | Get-Item).Directory.Parent.Fullname
    $defaultPythonVirtualenvVersion = [System.Diagnostics.FileVersionInfo]::GetVersionInfo("$defaultVirtualenvPythonPath\python.exe").FileVersion

    # Create virtual env. and activate it if check passes
    if ($defaultPythonVirtualenvVersion -ge '3.7') {
        Write-Host "System command 'virtualenv' refers to the virtualenv.exe that uses python version 3.7 or higher" -ForegroundColor Cyan
        Write-Host "Version requirement check completed successfully!" -ForegroundColor Cyan

        Write-Host "Creating python virtual environment 'py-venv', in which MLU dependencies will be installed" -ForegroundColor Cyan
        virtualenv $pythonVenvLocation

        Write-Host "Activating virtual environment 'py-venv'" -ForegroundColor Cyan
        .\py-venv\Scripts\activate

    # Print out troubleshooting steps to guide user towards using the correct virtualenv/python version
    } else {
        Write-Host "Version requirement check error" -ForegroundColor Red
        Write-Host "On this system, the command 'virtualenv' refers to a virtualenv.exe that uses python version lower than (python3.7).`n
        This project requires that python version 3.7 or higher be installed, so that a virtual environment can be created using python3.7 interpreter.`n" -ForegroundColor Red

        Write-Host "`nTo fix this error, do the following steps:`n" -ForegroundColor Magenta
        Write-Host "    - Ensure that the latest version of python3 is installed and updated on your system`n" 
        Write-Host "    - Ensure that your system's PATH variable includes the installation directory for python3, and that it is listed BEFORE any other python installation directories`n"
        Write-Host "    - Run this script again, after ensuring the above`n"

        Write-Host "`nFurther troubleshooting - try these options the previous steps didn't work:" -ForegroundColor Magenta
        Write-Host "    - Input the path to your 'virtualenv.exe' program, located in the 'Scripts' directory of your python3 installation, and I will try to create the virtual environment using it. (This way, you don't need to modify your system PATH)`n"
        Write-Host "    - Create the python virtual environment manually: must be named 'py-venv', located in the root of the MLU project folder, and use python3.7. Then run the script again with the -UseExistingVenv parameter."

        # Try to use a non-default virtualenv path that the user enters
        do {
            $continue = Read-Host -Prompt "Proceeding - please enter 'P' to input your path to 'virtualenv.exe' and retry the setup, or enter 'Q' to quit"

            if ($continue -eq 'q') {
                throw "Exiting due to choice of user"
            
            } elseif ($continue -ne 'p') {
                Write-Host "Incorrect response: Enter P or Q" -ForegroundColor Red
            }
        
        } while ($continue -ne 'p') 

        $venvCustomPath = Read-Host -Prompt "Please enter the path of the python3 'virtualenv.exe' program installed on your system"
        Write-Host "Attempting to use virtualenv.exe at $venvCustomPath" -ForegroundColor Cyan

        # Check that the path is valid
        # TODO: CHECK THAT THIS VENV EXE USES PYTHON3.7 (repeat same process as before)
        if (Test-Path -Path $venvCustomPath) {
            $x = "C:\Libs\Python\3.7\Scripts\virtualenv.exe"
            & $x $pythonVenvLocation

            if (Test-Path -Path $pythonVenvLocation) {
                Write-Host "Virtual environment 'py-venv' appears to have been created successfully" -ForegroundColor Cyan
                Write-Host "Activating virtual environment 'py-venv'" -ForegroundColor Cyan
                .\py-venv\Scripts\activate
            }

        } else {
            Write-Host "Specified virtualenv file not found: $venvCustomPath" -ForegroundColor Red
            throw "Error: file not found"
        }
    }
}





Write-Host "Installing Pip packages into virtual environment" -ForegroundColor Cyan
pip install -r ./requirements.txt



