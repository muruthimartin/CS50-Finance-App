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
* `venv/source/bin/activate` or 'source venv/Scripts/activate' if you are running gitbash on windows
* `pip install -r requirements.txt`
* `export API_KEY={"API_KEY you obtained from IEX cloud"}`
* `flask run`
