## Setting
### Install
Python packages:
```
pip3 install django
pip3 install django-boost
pip3 install pandas
pip3 install numpy
pip3 install mplfinance
pip3 install selenium
pip3 install bs4
```
Setting selenium:
```
# Ubuntu
sudo apt install python3-selenium
```
`TA-Lib`:
```
# Mac
brew install ta-lib
pip3 install TA-Lib
# Linux
wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz
tar -xzf ta-lib-0.4.0-src.tar.gz
cd ta-lib
./configure --prefix=/usr
sudo make
sudo make install
pip3 install TA-Lib
```
Others:
```
# Ubuntu
sudo apt install unzip
```

### Generate and set SECRET KEY
Launch a shell:
```
python3 manage.py shell
```
Generate and print SECRET KEY:
```
from django.core.management.utils import get_random_secret_key
get_random_secret_key()
exit()
```
Then copy `settings_local_sample.py` as `secret_local.py` and replace `{}` in settings_local.py



