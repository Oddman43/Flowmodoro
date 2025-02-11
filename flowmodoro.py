import sqlite3
from datetime import datetime, timedelta
import time
import os
import pygame


def get_break_level() -> float:
    con: sqlite3.Connection = sqlite3.connect("flow.db")
    cur: sqlite3.Cursor = con.cursor()
    bl = cur.execute("SELECT break_level FROM break_level")
    break_level: int = int(bl.fetchone()[0])
    con.close()
    if break_level == 1:
        return 5 / 60
    elif break_level == 2:
        return 10 / 60
    elif break_level == 3:
        return 15 / 60


def get_today_cicles() -> list:
    today: str = str(datetime.now()).split()[0]
    con: sqlite3.Connection = sqlite3.connect("flow.db")
    cur: sqlite3.Cursor = con.cursor()
    res = cur.execute(
        "SELECT project_id, started, ended, mins_worked, accomplished FROM daily_log WHERE DATE(started) = ?",
        (today,),
    )
    results: list = res.fetchall()
    con.close()
    i: int = 1
    cycles_lst: list = []
    projects_dict: dict = get_subs_dict()
    for cicle in results:
        started: list = cicle[1].split()
        started_time: str = f"{started[1].split(':')[0]}:{started[1].split(':')[1]}"
        ended: list = cicle[2].split()
        ended_time: str = f"{ended[1].split(':')[0]}:{ended[1].split(':')[1]}"
        hours: int
        minutes: int
        hours, minutes = divmod(int(cicle[3]), 60)
        cicle_formated = f"Cycle {i} -> {started[0]} {started_time} | {ended[0]} {ended_time} | Working {hours:02d}:{minutes:02d} | {projects_dict[cicle[0]].capitalize()} | {cicle[4]}"
        i += 1
        cycles_lst.append(cicle_formated)
    return cycles_lst


def get_subs_dict(reverse=False) -> dict:
    con: sqlite3.Connection = sqlite3.connect("flow.db")
    cur: sqlite3.Cursor = con.cursor()
    res = cur.execute("SELECT * FROM projects")
    results: list = res.fetchall()
    con.close()
    prj_dict: dict = {}
    if reverse:
        for project in results:
            if project[2] == 1:
                pass
            else:
                prj_dict[project[1]] = project[0]
        return prj_dict
    else:
        for project in results:
            if project[2] == 1:
                pass
            else:
                prj_dict[project[0]] = project[1]
        return prj_dict


def get_last_sevendays_avg() -> int:
    yesterday: str = str(datetime.now() - timedelta(days=1)).split()[0]
    eight_days: str = str(datetime.now() - timedelta(days=8)).split()[0]
    con: sqlite3.Connection = sqlite3.connect("flow.db")
    cur: sqlite3.Cursor = con.cursor()
    res = cur.execute(
        "SELECT SUM(mins_worked) FROM daily_log WHERE DATE(started) >= ? AND DATE(started) <= ?",
        (eight_days, yesterday),
    )
    results: list = res.fetchall()
    con.close()
    try:
        avg = int(int(results[0][0]) / 7)
    except TypeError:
        avg = 0
    return avg


def total_mins_today() -> int:
    today: str = str(datetime.now()).split()[0]
    con: sqlite3.Connection = sqlite3.connect("flow.db")
    cur: sqlite3.Cursor = con.cursor()
    res = cur.execute(
        "SELECT SUM(mins_worked) FROM daily_log WHERE DATE(started) = ?", (today,)
    )
    result: list = res.fetchall()
    con.close()
    return 0 if result[0][0] == None else int(result[0][0])


def start() -> None:
    os.system("cls" if os.name == "nt" else "clear")
    con: sqlite3.Connection = sqlite3.connect("flow.db")
    cur: sqlite3.Cursor = con.cursor()
    res = cur.execute("SELECT break_level FROM break_level WHERE id = 1")
    result = res.fetchall()
    flowmodoro_description: str = (
        # Que es flowmodoro
        f"FlowModoro:\nA flexible time management tool inspired by Pomodoro technique. "
        f"Start work sessions at your convenience, pause when concentration wanes, and let the system calculate optimal break times. "
        f"Tailored productivity for individual rhythms, whether tackling projects or studying.\n\n"
        # Que es workometer
        f"Workometer is a feature that calculates the average time worked per day over the user's last workweek"
        f"and displays a progress bar to incentivize reaching at least 100% productivity\n\n"
        # Como usar
        f"To start using select a break level:\n"
        f"    - 1 : offers a break ratio of 05-minute break for every 60 minutes of work\n"
        f"    - 2 : offers a break ratio of 10-minute break for every 60 minutes of work.\n"
        f"    - 3 : offers a break ratio of 15-minute break for every 60 minutes of work.\n"
        f"Your selected break level is: {result[0][0]} \nTo start working with this break level press enter\n\n"
        f"To change it enter the int corresponding with you selected Break Level\n"
    )
    inp = input(flowmodoro_description)
    try:
        if int(inp) in [1, 2, 3]:
            cur.execute(
                f"UPDATE break_level SET break_level = ? WHERE id = ?", (int(inp), 1)
            )
            con.commit()
        else:
            start()
    except ValueError:
        pass
    con.close()


def progress_bar(
    current: int, total: int, length: int = 50, reverse: bool = False
) -> str:
    try:
        if reverse:
            percent: float = 100 * ((total - current) / total)
        else:
            percent = 100 * (current / total)
    except ZeroDivisionError:
        percent = 100.0
    if percent < 100:
        filled_length: int = int(percent / 100 * length)
        empty_length: int = length - filled_length
        if reverse:
            bar_format: str = "░" * filled_length + "█" * empty_length
        else:
            bar_format: str = "█" * filled_length + "░" * empty_length
        bar: str = f"|{bar_format}| {percent:.0f}%"
    else:
        full_bar: str = f"█" * length
        bar: str = f"|{full_bar}| 100% Accomplished"
    return bar


def work_loop(
    cycles: list, total_worked: int, workometer: int, working_on: str
) -> tuple:
    time_started: datetime = datetime.now()
    timer: int = 1
    while True:
        try:
            while timer:
                os.system("cls" if os.name == "nt" else "clear")
                total_secs: int = timer + (total_worked * 60)
                total_m, _ = divmod(total_secs, 60)
                total_hours, total_minutes = divmod(total_m, 60)
                print(f"Worked today -> {total_hours:02d}:{total_minutes:02d}")
                cycle_m, _ = divmod(timer, 60)
                cycle_hours, cycle_minutes = divmod(cycle_m, 60)
                print(f"Current cycle -> {cycle_hours:02d}:{cycle_minutes:02d}")
                print(f"Working on -> {working_on.upper()}\n")
                workometer_hours, workometer_minutes = divmod(workometer, 60)
                bar: str = progress_bar(total_m, workometer)
                print(
                    f"Workometer -> {workometer_hours:02d}:{workometer_minutes:02d}\n{bar}\n"
                )
                print(f"Press Cntrl + C to end working\n")
                print("Cycles today:\n")
                for i in cycles:
                    print(f"{i}")
                time.sleep(1)
                timer += 1
        except KeyboardInterrupt:
            os.system("cls" if os.name == "nt" else "clear")
            time_ended: datetime = datetime.now()
            break
    while True:
        try:
            accomplished: str = input("What did you accomplish during this cycle? ")
            break
        except (KeyboardInterrupt, EOFError):
            continue
    time_worked: timedelta = time_ended - time_started
    mins_worked: int = int(time_worked.total_seconds() / 60)
    projects_id: dict = get_subs_dict(reverse=True)
    t_started = time_started.format("YYYY-MM-DD HH:mm:ssZZ")
    t_ended = time_ended.format("YYYY-MM-DD HH:mm:ssZZ")
    t_s_clean = t_started[:22] + ":" + t_started[22:]
    t_e_clean = t_ended[:22] + ":" + t_ended[22:]
    return (projects_id[working_on], t_s_clean, t_e_clean, mins_worked, accomplished)


def save_cycle(work_tuple: tuple) -> None:
    con: sqlite3.Connection = sqlite3.connect("flow.db")
    cur: sqlite3.Cursor = con.cursor()
    cur.execute(
        "INSERT INTO daily_log (project_id, started, ended, mins_worked, accomplished)VALUES (?, ?, ?, ?, ?)",
        work_tuple,
    )
    con.commit()
    con.close()


def break_time(mins_worked: int, break_level: float) -> None:
    os.system("cls" if os.name == "nt" else "clear")
    seconds_rest = int((mins_worked * 60) * break_level)
    prog_bar_secs = seconds_rest
    input("Press enter to start the break ")
    try:
        while seconds_rest:
            os.system("cls" if os.name == "nt" else "clear")
            bar = progress_bar(seconds_rest, prog_bar_secs, reverse=True)
            mins: int
            secs: int
            mins, secs = divmod(seconds_rest, 60)
            print(f"Break time: \n" f"{mins:02d}m:{secs:02d}s" f"{bar}")
            time.sleep(1)
            seconds_rest -= 1
    except(KeyboardInterrupt, EOFError):
        pass
    try:
        file_path: str = "C:\\Users\\alber\\Documents\\Flowmodoro\\alarm.wav"
        print("Break time is over")
        pygame.mixer.init()
        pygame.mixer.music.load(file_path)
        pygame.mixer.music.play()
        input("To continue working press enter: ")
    except (KeyboardInterrupt, EOFError):
        pass
    pygame.mixer.music.stop()


def select_wip() -> str:
    os.system("cls" if os.name == "nt" else "clear")
    con: sqlite3.Connection = sqlite3.connect("flow.db")
    cur: sqlite3.Cursor = con.cursor()
    res = cur.execute("SELECT project, status FROM projects")
    results: list = res.fetchall()
    print("Daily projects:")
    for tpl in results:
        if tpl[1] == 0:
            print(f"· {tpl[0].upper()}")
    working = input(
        "On what project are you wokring on this cycle?\n"
        "If you wish to create a new project add !\n"
        "If you want to see inactive projects input 0\n"
    ).lower()
    wip = check_wip(working, con, cur, results)
    con.close()
    return wip


def check_wip(working: str, con, cur, results):
    check = {i[0]: i[1] for i in results}
    if working in check.keys():
        # si project existe cambiar status a 0 (activo)
        if check[working] == 1:
            cur.execute(
                "UPDATE projects SET status = ? WHERE project = ?", (0, working)
            )
            con.commit()
        return working
    else:
        # si empieza con ! crear proyecto
        if working[0] == "!":
            cur.execute(
                "INSERT INTO projects (project) VALUES (?)", (working.replace("!", ""),)
            )
            con.commit()
            return working
        # si es 0 dar lista de inactive
        elif working == "0":
            print("Inactive projects")
            for k, v in check.items():
                if v == 1:
                    print(f"· {k.upper()}")
            input("Press enter to continue\n")
        # no existe o esta mal escrito
        else:
            input("The project dosent exist, please press enter to selecta again\n")
        return select_wip()


def main():
    # con: sqlite3.Connection = sqlite3.connect("flow.db")
    # cur: sqlite3.Cursor = con.cursor()
    workometer: int = get_last_sevendays_avg()
    start()
    while True:
        work_cycle = work_loop(
            get_today_cicles(), total_mins_today(), workometer, select_wip()
        )
        save_cycle(work_cycle)
        break_time(work_cycle[3], get_break_level())


if __name__ == "__main__":
    main()
