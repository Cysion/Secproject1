#!/bin/python

# Functional tests for application 'twelvesteps'

from sys import exit, stderr
from time import sleep
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import WebDriverException, NoSuchElementException


browser = webdriver.Firefox()
wait_time = 1

url_list = {}
url_list["browser_home"] = r'about:home'
url_list["base"] = r'http://127.0.0.1:8000/'
url_list["login"] = url_list["base"] + 'login/'
url_list["register"] = url_list["login"] + 'register/'
url_list["profile"] = url_list["base"] + 'userprofile/'
url_list["backupkey"] = url_list["profile"] + 'backupkey/'
url_list["profile_edit"] = url_list["profile"] + 'edit/'
url_list["prepare"] = url_list["base"] + 'prepare/'


credentials = {
    'email': 'test_user@gmail.com',
    'password': 'test_password',

    'first_name': 'Test',
    'last_name': 'User',
    'birth': '1996-03-21',
    'gender': 'Female',

    'is_professional': False,
    'agree_on_terms': True,

    'priv_key': ''
}


def error(name, message, solutions = []):
    """ Print error and gracefully exit """

    print("\n-- TEST FAILED --")
    print("> " + name, file = stderr)
    print("")

    # Format, print error message
    message = message.replace('\n', ", ")
    message = message.split(": ", 1)
    if len(message) > 1:
        print("Message: " + message[1], file = stderr)
    else:
        print("Message: " + message[0], file = stderr)
    print("")

    # List possible solutions
    if not solutions:
        print("Possible solutions: Unknown", file = stderr)
    else:
        print("Possible solutions:", file = stderr)
        for solution in solutions:
            print("* " + solution, file = stderr)
    print("")

    exit(1)


# Exception thrown when functional error is detected
class ApplicationFunctionException(Exception):
    def __init__(self, description, solutions = []):
        self.description = description
        self.solutions = solutions


# -- Tests --

def test_start_page():
    """ User enters base URL and gets redirected to startpage """

    # Navigate
    browser.get(url_list["base"])
    sleep(wait_time)

    # Go to login page
    browser.find_element_by_link_text("Login or register here").click()
    sleep(wait_time)


def test_invalid_login():
    """ User tries to login with invalid account """
    # OBS! Requires 'credentials' to be non-registered!

    # Navigate
    browser.get(url_list["login"])
    sleep(wait_time)

    # Post form
    browser.find_element_by_id("email").send_keys(credentials["email"])
    browser.find_element_by_id("password").send_keys(credentials["password"])
    browser.find_element_by_id("password").submit()
    sleep(wait_time + 1)

    # Verify no redirection has been made
    if browser.current_url != url_list["login"]:
        raise ApplicationFunctionException("Got redirected after invalid login", ["User '" + credentials["email"] + "' has already been registered", "Login with incorrect credentials got accepted"])


def test_create_account():
    """ User creates an account """
    # OBS! Requires 'credentials' to be non-registered!

    # Navigate
    browser.get(url_list["login"])
    sleep(wait_time)
    browser.find_element_by_partial_link_text("Register").click()
    sleep(wait_time)

    # Fill and post form
    browser.find_element_by_id("first_name").send_keys(credentials["first_name"])
    browser.find_element_by_id("last_name").send_keys(credentials["last_name"])
    browser.find_element_by_id("date_of_birth").send_keys(credentials["birth"])
    # select gender
    browser.find_element_by_id("email").send_keys(credentials["email"])
    browser.find_element_by_id("password").send_keys(credentials["password"])
    browser.find_element_by_id("repassword").send_keys(credentials["password"])
    if credentials["is_professional"]:
        browser.find_element_by_id("professional").click()
    if credentials["agree_on_terms"]:
        browser.find_element_by_id("agree_terms").click()

    browser.find_element_by_id("email").submit()
    sleep(wait_time + 1)

    # Save private key and verify redirection
    if browser.current_url != url_list["backupkey"]:
        raise ApplicationFunctionException("Did not get redirected to backup-key URL after registration", ["User '" + credentials["email"] + "' has already been registered", "Registration of specified user failed"])

    credentials["priv_key"] = browser.find_element_by_class_name("form-control").get_attribute("value")


def test_logout():
    """ User logs out """
    # OBS! Assumes user is already logged in!

    # Navigate
    browser.get(url_list["login"])
    sleep(wait_time)

    # Log out
    browser.find_element_by_xpath("//*[text()='Logout']").click()
    sleep(wait_time)

    # Verify logged out
    browser.get(url_list["browser_home"])
    sleep(wait_time)
    browser.get(url_list["profile"])
    sleep(wait_time)

    if browser.current_url == url_list["profile"]:
        raise ApplicationFunctionException("User session remains active after logout", ["Logging out does not remove cookie or session"])


def test_valid_login():
    """ User logs in with account """

    # Navigate
    browser.get(url_list["login"])
    sleep(wait_time)

    # If already logged in, log out
    if browser.current_url == url_list["profile"]:
        browser.find_element_by_xpath("//*[text()='Logout']").click()

    # Fill and post form
    browser.find_element_by_id("email").send_keys(credentials["email"])
    browser.find_element_by_id("password").send_keys(credentials["password"])
    browser.find_element_by_id("password").submit()
    sleep(wait_time + 1)

    # Verify redirection to profile
    if browser.current_url != url_list["profile"]:
        raise ApplicationFunctionException("Incorrect redirection to '" + browser.current_url + "' after login", ["Login with credentials for user '" + credentials["email"] + "' failed"])


def test_login_session():
    """ User gets automatically logged in via cookie """

    browser.get(url_list["browser_home"])
    sleep(wait_time)
    browser.get(url_list["profile"])
    sleep(wait_time)

    # Verify login success
    if browser.current_url != url_list["profile"]:
        raise ApplicationFunctionException("Did not get automatically logged in", ["Session cookie unavailable", "Start/login page has been edited or removed"])


def test_edit_credentials():
    """ User edits his/her credentials """

    browser.get(url_list["profile_edit"])
    sleep(wait_time)

    # Change credentials
    credentials["first_name"] = credentials["first_name"] + '_new'
    credentials["last_name"] = credentials["last_name"] + '_new'
    credentials["email"] = credentials["email"].split('@')[0] + '_new@' + credentials["email"].split('@')[1]

    # Change on site
    browser.find_element_by_id("first_name").clear()
    browser.find_element_by_id("first_name").send_keys(credentials["first_name"])
    browser.find_element_by_id("last_name").clear()
    browser.find_element_by_id("last_name").send_keys(credentials["last_name"])
    browser.find_element_by_id("email").clear()
    browser.find_element_by_id("email").send_keys(credentials["email"])
    browser.find_element_by_id("password").send_keys(credentials["password"])
    browser.find_element_by_id("password").submit()
    sleep(wait_time + 1)

    full_name = credentials["first_name"] + ' ' + credentials["last_name"]
    set_name = browser.find_element_by_xpath("//div[@class='profile']/h1").text

    if set_name != full_name:
        raise ApplicationFunctionException("Changed name doesn't match current name", ["Unable to edit user credentials"])


def test_prepare_page1():
    """ User reads saveme-plan page 1 """

    browser.get(url_list["prepare"] + '1/')
    sleep(wait_time)


def test_prepare_page2():
    """ User reads saveme-plan page 2 """

    browser.get(url_list["prepare"] + '2/')
    sleep(wait_time)


def test_prepare_page3():
    """ User adds a memory on saveme-plan page 3 """

    browser.get(url_list["prepare"] + '3/')
    sleep(wait_time)

    # Add memory
    browser.find_element_by_xpath("//*[text()='Add supportive memory']").click()
    sleep(wait_time)

    browser.find_element_by_id("title").send_keys("My memory")
    browser.find_element_by_id("media_text").send_keys("This is the phrase user " + credentials["first_name"] + " entered")
    Select(browser.find_element_by_id("type")).select_by_visible_text('Phrase')
    browser.find_element_by_xpath("//*[text()='Add memory']").click()
    sleep(wait_time)
    browser.find_element_by_xpath("//*[text()='Back']").click()


def test_prepare_page4():
    """ User adds a destructive memory on saveme-plan page 4 """

    browser.get(url_list["prepare"] + '4/')
    sleep(wait_time)

    # Add destructive memory
    browser.get(url_list["base"] + 'prepare/memory/add/?mem_type=d') # Special case due to no identifying tags
    sleep(wait_time)

    browser.find_element_by_id("title").send_keys("My destructive memory")
    browser.find_element_by_id("media_text").send_keys("This is the destructive phrase user " + credentials["first_name"] + " entered")
    Select(browser.find_element_by_id("type")).select_by_visible_text('Phrase')
    browser.find_element_by_xpath("//*[text()='Add memory']").click()
    sleep(wait_time)
    browser.find_element_by_xpath("//*[text()='Back']").click()


def test_prepare_page5():
    """ User adds a new contact on saveme-plan page 5 """

    browser.get(url_list["prepare"] + '5/')
    sleep(wait_time)

    # Add new contact
    browser.find_element_by_xpath("//*[text()='Add new contact']").click()
    sleep(wait_time)

    browser.find_element_by_id("name").send_keys("Test contact name")
    browser.find_element_by_id("phonenumber").send_keys("0734165244")
    browser.find_element_by_id("available").send_keys("test contact availability")
    browser.find_element_by_id("available").submit()
    sleep(wait_time)


def test_prepare_page6():
    """ User reads through saveme-plan page 6 """

    browser.get(url_list["prepare"] + '6/')
    sleep(wait_time)


def test_prepare_page7():
    """ User adds a diary entry on saveme-plan page 7 """

    browser.get(url_list["prepare"] + '7/')
    sleep(wait_time)

    # Add diary-entry
    browser.find_element_by_id("date").send_keys(credentials["birth"])
    browser.find_element_by_id("text").send_keys("This is my new diary entry")
    browser.find_element_by_id("text").submit()


def test_prepare_page8():
    """ User adds a therapy entry on saveme-plan page 8 """

    browser.get(url_list["prepare"] + '8/')
    sleep(wait_time)

    # Add therapy-entry
    browser.find_element_by_id("date").send_keys(credentials["birth"])
    browser.find_element_by_id("text").send_keys("This is my new therapy entry")
    browser.find_element_by_id("text").submit()


def main():

    # -- Select tests to run --
    tests = []
    tests.append(('test_start_page', test_start_page))
    tests.append(('test_invalid_login', test_invalid_login))
    tests.append(('test_create_account', test_create_account))
    tests.append(('test_logout', test_logout))
    tests.append(('test_valid_login', test_valid_login))
    tests.append(('test_login_session', test_login_session))
    tests.append(('test_edit_credentials', test_edit_credentials))
    tests.append(('test_prepare_page1', test_prepare_page1))
    tests.append(('test_prepare_page2', test_prepare_page2))
    tests.append(('test_prepare_page3', test_prepare_page3))
    tests.append(('test_prepare_page4', test_prepare_page4))
    tests.append(('test_prepare_page5', test_prepare_page5))
    tests.append(('test_prepare_page6', test_prepare_page6))
    tests.append(('test_prepare_page7', test_prepare_page7))
    tests.append(('test_prepare_page8', test_prepare_page8))

    print("\n-- RUNNING TESTS --")
    print("> Test count: " + str(len(tests)))

    # Perform tests
    print("")
    for test in tests:
        print("* Running test: " + test[0] + "... ", end = '')
        try:
            test[1]()
        except ApplicationFunctionException as e:
            print("Failed")
            error(
                test[0],
                e.description,
                e.solutions
            )
        except NoSuchElementException as e:
            print("Failed")
            error(
                test[0],
                str(e),
                ["The page has been edited or removed", "A server error has occured"]
            )
        except WebDriverException as e:
            print("Failed")
            error(
                test[0],
                str(e),
                ["Website is offline", "Selenium was closed manually"]
            )
        except Exception as e:
            print("Failed")
            error(test[0], str(e))
        else:
            print("Passed")

    # Quit
    print("\n> Tests completed: " + str(len(tests)))
    print("\n-- TESTING FINISHED --\n")
    browser.quit()
    exit(0)


if __name__ == '__main__':
    main()


