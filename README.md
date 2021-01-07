# Firefox Lockwise Validator

Over time, data can get messy and become duplicated. This simple script aims to read a **local** copy of your Firefox Lockwise passwords in order to generate a report on bad data. At the time of creation, Firefox does not support re-importing a modified version of the Firefox export, so this report performs read-only operations - your data is not manipulated or cleaned automatically, but you can use the results, to perform manual cleanup in your Lockwise vault.

To use the script, export your Lockwise password .csv, drop the file in the same directory as the `dedupe.py` script, and run.
  
## Exporting Firefox Lockwise Credentials

1. Launch Firefox, sign in, and browse to [about:logins](about:logins)
2. In the top-right corner, next to your user profile icon, click the `...`
3. Choose **Export Logins...**
4. Accept the warning
   * Note that passwords will be stored in plain text - protect this file!
5. Save the file. The default name is `logins.csv`, which the script is expecting. Save to the same directory as the `dedupe.py` file

## Supported Reports

* Blank usernames
* Blank/invalid passwords
	* Password validation is *very* limited. Checking for weak passwords is not in scope for this script at this time
* Duplicate entries by website

## Requirements

* Mac: `pip3 install pandas tabulate`
* Windows: `pip install pandas tabulate`