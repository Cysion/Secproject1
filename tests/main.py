#!/bin/python

# Functional tests for application 'twelvesteps'


from sys import exit, stderr
from time import sleep
from selenium import webdriver
from selenium.webdriver.support.ui import Select
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
url_list["profile_edit"] = url_list["profile"] + 'edit/'
url_list["prepare"] = url_list["base"] + 'prepare/'


credentials = {
    'email': 'robin_hood25@gmail.com',
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
    sleep(wait_time + 1)

    # Save private key and verify redirection
    if browser.current_url != url_list["backupkey"]:
        raise ApplicationFunctionError('Did not get redirected to backup-key URL after registration: Assmuming registration with selected credentials failed.')

    credentials["priv_key"] = browser.find_element_by_class_name("form-control").get_attribute("value")


def test_valid_login():

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


def test_edit_credentials():
    pass


def test_prepare_page1():
    browser.get(url_list["prepare"] + '1/')
    sleep(wait_time)


def test_prepare_page2():
    browser.get(url_list["prepare"] + '2/')
    sleep(wait_time)


def test_prepare_page3():
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
    browser.get(url_list["prepare"] + '6/')
    sleep(wait_time)


def test_prepare_page7():
    browser.get(url_list["prepare"] + '7/')
    sleep(wait_time)

    # Add diary-entry
    browser.find_element_by_id("date").send_keys(credentials["birth"])
    browser.find_element_by_id("text").send_keys("This is my new diary entry")
    browser.find_element_by_id("text").submit()


def test_prepare_page8():
    browser.get(url_list["prepare"] + '8/')
    sleep(wait_time)

    # Add therapy-entry
    browser.find_element_by_id("date").send_keys(credentials["birth"])
    browser.find_element_by_id("text").send_keys("This is my new therapy entry")
    browser.find_element_by_id("text").submit()


def test_prepare_plan():
    """ Tests entire prepare plan """

    test_prepare_page1()
    test_prepare_page2()
    test_prepare_page3()
    test_prepare_page4()
    test_prepare_page5()
    test_prepare_page6()
    test_prepare_page7()
    test_prepare_page8()

    # Navigate to start
    browser.get(url_list["prepare"])
    sleep(wait_time)
    
    # Page 2
    browser.get(url_list["prepare"] + '2/')
    sleep(wait_time)

    # Page 3
    browser.get(url_list["prepare"] + '3/')
    sleep(wait_time)

    # Page 4
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

    # Page 5
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

    # Read page 6
    browser.get(url_list["prepare"] + '6/')
    sleep(wait_time)

    # Page 7
    browser.get(url_list["prepare"] + '7/')
    sleep(wait_time)

    # Add diary-entry
    browser.find_element_by_id("date").send_keys(credentials["birth"])
    browser.find_element_by_id("text").send_keys("This is my new diary entry")
    browser.find_element_by_id("text").submit()

    # Page 8
    browser.get(url_list["prepare"] + '8/')
    sleep(wait_time)

    # Add therapy-entry
    browser.find_element_by_id("date").send_keys(credentials["birth"])
    browser.find_element_by_id("text").send_keys("This is my new therapy entry")
    browser.find_element_by_id("text").submit()


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

    # -- Select tests to run --
    tests = []
    tests.append(('test_start_page', test_start_page))
    tests.append(('test_invalid_login', test_invalid_login))
    tests.append(('test_create_account', test_create_account))
    tests.append(('test_valid_login', test_valid_login))
    tests.append(('test_login_session', test_login_session))
    tests.append(('test_prepare_plan', test_prepare_plan))

    print("\n-- Running tests --")
    print("> Test count: " + str(len(tests)))

    # Perform tests
    print("")
    for test in tests:
        print("* Running test: " + test[0] + "... ", end = '')
        try:
            test[1]()
        except Exception as e:
            print("Failed")
            error(test[0], str(e))
        else:
            print("Passed")

    # Quit
    print("\n> Tests complete")
    print("Testing finnished\n")
    browser.quit()
    exit(0)


if __name__ == '__main__':
    main()

