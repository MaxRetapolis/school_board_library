
@echo off
C:/Users/Maxim/AppData/Local/Programs/Python/Python312/python.exe -m venv venv
call venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
echo Virtual environment setup complete.