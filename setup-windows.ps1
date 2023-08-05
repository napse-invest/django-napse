winget install python3
python.exe -m pip install --upgrade pip
python.exe -m pip install virtualenv

if (Test-Path ".\.venv" -PathType Container) {
   	Remove-Item -Path .venv -Recurse -Force
	Write-Host "Old virtual env have been removed"
}

python.exe -m venv .venv
Write-Host "Virtual env have been created"


Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.venv\Scripts\Activate.ps1
Write-Host "Virtual env is now activated "

python.exe -m pip install --upgrade pip
python.exe -m pip install pip-tools
pip-compile .\backend\requirements\development.txt --output-file .\full-requirements.txt --resolver=backtracking
python -m pip install -r .\full-requirements.txt

Write-Host "Have fun with coding"