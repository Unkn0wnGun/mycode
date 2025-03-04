from concurrent.futures import ProcessPoolExecutor, as_completed
import os
from colorama import Fore
from tkinter import filedialog, Tk
import sqlite3
from rich.live import Live
from rich.console import Console
import time

def bar(sim, contador, falta, total, size, lev):
    
    display_text = f"""

        [bold]INFORMAÇÕES[/bold]

[bold]Total Files[/bold]: {total}
[bold]Size[/bold]: {size / (1024 * 1024):.2f} MB

[bold]Simultaneamente[/bold]: [magenta]{sim}[/magenta]
[bold]Terminado[/bold]: [green]{contador}[/green]
[bold]Falta Terminar[/bold]: [blue]{falta}[/blue]

[bold]Duração[/bold]: [blue]{lev} minutos[/blue]

"""
    return display_text

def adc(tudo, id):

    p = 'txt_sql'
    if not os.path.exists(p):
        os.mkdir(p)

    con = sqlite3.connect(f'{p}/cloud_conv_{id}.db')
    cur = con.cursor()
    cur.execute('PRAGMA synchronous = OFF;')
    cur.execute('PRAGMA journal_mode = OFF;')
    cur.execute('PRAGMA temp_store = MEMORY;')
    cur.executemany('''
        INSERT INTO info (url, email, senha) VALUES (?, ?, ?)
    ''', tudo)

    con.commit()
    con.close()


def criar(id):
    p = 'txt_sql'
    if not os.path.exists(p):
        os.mkdir(p)

    con = sqlite3.connect(f'{p}/cloud_conv_{id}.db')
    cur = con.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS info (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT,
            email TEXT,
            senha TEXT
        )
    ''')
    con.commit()
    cur.close()
    con.close()


def pros(path, txt: str, id):

    criar(id)

    with open(f'{path}/{txt}','r', errors='replace', encoding='utf-8') as pes:

        mod = map(lambda x: x.replace(' ',':').replace(';',':').replace('|',':').strip().replace('www.','').replace('\x00','').replace('"','').replace("'",'').replace('android://','').replace('http://','').replace('https://','')
        if x.replace('http://','').replace('https://','').count(':') < 2
        else x.strip().replace('www.','').replace('\x00','').replace('"','').replace("'",'').replace(' ','').replace('android://','').replace('http://','').replace('https://',''), pes)
        
        ss1 = map(lambda x: x.split(':')[0:1] + x.split(':')[2:4] if len(x.split(':')) > 3
                else x.split(':')[0:3]
                if len(x.split(':')) > 2 else None, mod)
        
        ss = filter(lambda x: x, ss1)

        adc(ss, id)

    return


def main():

    print(f'''{Fore.BLUE}

   [-;-/=_
    `-; \=_       ___
      ) ,"-...--./===--__
    __|/      /  ]`
   /;--> >...-\ <\_
   `- <<,      7/-.\,
   ck  `-     /(   `-

{Fore.RESET}''')

    try:
        root = Tk()
        root.withdraw()

        files = filedialog.askdirectory(title='Pasta')
        gz = 0
        lfs = [fi for fi in os.listdir(files) if fi.endswith('.txt')]
        gz = sum([os.path.getsize(f'{files}/{fi}') for fi in os.listdir(files) if fi.endswith('.txt')])
        
        total = len(lfs)
        try:
            mw = int(input('Converte Quantos arquivos simultaneamente: '))
        except:
            mw = 2
            print(f'{Fore.CYAN}Quantos simultaneamente: 2{Fore.RESET}')
        
        ni = time.time()
        with Live(console=console, refresh_per_second=4) as live:
            with ProcessPoolExecutor(max_workers=mw) as wp:
                r = [wp.submit(pros, files, lf, id) for id, lf in enumerate(lfs, start=1)]
                contador = 0

                live.update(bar(mw, contador, total, total , gz, 0))
                tota = total
                for rr in as_completed(r):
                    lev = f'{(time.time()-ni)/60:.2f}'
                    contador += 1
                    tota -= 1
                    rr.result()
                    live.update(bar(mw, contador, tota, total , gz, lev))

        print(f'{Fore.GREEN}Finalizado. Levou: {(time.time()-ni)/60:.2f} minutos\n\n{Fore.RESET}')

    except Exception as e:
        print(e)


if __name__ == '__main__':
    console = Console()
    main()

