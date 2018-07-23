python setup.py sdist bdist_wheel

:: delete the old wheel file and put in the new one
:: COPY dist\radie*.whl distribution\

:: I don't need these directories for now, so I won't use them
:: RMDIR /S /Q dist\
:: RMDIR /S /Q build\
RMDIR /S /Q radie.egg-info\
