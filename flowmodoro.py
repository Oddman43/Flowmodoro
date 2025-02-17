import sqlite3
from datetime import datetime, timedelta
import time
import os
import pygame


def get_break_level(selected: int) -> float:
    if selected == 1:
        return 5 / 60
    elif selected == 2:
        return 10 / 60
    elif selected == 3:
        return 15 / 60


def get_today_cicles() -> str:
    today: str = str(datetime.now()).split()[0]
    query: str = (
        f"SELECT project_id, started, ended, mins_worked, accomplished FROM daily_log WHERE DATE(started) = '{today}'"
    )
    results: list = sql_query(query)
    i: int = 1
    cycles_str: str = ""
    projects_dict: dict = get_subs_dict()
    for cicle in results:
        started: list = cicle[1].split()
        started_time: str = f"{started[1].split(':')[0]}:{started[1].split(':')[1]}"
        ended: list = cicle[2].split()
        ended_time: str = f"{ended[1].split(':')[0]}:{ended[1].split(':')[1]}"
        hours, minutes = divmod(int(cicle[3]), 60)
        cicle_formated = f"Cycle {i:02d} -> {started_time} - {ended_time} | {hours:02d}:{minutes:02d} | {projects_dict[cicle[0]].upper()}\n"
        # cicle_formated_accomp = f"Cycle {i:02d} -> {started_time} - {ended_time} | {hours:02d}:{minutes:02d} | {projects_dict[cicle[0]].upper()} | {cicle[4]}\n"
        i += 1
        cycles_str += cicle_formated
    return cycles_str


def get_subs_dict(reverse=False) -> dict:
    query: str = "SELECT * FROM projects"
    results: str = sql_query(query)
    prj_dict: dict = {}
    for project in results:
        if project[2] == 1:
            pass
        else:
            if reverse:
                prj_dict[project[1]] = project[0]
            else:
                prj_dict[project[0]] = project[1]
    return prj_dict


def get_last_sevendays_avg() -> int:
    yesterday: str = str(datetime.now() - timedelta(days=1)).split()[0]
    eight_days: str = str(datetime.now() - timedelta(days=8)).split()[0]
    query: str = (
        f"SELECT SUM(mins_worked) FROM daily_log WHERE DATE(started) >= '{eight_days}' AND DATE(started) <= '{yesterday}'"
    )
    results: list = sql_query(query)
    try:
        avg = int(int(results[0][0]) / 7)
    except TypeError:
        avg = 0
    return avg


def total_mins_today() -> int:
    today: str = str(datetime.now()).split()[0]
    query: str = (
        f"SELECT SUM(mins_worked) FROM daily_log WHERE DATE(started) = '{today}'"
    )
    result: list = sql_query(query)
    return 0 if result[0][0] == None else int(result[0][0])


def start() -> None:
    os.system("cls" if os.name == "nt" else "clear")
    query: str = "SELECT break_level FROM break_level WHERE id = 1"
    result = sql_query(query)
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
        f"    - 3 : offers a break ratio of 15-minute break for every 60 minutes of work.\n\n"
        f"Your selected break level is: {result[0][0]} \nTo start working with this break level press enter\n\n"
        f"To change it enter the int corresponding with you selected Break Level\n\n"
    )
    inp = input(flowmodoro_description)
    try:
        if inp == "":
            selected = int(result[0][0])
        elif int(inp) in [1, 2, 3]:
            sql_insert_update(
                f"UPDATE break_level SET break_level = {int(inp)} WHERE id = 1"
            )
            selected = int(inp)
        else:
            start()
        return get_break_level(selected)
    except ValueError:
        pass


def progress_bar(
    current: int, total: int, length: int = 25, reverse: bool = False
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


def work_loop(cycles: str, total_worked: int, workometer: int, working_on: str) -> int:
    projects_goal: dict = project_goals()
    time_started: datetime = datetime.now()
    timer: int = 1
    while True:
        try:
            while timer:
                os.system("cls" if os.name == "nt" else "clear")
                total_secs: int = timer + (total_worked * 60)
                total_m, _ = divmod(total_secs, 60)
                total_hours, total_minutes = divmod(total_m, 60)
                cycle_m, _ = divmod(timer, 60)
                cycle_hours, cycle_minutes = divmod(cycle_m, 60)
                workometer_hours, workometer_minutes = divmod(workometer, 60)
                print(f"Worked today -> {total_hours:02d}:{total_minutes:02d}")
                print(f"Current cycle -> {cycle_hours:02d}:{cycle_minutes:02d}")
                print(f"Working on -> {working_on.upper()}\n")
                print(
                    f"Workometer -> {workometer_hours:02d}:{workometer_minutes:02d}\n{progress_bar(total_m, workometer)}\n"
                )
                print("Projects progress:")
                print(f"{goals_bar(projects_goal, cycle_m, working_on)}")
                print("Press Cntrl + C to end working\n")
                print("Cycles today:\n")
                print(cycles)
                time.sleep(1)
                timer += 1
        except KeyboardInterrupt:
            os.system("cls" if os.name == "nt" else "clear")
            time_ended: datetime = datetime.now()
            break
    while True:
        try:
            accomplished: str = input("What did you accomplish during this cycle? \n\n")
            break
        except (KeyboardInterrupt, EOFError):
            continue
    time_worked: timedelta = time_ended - time_started
    mins_worked: int = int(time_worked.total_seconds() / 60)
    projects_id: dict = get_subs_dict(reverse=True)
    t_started = str(time_started).split(".")[0]
    t_ended = str(time_ended).split(".")[0]
    query: str = (
        "INSERT INTO daily_log (project_id, started, ended, mins_worked, accomplished)VALUES (?, ?, ?, ?, ?)"
    )
    work_loop_info: tuple = (
        projects_id[working_on],
        t_started,
        t_ended,
        mins_worked,
        accomplished,
    )
    sql_insert_update(query, work_loop_info)
    return mins_worked


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
    except (KeyboardInterrupt, EOFError):
        pass
    try:
        file_path: str = r"C:\Users\alber\Documents\Flowmodoro funct\alarm.wav"
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
    query: str = "SELECT project, status FROM projects"
    results: list = sql_query(query)
    print(
        "If you wish to create a new project add !\n"
        "If you want to see inactive projects input 0\n\n"
    )
    print("Daily projects:")
    for tpl in results:
        if tpl[1] == 0:
            print(f"· {tpl[0].upper()}")
    working = input(
        "On what project are you wokring on this cycle?\n\n"
    ).lower()
    wip = check_wip(working, results)
    return wip


def check_wip(working: str, results):
    check = {i[0]: i[1] for i in results}
    if working in check.keys():
        # si project existe cambiar status a 0 (activo)
        if check[working] == 1:
            sql_insert_update(
                f"UPDATE projects SET status = 0 WHERE project = {working}"
            )
        return working
    else:
        # si empieza con ! crear proyecto
        if working[0] == "!":
            sql_insert_update(
                f"INSERT INTO projects (project) VALUES ({working.replace("!", "")})"
            )
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


def sql_query(query: str, fetch_all=True) -> list:
    con: sqlite3.Connection = sqlite3.connect("flow.db")
    cur: sqlite3.Cursor = con.cursor()
    res = cur.execute(query)
    if fetch_all:
        results = res.fetchall()
    else:
        results = res.fetchone()
    con.close()
    return results


def sql_insert_update(query: str, filler: tuple = ()) -> None:
    con: sqlite3.Connection = sqlite3.connect("flow.db")
    cur: sqlite3.Cursor = con.cursor()
    if len(filler) != 0:
        cur.execute(query, filler)
    else:
        cur.execute(query)
    con.commit()
    con.close


def project_goals() -> dict:
    today: str = str(datetime.now()).split()[0]
    query: str = (
        f"SELECT project_id, mins_worked FROM daily_log WHERE DATE(started) = '{today}'"
    )
    results: list = sql_query(query)
    coding: int = 0
    bir: int = 0
    for i in results:
        # coding
        if i[0] in [1, 3, 5, 7, 8]:
            coding += i[1]
        # bir
        elif i[0] == 2:
            bir += i[1]
    return {"coding": [240, coding], "bir": [60, bir]}


def goals_bar(remaining_time: dict, mins_cycle: int, working_in: str) -> str:
    bar_str: str = ""
    bir_format: str = "BIR -> 01:00\n"
    coding_format: str = "Coding -> 04:00\n"
    subs_dict = {
        "coding": "coding",
        "estadistica": "coding",
        "cs50": "coding",
        "master": "coding",
        "datacamp": "coding",
        "bir": "bir",
        "japanese": None,
        "ics": None,
    }
    if subs_dict[working_in] != None:
        for project, times_list in remaining_time.items():
            time_done: int = times_list[1]
            current_t: int = (
                time_done
                if subs_dict[working_in] != project
                else time_done + mins_cycle
            )
            bar = progress_bar(current_t, times_list[0])
            formated_bar = (
                bir_format + bar + "\n"
                if project == "bir"
                else coding_format + bar + "\n"
            )
            bar_str += formated_bar
    else:
        bar_bir: str = progress_bar(remaining_time["bir"][1], remaining_time["bir"][0])
        bar_coding: str = progress_bar(
            remaining_time["coding"][1], remaining_time["coding"][0]
        )
        bar_str += coding_format + bar_coding + "\n" + bir_format + bar_bir + "\n"
    return bar_str


def main():
    workometer: int = get_last_sevendays_avg()
    break_level: float = start()
    while True:
        mins_worked: int = work_loop(
            get_today_cicles(), total_mins_today(), workometer, select_wip()
        )
        break_time(mins_worked, break_level)


if __name__ == "__main__":
    main()
