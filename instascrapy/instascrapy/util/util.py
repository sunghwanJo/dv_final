from random import gauss
from time import sleep as original_sleep

# Amount of variance to be introduced
# i.e. random time will be in the range: TIME +/- STDEV %
STDEV = 0.5
sleep_percentage = 1


def randomize_time(mean):
    allowed_range = mean * STDEV
    stdev = allowed_range / 3  # 99.73% chance to be in the allowed range

    t = 0
    while abs(mean - t) > allowed_range:
        t = gauss(mean, stdev)

    return t


def set_sleep_percentage(percentage):
    global sleep_percentage
    sleep_percentage = percentage/100


def sleep(t, custom_percentage=None):
    if custom_percentage is None:
        custom_percentage = sleep_percentage
    time = randomize_time(t)*custom_percentage
    original_sleep(time)

def scroll_bottom(browser, element, range_int):
    if range_int > 50:
        range_int = 50

    for i in range(int(range_int / 2)):
        browser.execute_script(
            "arguments[0].scrollTop = arguments[0].scrollHeight", element)
        sleep(1)

    return

def format_number(number):
        formattedNum = number.replace(',', '').replace('.', '')
        formattedNum = int(formattedNum.replace('k', '00').replace('m', '00000'))
        return formattedNum