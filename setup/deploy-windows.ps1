# MLU project deployment script for Windows OSs - Powershell script
#
# After cloning the MLU repo from Github and saving it in the directory of choice, run this script
# to setup the project so it can be used. 
#
# Please refer to the README.md on Github or in this directory for setup troubleshooting and for
# information on how to use the features of MLU!

# This script is located in <projectRoot>\setup folder
$pythonVenvLocation = '..\py-venv'
$pipRequirementsLocation = '..\requirements.txt'

function Deploy-MLUProject {

    # Remove pre-exisitng path of the projects virtual environment, if it exists
    Remove-MLUVenvIfExists

    # Create virtual env. and activate it if the version check passes
    if (Test-VenvPythonVersionIsCorrect) {
        Write-Host "Version requirement check passed!" -ForegroundColor Cyan
        Install-MLUPythonPackages

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
            $continue = Read-Host -Prompt "`nTo proceed with setup, please enter 'P' to input your path to 'virtualenv.exe' and retry the setup (alternative method), or enter 'Q' to quit"

            if ($continue -eq 'q') {
                throw "Exiting due to choice of user"
            
            } elseif ($continue -ne 'p') {
                Write-Host "Incorrect response: Enter P or Q" -ForegroundColor Red
            }
        
        } while ($continue -ne 'p') 

        $venvCustomPath = Read-Host -Prompt "Please enter the path of the python3 'virtualenv.exe' program installed on your system"
        Write-Host "Attempting to use virtualenv.exe at $venvCustomPath" -ForegroundColor Cyan

        # Check that the path is valid and that this new virtualenv.exe uses correct python version
=        if (Test-Path -Path $venvCustomPath) {
            if (Test-VenvPythonVersionIsCorrect -VenvExePath $venvCustomPath) {
                Install-MLUPythonPackages -VenvExePath $venvCustomPath
            
            } else {
                throw "Error: Version requirement check failed. $venvCustomPath does not use the required version of python for this project."
            }

        } else {
            throw "Error: Specified virtualenv executable file not found: $venvCustomPath"
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

function Remove-MLUVenvIfExists {
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
        
        Remove-Item -Path $pythonVenvLocation -Recurse -Force
    } 
}

function Install-MLUPythonPackages {
    param(
        [Parameter(Mandatory=$false)]
        [string]$VenvExePath
    )

    Write-Host "Creating python virtual environment 'py-venv', in which MLU dependencies will be installed" -ForegroundColor Cyan

    # run the virtualenv command to make the virtual env.
    # Use the virtualenv exe specified, or use the default one if none is specified
    if ($VenvExePath) {
        & $VenvExePath $pythonVenvLocation
    } else {
        virtualenv $pythonVenvLocation     
    }

    if (Test-Path -Path $pythonVenvLocation) {
        Write-Host "Virtual environment 'py-venv' directory exists - it appears to have been created successfully" -ForegroundColor Cyan
        Write-Host "Activating virtual environment 'py-venv'" -ForegroundColor Cyan
        & "$pythonVenvLocation\Scripts\activate" # run the 'activate' script to activate the virtual env.
    
    } else {
        throw "Error: Virtual environment 'py-env' was not found...there was an issue creating this env. Please see the docs to setup the project manually."
    } 

    Write-Host "Installing Pip packages into virtual environment" -ForegroundColor Cyan
    pip install -r $pipRequirementsLocation
    
}

Deploy-MLUProject










