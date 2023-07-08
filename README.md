# Setting
Install packages:
```
pip3 install django
pip3 install django-boost
pip3 install pandas
pip3 install numpy
pip3 install mplfinance
```
Install `TA-Lib`:
```
# Mac
brew install ta-lib
pip3 install TA-Lib
# Linux
wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz
tar -xzf ta-lib-0.4.0-src.tar.gz
cd ta-lib
sudo make
sudo make install
pip3 install TA-Lib
```

# Generate and set SECRET KEY
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



