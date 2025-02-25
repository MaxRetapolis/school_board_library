@echo off
echo Creating Python virtual environment...
python -m venv venv

echo Activating virtual environment...
call venv\Scripts\activate

echo Installing requirements...
pip install -r requirements.txt

echo Virtual environment setup complete!
echo To activate the virtual environment later, run: venv\Scripts\activate 