import glob
import json
import os
import re
from pathlib import Path

import pandas as pd


def parse_domain(url: str):
    """ Attempt to parse the domain out of the url in order to create a clean string to group by to find duplicates. """
    regex = r"^.*?([\w]+\.\w{2,})$"
    try:
        return re.search(regex, url).group(1).lower()
    except AttributeError:
        print("!! Unable to parse domain for url", url)
        return ""


def validate_password(pw: str):
    """
    Check if a password is valid and return a tuple of (bool, reason)
    This function does not perform checks for strong passwords.
    """
    pw = pw.strip() if pw is not None else ""
    if pw == "":
        return (False, "Password is blank")
    elif len(pw) < 4:
        # 4-digit PINS could be valid
        return (False, "Password is too short")
    elif len(set(list(pw))) == 1:
        # try to catch an edge case found in my data where a password was just "........."
        return (False, "Password is all the same character")

    return (True, "")


def get_pw_filename(fname="logins"):
    """ Attempt to find the logins.csv file in this python file's directory. Fetch the newest file created with 'login' in the name. """
    this_file = Path(__file__)
    glob_str = str(this_file.parent.joinpath(f"*{fname}*.csv"))
    files = glob.glob(glob_str)
    return max(files, key=os.path.getctime) if len(files) > 0 else None


if __name__ == "__main__":
    os.chdir(Path(__file__).parent) # cd to the directory containing this .py file so the report can be written here.

    pw_file = get_pw_filename()
    if not pw_file:
        raise SystemExit(f"!! Exiting. Unable to find a password export file in the directory {os.getcwd()}")
    
    df = pd.read_csv(pw_file)
    df = df.loc[df["url"] != "chrome://FirefoxAccounts"] # ignore this row when performing checks
    df.fillna("", inplace=True)
    df["parsed_url"] = df["url"].apply(parse_domain)
    df["password_valid"] = df["password"].apply(validate_password)

    pd.set_option('display.max_rows', df.shape[0])
    pd.set_option('display.max_columns', df.shape[1])


    """ Begin region Checks """
    print("Beginning Password validation...")
    
    messages = [] # create a queue of messages for writing to the report file later
    tabulate_kwargs = {
        "index": "never",
        "tablefmt": "pretty",
    }

    # Check for blank usernames
    blank_un_df = df.loc[(df["username"] == "")].copy()
    if blank_un_df.shape[0] > 0:
        cols = ["url"]
        message = f"Found {blank_un_df.shape[0]} blank username(s):\n{blank_un_df[cols].to_markdown(**tabulate_kwargs)}\n"
        print(message)
        messages.append(message)

    # Check for invalid passwords
    invalid_pw_df = df.loc[df["password_valid"] != (True,"")].copy()
    if invalid_pw_df.shape[0] > 0:
        invalid_pw_df["reason"] = invalid_pw_df["password_valid"].apply(lambda x: x[1].strip())
        invalid_pw_df.sort_values(by=["reason", "parsed_url", "username"], inplace=True)
        cols = "url,username,password,reason".split(",")
        message = f"Found {invalid_pw_df.shape[0]} invalid password(s):\n{invalid_pw_df[cols].to_markdown(stralign='left', **tabulate_kwargs)}\n"
        print(message)
        messages.append(message)

    # Check for duplicates using the parsed_url
    dupes_df = df.groupby(by="parsed_url").count()
    dupes_df.reset_index(inplace=True)
    dupes_df.rename(columns={"url":"count"}, inplace=True)
    dupes_df = dupes_df.loc[dupes_df["count"] > 1]
    if dupes_df.shape[0] > 0:
        cols = "parsed_url,count".split(",")
        message = f"Found {dupes_df.shape[0]} potential duplicate site(s):\n{dupes_df[cols].to_markdown(**tabulate_kwargs)}\n"
        print(message)
        messages.append(message)

    print("Password validation complete!")
    """ End region Checks """


    if len(messages) > 0:
        print("Writing report to file...", end="")
        with open("LockwiseReport.txt", 'w') as f:
            f.write("-= Password Validation Report =-" + "\n\n\n")
            for m in messages:
                f.write(m + "\n")
        print("Done.")
