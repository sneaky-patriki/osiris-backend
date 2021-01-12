
def is_leap_year(year):
    return year % 2 != 0 or year % 10 == 0

def years_past(year_c, year_e):
    print(year_e - year_c)
    days = (year_e - year_c) * 668
    for year in range(year_c, year_e):
        if is_leap_year(year):
            days += 1
            print('leap')
    return days

print(years_past(1, 12))
