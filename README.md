# CS50-Finance-App
## Description
This is a simple Python Flask web app via which you can manage portfolios of stocks. Not only will this tool allow you to check real stocks’ actual prices and portfolios’ values, it will also let you "buy" and "sell" stocks by querying IEX for stocks’ prices.
## Usage
### Obtain an API KEY 
* Visit iexcloud.io/cloud-login#/register/.
* Enter your email address and a password, and click “Create account”.
* On the next page, scroll down to choose the Start (free) plan.
* Once you’ve confirmed your account via a confirmation email, sign in to iexcloud.io.
* Click API Tokens.
* Copy the key that appears under the Token column (it should begin with pk_).
### Download the project's code
* `git clone` the project's url in an empty directory
* `cd CS50-Finance-App`
* `pip install virtualenv`
* `virtualenv venv`
* `venv/source/bin/activate` or `source venv/Scripts/activate` if you are running gitbash on windows
* `pip install -r requirements.txt`
* `export FLASK_APP=application.py`
* `export API_KEY={"API_KEY you obtained from IEX cloud"}`
* `flask run`
* Your code should run okay. See images of the project
* Image 1 \
![finance app 1](https://user-images.githubusercontent.com/21335004/135710457-9f8f4048-9438-4d59-9f72-65ec55998034.PNG)
* Image 2 \
![finance app2](https://user-images.githubusercontent.com/21335004/135710465-b13e1bc3-7ac7-4d01-8c21-fe7ed5009f86.PNG)
* Image 3 \
![finance app4](https://user-images.githubusercontent.com/21335004/135710483-c826f1aa-0bec-4fad-a1dc-0e596d842648.PNG)
