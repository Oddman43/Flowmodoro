import sqlite3
import pendulum
from datetime import datetime, timedelta
import time
import os
import pygame


# Lee la db para determianr que valor esta en la tabla break level y devuelve el float associado
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


# Lee la db tabla daily_log para cuando started == hoy y formatea el return de la db de manera bonita
def get_today_cicles() -> list:
    today: str = str(pendulum.now()).split()[0]
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


# Lee la db de projects y crea un diccionario con el id y el proyecto
# Los valores de k:v pueden ser invertidos con el agrumento reverse=True
def get_subs_dict(reverse=False) -> dict:
    con: sqlite3.Connection = sqlite3.connect("flow.db")
    cur: sqlite3.Cursor = con.cursor()
    res = cur.execute("SELECT * FROM projects")
    results: list = res.fetchall()
    con.close()
    prj_dict: dict = {}
    for project in results:
        if reverse:
            prj_dict[project[1]] = project[0]
        else:
            prj_dict[project[0]] = project[1]
    return prj_dict

# Hace query a la db y suma los valores de mins worked dentro del rango indicado
# Returnea la suma de los minutos / 7 en forma de int
def get_last_sevendays_avg() -> int:
    yesterday: str = str(pendulum.yesterday()).split()[0]
    eight_days: str = str(pendulum.now().subtract(days=8)).split()[0]
    con: sqlite3.Connection = sqlite3.connect("flow.db")
    cur: sqlite3.Cursor = con.cursor()
    res = cur.execute(
        "SELECT SUM(mins_worked) FROM daily_log WHERE DATE(started) >= ? AND DATE(started) <= ?",
        (eight_days, yesterday),
    )
    results: list = res.fetchall()
    con.close()
    return int(int(results[0][0]) / 7)


# Hace un query en la db tabla daily_log para started hoy de la suma de los mins trabajados
# Si de querry el resultado es None return 0, sino return el int de la suma mins trabajados
def total_mins_today() -> int:
    today: str = str(pendulum.now()).split()[0]
    con: sqlite3.Connection = sqlite3.connect("flow.db")
    cur: sqlite3.Cursor = con.cursor()
    res = cur.execute(
        "SELECT SUM(mins_worked) FROM daily_log WHERE DATE(started) = ?", (today,)
    )
    result: list = res.fetchall()
    if result[0][0] == None:
        return 0
    else:
        return int(result[0][0])


# Cambia el valor de la tabla break_level que se usa como default para break_level
def change_break_level_default(new_bl: str) -> None:
    con: sqlite3.Connection = sqlite3.connect("flow.db")
    cur: sqlite3.Cursor = con.cursor()
    cur.execute("UPDATE break_level SET break_level = ? WHERE id = 1", (int(new_bl),))
    con.commit()
    con.close()


# Explicaicon de flowmodoro y capacidad de cambiar el bl tanto el dafault como para 1 sesion
# returnea un float que puede ser 0.0  o el bl para la sesion
def start() -> float:
    os.system("cls" if os.name == "nt" else "clear")
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
        f"\n To start working press enter"
        f"\n To change the default break level enter the number corresponding with the break level"
        f"\n To change the break level for this sesion enter '-' followed by the corresponding break level\n"
    )
    while True:
        break_level: str = input(flowmodoro_description)
        if break_level.isdigit():
            if 1 <= int(break_level) <= 3:
                change_break_level_default(break_level)
                return 0.0
            else:
                os.system("cls" if os.name == "nt" else "clear")
                print("Incorrect break level selected")
        elif break_level in ["-1", "-2", "-3"]:
            if break_level == "-1":
                return 5/60
            elif break_level == "-2":
                return 10/60
            elif break_level == "-3":
                return 15/60
            else:
                print("Error")
        else:
            return 0.0


# Query a db para tener una lista de los proyectos activos y input sobre que proyecto se va a trabajar
# Si el proyecto no existe crear y preguntar si se quiere añadir un goal
def working_project() -> str:
    con: sqlite3.Connection = sqlite3.connect("flow.db")
    cur: sqlite3.Cursor = con.cursor()
    res_all = cur.execute("SELECT project, status FROM projects")
    results: list = res_all.fetchall()
    print("Daily projects:")
    prj_list: list = []
    prj_dict: dict = get_subs_dict(reverse=True)
    project: tuple
    for project in results:
        if project[1] == 0:
            print(f"· {project[0].upper()}")
        prj_list.append(project[0])
    working_on: str =  input("On what project are you wokring on this cycle? ").lower()
    if working_on not in prj_dict:
        cur.execute("INSERT INTO projects (project) VALUES (?)", (working_on,))
        con.commit()
        try:
            goal_mins: int = int(input("If you want to create a goal for this project write the number of minutes if you dont want just press enter:\n"))
            prj_id: int = prj_dict[working_on]
            cur.execute("INSERT INTO projects_goal (project_id, goal_mins) VALUES(?,?)", (prj_id, goal_mins))
            con.commit()
        except:
            pass
    elif working_on in prj_dict:
        for i in results:
            if i[0] == working_on and i[1] == 1:
                cur.execute("UPDATE projects SET status = 0 WHERE id = ?", (prj_dict[working_on],))
                cur.execute("UPDATE projects_goal SET status = 0 WHERE id = ?", (prj_dict[working_on],))
                con.commit()
    con.close()
    return working_on


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
    time_started: datetime = pendulum.now()
    timer: int = 1
    while True:
        try:
            while timer:
                os.system("cls" if os.name == "nt" else "clear")
                total_secs: int = timer + (total_worked * 60)
                total_m: int
                total_m, _ = divmod(total_secs, 60)
                total_hours: int
                total_minutes: int
                total_hours, total_minutes = divmod(total_m, 60)
                print(f"Worked today -> {total_hours:02d}:{total_minutes:02d}")
                cycle_m: int
                cycle_m, cycle_seconds = divmod(timer, 60)
                cycle_hours: int
                cycle_minutes: int
                cycle_hours, cycle_minutes = divmod(cycle_m, 60)
                print(f"Current cycle -> {cycle_hours:02d}:{cycle_minutes:02d}:{cycle_seconds:02d}")
                print(f"Working on -> {working_on.upper()}\n")
                workometer_hours: int
                workometer_minutes: int
                workometer_hours, workometer_minutes = divmod(workometer, 60)
                bar: str = progress_bar(total_m, workometer)
                print(
                    f"Workometer -> {workometer_hours:02d}:{workometer_minutes:02d}\n{bar}\n"
                )
                print(f"Press Cntrl + C to end working\n")
                print("Cycles today:\n")
                i: str
                for i in cycles:
                    print(f"{i}")
                time.sleep(1)
                timer += 1
        except KeyboardInterrupt:
            os.system("cls" if os.name == "nt" else "clear")
            time_ended: datetime = pendulum.now()
            break
    while True:
        try:
            accomplished: str = input("What did you accomplish during this cycle?\n")
            break
        except (KeyboardInterrupt, EOFError):
            continue
    time_worked: timedelta = time_ended - time_started
    mins_worked: int = time_worked.in_minutes()
    projects_id: dict = get_subs_dict(reverse=True)
    t_started = time_started.format("YYYY-MM-DD HH:mm:ssZZ")
    t_ended = time_ended.format("YYYY-MM-DD HH:mm:ssZZ")
    t_s_clean = t_started[:22] + ":" + t_started[22:]
    t_e_clean = t_ended[:22] + ":" + t_ended[22:]
    return (projects_id[working_on], t_s_clean, t_e_clean, mins_worked, accomplished)


# Guardar en db el workcycle tuple
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
    while True:
        input("Press enter to start the break ")
        seconds_rest = int((mins_worked * 60) * break_level)
        prog_bar_secs = seconds_rest
        while seconds_rest:
            os.system("cls" if os.name == "nt" else "clear")
            bar = progress_bar(seconds_rest, prog_bar_secs, reverse=True)
            mins: int
            secs: int
            mins, secs = divmod(seconds_rest, 60)
            print(f"Break time: \n" f"{mins:02d}m:{secs:02d}s" f"{bar}")
            time.sleep(1)
            seconds_rest -= 1
        break
    try:
        os.system("cls" if os.name == "nt" else "clear")
        file: str = "C:\\Users\\alber\\Documents\\Flowmodoro\\alarm.wav"
        play_sound(file)
        print("Break time is over")
        input("To continue working press enter:\nNow it is safe to close the program")
        pygame.mixer_music.stop()
    except (KeyboardInterrupt, EOFError):
        pass


def play_sound(file_path: str) -> None:
    pygame.mixer.init()
    pygame.mixer.music.load(file_path)
    pygame.mixer.music.play()


def main():
    # con: sqlite3.Connection = sqlite3.connect("flow.db")
    # cur: sqlite3.Cursor = con.cursor()
    workometer: int = get_last_sevendays_avg()
    total_minutes: int = total_mins_today()
    break_level_select: float = start()
    if break_level_select == 0.0:
        break_level: float = get_break_level()
    else:
        break_level = break_level_select
    while True:
        current_project: str = working_project()
        work_cycle: tuple = work_loop(get_today_cicles(), total_minutes, workometer, current_project)
        # save_cycle(work_cycle)
        break_time(work_cycle[3], break_level)
        total_minutes += work_cycle[3]


if __name__ == "__main__":
    main()
