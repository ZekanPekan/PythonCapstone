# Parse GridDynamics Blog with Scrapy and visualize it
A parser for GridDynamics blog and a report that will show:
* Top-5 Authors,
* Top-5 New Articles,
* Plot with articles counter of 7 most popular tags

## How to
### Setup
It's recommended that you create virtual environment first and operate within it. 
Commands described here are recommended to be executed from the project root folder. 

* Run `pip install -r requirements.txt` to install all dependencies
### Run app
* Run `python3 report.py` to execute crawling and generate report
### Run tests
 * Run `python3 tests.py` to execute test, you should get response like this [here](tests_result.png)
