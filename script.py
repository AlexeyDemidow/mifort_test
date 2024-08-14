import time
import re

from playwright.sync_api import Playwright, sync_playwright, expect
from bs4 import BeautifulSoup
import pandas as pd

args = [
    '--disable-blink-features=AutomationControlled',
    '--lang=en-EN'
]


def login_to_google_account(page):
    page.goto("https://myaccount.google.com/")
    page.get_by_role("link", name="Go to your Google Account").click()
    page.get_by_label("Email or phone").fill(g_email)
    time.sleep(0.5)
    page.get_by_role("button", name="Next").click()
    page.get_by_label("Enter your password").fill(g_password)
    time.sleep(0.5)
    page.get_by_role("button", name="Next").click()
    time.sleep(0.5)
    page.get_by_role("list").locator("li").filter(has_text="Personal info").click()
    time.sleep(0.5)


def edit_name_of_google_account(playwright: Playwright) -> None:
    first_name = input('Введите новое имя.\n')
    last_name = input('Введите новую фамилию.\n')
    print('Ожидайте.')

    browser = playwright.chromium.launch(headless=False, args=args, slow_mo=100)
    context = browser.new_context()
    page = context.new_page()

    login_to_google_account(page)

    page.get_by_role('link', name='Name').click()
    time.sleep(1)
    page.get_by_role("button", name="Edit Name").click()
    time.sleep(1)
    page.get_by_label("First name").fill(f"{first_name}")
    page.get_by_label("Last name").fill(f"{last_name}")
    time.sleep(1)
    page.locator("button").filter(has_text="Save").click()
    print('Имя и фамилия успешно изменены.')
    print()

    context.close()
    browser.close()


def edit_password_of_google_account(playwright: Playwright):
    g_new_password = input('Введите новый пароль.\n')
    print('Ожидайте.')

    browser = playwright.chromium.launch(headless=False, args=args, slow_mo=100)
    context = browser.new_context()
    page = context.new_page()

    login_to_google_account(page)

    page.get_by_role('link', name='Password').click()
    time.sleep(0.5)
    page.get_by_label("New password", exact=True).fill(f"{g_new_password}")
    page.get_by_label("Confirm new password").fill(f"{g_new_password}")
    time.sleep(0.5)
    page.locator("button").filter(has_text="Change password").click()
    time.sleep(0.5)
    print('Пароль успешно изменен.')
    print()

    context.close()
    browser.close()

    return g_new_password


def save_data_of_google_account(playwright: Playwright) -> None:
    print('Личные данные пользователя будут сохранены в файл user_data.csv')
    print('Ожидайте.')

    browser = playwright.chromium.launch(headless=False, args=args, slow_mo=100)
    context = browser.new_context()
    page = context.new_page()

    login_to_google_account(page)

    p = page.content()
    soup = BeautifulSoup(p, 'html.parser')
    data = []
    data_dict = {}
    for n in soup.find_all('div', class_='ugt2L aK2X8b t97Ap iDdZmf'):
        data.append(n.text)
    for d in data:
        if 'Name' in d:
            data_dict['name'] = d.removesuffix('chevron_right').removeprefix('Name')
        if 'Birthday' in d:
            data_dict['date_of_birth'] = d.removesuffix('chevron_right').removeprefix('Birthday')
    data = []
    for e in soup.find_all('div', class_='ugt2L aK2X8b iDdZmf'):
        data.append(e.text)
    for d in data:
        if 'Email' in d:
            if len(re.findall(r'.+?.com', d.removesuffix('chevron_right').removeprefix('Email'))) > 1:
                data_dict['email'] = re.findall(r'.+?.com', d.removesuffix('chevron_right').removeprefix('Email'))[0]
                data_dict['reserve_email'] = re.findall(
                    r'.+?.com',
                    d.removesuffix('chevron_right').removeprefix('Email')
                )[1]
            else:
                data_dict['email'] = re.findall(r'.+?.com', d.removesuffix('chevron_right').removeprefix('Email'))[0]
                data_dict['reserve_email'] = None
    data_dict['password'] = g_password
    df = pd.DataFrame(data=data_dict, index=[0])
    df.to_csv('user_data.csv', sep=';')
    print('Данные сохранены.')
    print()

    context.close()
    browser.close()


def login_to_twitter_account(page, page1):
    page.goto("https://twitter.com/")
    page.get_by_test_id("loginButton").click()
    time.sleep(1)
    page.locator("label div").nth(3).click()
    page.get_by_label("Phone, email address, or username").fill(tw_email)
    page.get_by_role("button", name="Next").click()
    time.sleep(1)
    page.get_by_test_id("ocfEnterTextTextInput").fill(tw_name)
    page.get_by_test_id("ocfEnterTextNextButton").click()
    time.sleep(1)
    page.get_by_label("Password", exact=True).fill(tw_password_old)
    page.get_by_test_id("LoginForm_Login_Button").click()
    time.sleep(1)

    page1.goto("https://www.mail.com/")
    page1.reload()
    time.sleep(1)
    page1.get_by_role("link", name="Log in").click()
    page1.get_by_placeholder("Email address").fill(tw_email)
    page1.get_by_placeholder("Password").click()
    page1.get_by_placeholder("Password").fill(tw_email_password)
    page1.get_by_role("button", name="Log in").click()
    page1.locator("[data-test=\"actions-menu__visible\"] [data-test=\"actions-menu__item-mail\"]").click()
    page1.frame_locator("[data-test=\"third-party-frame_mail\"]").get_by_text(
        "Your X confirmation code is").first.click()
    code = page1.frame_locator("[data-test=\"third-party-frame_mail\"]").get_by_text(
        "Your X confirmation code is").first.text_content().split(' ')[-1]
    time.sleep(1)

    page.get_by_test_id("ocfEnterTextTextInput").fill(code)
    page.get_by_test_id("ocfEnterTextNextButton").click()
    time.sleep(1)


def reset_password_of_twitter_account(playwright: Playwright):
    tw_password_new = input('Введите новый пароль.\n')
    print('Ожидайте.')
    browser = playwright.chromium.launch(headless=False, args=args)
    context = browser.new_context()
    page = context.new_page()
    page1 = context.new_page()

    login_to_twitter_account(page, page1)

    page.get_by_test_id("AppTabBar_More_Menu").click()
    time.sleep(1)
    page.get_by_test_id("settings").click()
    time.sleep(1)
    page.get_by_role("tab", name="Change your password Change").click()
    time.sleep(1)
    page.get_by_label("Current password").fill(tw_password_old)
    page.get_by_label("New password").fill(tw_password_new)
    page.get_by_label("Confirm password").fill(tw_password_new)
    time.sleep(1)
    page.get_by_test_id("settingsDetailSave").click()
    time.sleep(1)
    print('Пароль успешно изменен.')
    print()

    context.close()
    browser.close()

    return tw_password_new


def add_twit_to_twitter_account(playwright: Playwright) -> None:
    twit = input('Введите текст твита:\n')
    print('Ожидайте.')

    browser = playwright.chromium.launch(headless=False, args=args)
    context = browser.new_context()
    page = context.new_page()
    page1 = context.new_page()

    login_to_twitter_account(page, page1)

    page.get_by_test_id("AppTabBar_Home_Link").click()
    time.sleep(1)
    page.get_by_test_id("tweetTextarea_0").fill(twit)
    time.sleep(1)
    page.get_by_test_id("tweetButtonInline").click()
    time.sleep(1)
    print('Твит успешно добавлен.')
    print()

    context.close()
    browser.close()


while True:
    print('Скрипт для работы с Google и Twitter аккаунтом.')
    print('Для выполнения операций введите нужную цифру.')
    print('Для работы с Twitter аккаунтом введите 1.')
    print('Для работы с Google аккаунтом введите 2.')
    print('Для выхода введите "q".')
    service_choice = input()

    if service_choice == '1':
        print('Для начала работы с Twitter введите Email пользователя, пароль от почты, Имя пользователя и пароль.')
        print()

        tw_email = input('Введите Email:\n')
        tw_email_password = input('Введите пароль от почты пользователя.\n')
        tw_name = input('Введите Имя:\n')
        tw_password_old = input('Введите пароль:\n')
        print()

        while True:
            print('Меню:')
            print('1. Изменить пароль.')
            print('2. Добавить твит с вашим текстом.')
            print('q - чтобы вернуться назад.')

            choice = input()

            with sync_playwright() as playwright:
                if choice == '1':
                    tw_password_old = reset_password_of_twitter_account(playwright)
                elif choice == '2':
                    add_twit_to_twitter_account(playwright)
                elif choice == 'q' or choice == 'й':
                    print('Выход')
                    break

    elif service_choice == '2':
        print('Для начала работы с Google аккаунтом введите Email пользователя и пароль.')
        print()

        g_email = input('Введите Email:\n')
        g_password = input('Введите пароль:\n')
        print()

        while True:
            print('Меню:')
            print('1. Изменить имя и фамилию пользователя.')
            print('2. Изменить пароль.')
            print('3. Сохранение данных в таблицу: Имя и фамилия, Email, резервный Email, пароль.')
            print('q - чтобы вернуться назад.')

            choice = input()

            with sync_playwright() as playwright:
                if choice == '1':
                    edit_name_of_google_account(playwright)
                elif choice == '2':
                    g_password = edit_password_of_google_account(playwright)
                elif choice == '3':
                    save_data_of_google_account(playwright)
                elif choice == 'q' or choice == 'й':
                    print('Выход')
                    break

    elif service_choice == 'q' or service_choice == 'й':
        print('Выход')
        break
