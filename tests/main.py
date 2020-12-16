#!/bin/python

# Functional tests for application 'twelvesteps'


from sys import exit, stderr
from time import sleep
from selenium import webdriver
from selenium.common.exceptions import WebDriverException


browser = webdriver.Firefox()
wait_time = 1

url_list = {}
url_list["browser_home"] = r'about:home'
url_list["base"] = r'http://127.0.0.1:8000/'
url_list["login"] = url_list["base"] + 'login/'
url_list["register"] = url_list["login"] + 'register/'
url_list["profile"] = url_list["base"] + 'userprofile/'
url_list["backupkey"] = url_list["profile"] + 'backupkey/'


credentials = {
    'email': 'robin_hood14@gmail.com',
    'password': 'robins_password',

    'first_name': 'Robin',
    'last_name': 'Hood',
    'birth': '1996-03-21',
    'gender': 'Female',

    'is_professional': False,
    'agree_on_terms': True,

    'priv_key': ''
}


def error(name, text):
    # Prints error and gracefully exits

    print("\nError: " + name, file = stderr)
    print("> " + text, file = stderr)
    print("")
    exit(1)


class ApplicationFunctionError(Exception):
    def __init__(self, description):
        self.description = description


# Tests

def test_start_page():
    """ Verify base-url redirects to login-page """

    # Navigate
    browser.get(url_list["base"])
    sleep(wait_time)

    # Verify page
    if browser.current_url != url_list["login"]:
        raise ApplicationFunctionError('Base URL does not redirect to login-page')


def test_invalid_login():

    # Navigate
    browser.get(url_list["login"])
    sleep(wait_time)

    # Post form
    browser.find_element_by_id("email").send_keys(credentials["email"])
    browser.find_element_by_id("password").send_keys(credentials["password"])
    browser.find_element_by_id("password").submit()
    sleep(wait_time)

    # Verify no redirection has been made
    if browser.current_url != url_list["login"]:
        raise ApplicationFunctionError('Got redirected after invalid login: Assmuming login with incorrect credentials passed.')


def test_create_account():

    # Navigate
    browser.get(url_list["login"])
    sleep(wait_time)
    browser.find_element_by_partial_link_text("Register").click()
    sleep(wait_time)
    if browser.current_url != url_list["register"]:
        raise ApplicationFunctionError("Register-button on login page redirects to '" + browser.current_url + "', but should redirect to '" + url_list["register"] + "'")

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
    sleep(wait_time)

    # Save private key and verify redirection
    if browser.current_url != url_list["backupkey"]:
        raise ApplicationFunctionError('Did not get redirected to backup-key URL after registration: Assmuming registration with selected credentials failed.')

    credentials["priv_key"] = browser.find_element_by_class_name("form-control").get_attribute("value")


def test_valid_login():

    # Navigate
    browser.get(url_list["login"])
    sleep(wait_time)

    # Fill and post form
    browser.find_element_by_id("email").send_keys(credentials["email"])
    browser.find_element_by_id("password").send_keys(credentials["password"])
    browser.find_element_by_id("password").submit()
    sleep(wait_time + 1)

    # Verify redirection to profile
    if browser.current_url != url_list["profile"]:
        raise ApplicationFunctionError("Incorrect redirection to '" + browser.current_url + "' after login. Assuming login with selected credentials failed")


def test_login_session():
    """ Verifies automatic login works. OBS! Cookie must be fetched BEFORE this test """

    browser.get(url_list["browser_home"])
    sleep(wait_time)
    browser.get(url_list["profile"])
    sleep(wait_time)

    # Verify login success
    if browser.current_url != url_list["profile"]:
        raise ApplicationFunctionError('Did not get automatically logged in. Automatic login failed.')


def test_info():
    """ Tests info page """
    pass


def test_prepare_plan():
    """ Tests prepare plan """
    # Test add picture
    # Test youtube link
    pass


def test_activate_plan():
    """ Tests to activate plan """
    pass


def test_media_upload():
    """ Verifies valid media gets uploaded correctly """
    pass


def test_excessive_media_upload():
    """ Verifies overly large media gets rejected """
    pass


def test_data_sharing():
    """ Verifies data gets shared between users properly """
    pass

def test_canceled_sharing():
    """ Verifies data doesn't get shared after cancelling """
    pass

def test_forgot_password():
    """ Verifies forgot password function """
    pass

def test_edit_credentials():
    """ Verifies forgot password function """
    pass


def main():

    # Select tests to run
    tests = []
    tests.append(('test_start_page', test_start_page))
    #tests.append(('test_invalid_login', test_invalid_login))
    #tests.append(('test_create_account', test_create_account))
    tests.append(('test_valid_login', test_valid_login))
    tests.append(('test_login_session', test_login_session))

    # Perform tests
    print("\nTest count: " + str(len(tests)))
    for test in tests:
        print("* Running test: " + test[0] + "... ", end = '')
        try:
            test[1]()
        except WebDriverException:
            print("Failed")
            error(test[0], 'WebDriverException occured. Assuming error connecting to site')
        except Exception as e:
            print("Failed")
            error(test[0], str(e))
        else:
            print("Passed")
    print("Tests complete")

    # Quit
    print("\nTesting finnished\n")
    exit(0)


if __name__ == '__main__':
    main()

