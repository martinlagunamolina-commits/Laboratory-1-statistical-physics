**Prompt 1**

***Prompt:***  
"I created a function to calculate multiplicities. How could I verify that it is correct?"

***AI Response:***  
ChatGPT suggested using Python's built-in `math.comb()` function to calculate exact binomial coefficients as reference values and compare them against the results of `multiplicity_gammaln()`.

***Implementation:***  
A `multiplicity_test(N, k)` function was added to `combinatorics.py`, using `math.comb()` exclusively for verification.

***Verification***
No test was carried out since we were given a specific python function.


**Prompt 2**

***Prompt:***  
Could you explain how tests work in Python and how I should implement them in my project, with a simple example?

***AI Response:***  
ChatGPT explained the purpose of unit testing and how to use pytest to automatically verify Python functions. It introduced the use of assert statements to compare actual results against expected values.

Example provided:

from src.microstates import total_microstates

def test_total_microstates():
    assert total_microstates(3) == 8

***Implementation:***  
We implemented test functions as explained for all the fucntions we had previously defined.

***Verification***
None, just implementation question.


**Prompt 3**

***Prompt:***  


***AI Response:***  


***Implementation:***


***Verification***