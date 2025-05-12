weekday_dict = ["пн", "вт", "ср", "чт", "пт", "сб", "вс"]
stroka = "пн-чт 12:00–00:00; пт,сб 12:00–02:00; вс 12:00–00:00"

def check_datetime(dt, weekday, timed):
    date = False
    time = False
    if "ежедневно" in dt:
        date = True
        if "круглосуточно" in dt:
            time = True
        else:
            data1 = dt.split(", ")[1].split("–")
            data1.append(timed)
    else:
        data = dt.split("; ")
        data = [i.split(" ") for i in data]
        for i in data:
            if weekday_dict.index(i[0][:2]) <= weekday <= weekday_dict.index(i[0][-2:]):
                date = True
                if "круглосуточно" in i[1]:
                    time = True
                else:
                    data1 = i[1].split("–")
                    data1.append(timed)
                break

    if date and not time:
        for i in range(len(data)):
            data[i] = data[i][:2]
            if data[i][0] == "0":
                data[i] = data[i][1]
            data[i] = int(data[i])
        num1, num2, num3 = data
        if num2 < num1:
            num2 += 24
        if num1 <= num3 <= num2 - 1:
            time = True
        if date and time:
            return True
        return False




print(check_datetime(stroka, 6, "01:53"))
