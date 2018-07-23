python setup.py sdist bdist_wheel

:: I don't need these directories for now, so I won't use them
:: RMDIR /S /Q dist\
RMDIR /S /Q build\
RMDIR /S /Q radie.egg-info\
