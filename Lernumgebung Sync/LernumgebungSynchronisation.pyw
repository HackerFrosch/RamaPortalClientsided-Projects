import os
import json
import shutil
import subprocess
import sys
from queue import LifoQueue
from tkinter import *
from tkinter import messagebox, filedialog
from threading import Thread



# tooltip class
class ToolTip(object):

    def __init__(self, widget, text):
        self.text = text
        self.widget = widget
        self.tipwindow = None
        self.x = self.y = 0
        self.widget.bind("<Enter>", self.showtip)
        self.widget.bind("<Leave>", self.hidetip)

    def showtip(self, event):
        if self.tipwindow or not self.text:
            return
        x = self.widget.winfo_rootx() + 37
        y = self.widget.winfo_rooty() + 27
        self.tipwindow = tw = Toplevel(self.widget)
        tw.wm_overrideredirect(1)
        tw.wm_geometry("+%d+%d" % (x, y))
        label = Label(tw, text=self.text, justify=LEFT, background=bg_color, foreground=font_color, relief=SOLID, borderwidth=1, font="Helvetia 8")
        label.pack(ipadx=1)

    def hidetip(self, event):
        tw = self.tipwindow
        self.tipwindow = None
        if tw:
            tw.destroy()

# import or install requests and bs4
try:
    import requests
    print("[Info] Packet requests ist installiert!")
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"])
    print("[Info] Packet requests wurde installiert!")
finally:
    import requests

try:
    from bs4 import BeautifulSoup
    print("[Info] Packet bs4 ist installiert!")
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "bs4"])
    print("[Info] Packet bs4 wurde installiert!")
finally:
    from bs4 import BeautifulSoup


# initialize Tkinter root
show_debug_messages = 0
if show_debug_messages == 1:
   print("[Debug] initialize Tkinter root")
root = Tk()
root.wm_title("RaMa-Client Sync")
root.wm_minsize(300, 330)
root.wm_maxsize(300, 330)
root.withdraw()

print(os.path.abspath(__file__))
# some global variables
tmpdir = os.environ["localappdata"].replace("\\", "/") + "/RamaPortal Client"
process_icon_path = os.path.abspath(__file__).replace("LernumgebungSynchronisation.pyw", "process_icon.ico")
root.iconbitmap(process_icon_path)
url = "https://portal.rama-mainz.de"
s = requests.Session()
error_log = []
userdata_reader = ""
userdata = {}
LU_dir = ""
show_password = False
delete_before_sync = BooleanVar()
sync_only_new = BooleanVar()
sync_only_new.set(TRUE)

version = "v4.1"

# color constants
bg_color = "#121212"
font_color = "light grey"
rama_color = "#A51320"
rama_color_active = "#9E1220"


def on_closing(event=""):
    global stopUpdate
    if messagebox.askokcancel("Verlassen", "RaMa-Client Sync verlassen?"):
        userdata_writer = open(tmpdir + "/userdata_client.json", 'w')
        json.dump(userdata, userdata_writer)
        userdata_writer.close()
        stopUpdate = True
        root.destroy()


def check_login():
    return not (BeautifulSoup(s.post(url + "/index.php", {"username": userdata.get("username"), "password": userdata.get(
            "password")}).text, features="html.parser").text.find("angemeldet als") == -1)


def submit_userdata(event=""):
    if show_debug_messages == 1:
        print("[Debug] submitting userdata")
    global userdata_reader, userdata, LU_dir
    userdata_creator = open(tmpdir + "/userdata_LU.json", "w+")
    json.dump({"username": username_entry.get(), "password": password_entry.get(), "dir": dir_entry.get()}, userdata_creator)
    userdata_creator.close()
    del userdata_creator
    # open reader
    userdata_reader = open(tmpdir + "/userdata_LU.json", "r")
    userdata = json.load(userdata_reader)
    userdata_reader.close()
    del userdata_reader
    LU_dir = userdata.get("dir") + "/Lernumgebung OfflineSync"
    if check_login():
        s.get(url + "/index.php?abmelden=1")
    if check_login():
        userdata_frame.pack_forget()
        main_frame.pack(expand=True, fill=BOTH)
    else:
        username_entry.delete(0, END)
        password_entry.delete(0, END)
        messagebox.showerror("Anmeldung fehlgeschlagen!", "Falscher Benutzername oder falsches Passwort")


def insert_dir():
    dir_entry.delete(0, END)
    dir_entry.insert(0, filedialog.askdirectory())


def show_settings():
    main_frame.pack_forget()
    username_entry.delete(0, END)
    password_entry.delete(0, END)
    dir_entry.delete(0, END)
    username_entry.insert(0, userdata.get("username"))
    password_entry.insert(0, userdata.get("password"))
    dir_entry.insert(0, userdata.get("dir"))
    userdata_frame.pack(expand=True, fill=BOTH)


def toggle_show_password():
    global show_password
    if show_password:
        password_entry.config(show="*")
    else:
        password_entry.config(show="")
    show_password = not show_password


def mk_dir(path):
    global error_log
    try:
        try:
            os.mkdir(path)
        except FileExistsError:
            pass
    except Exception as ex:
        error_log.append("Folgender Pfad konnte nicht erstellt werden: ", ex, path)


def download_file(file, dir_string):
    # exclude broken file
    if file.get("name") == "Hallo ihr Lieben, diese Woche beschäftigt ihr euch mit der Gegenreformation.  Dazu erarbeitet ihr die folgenden Aufgaben   1. Informiert euch mit Hilfe des Buches über die einzelnen Schritte der Gegenreformationen (S. 107). 2. S. 113  M3. Aufgabe 1  Arbeiten Sie aus dem Gutachten die Handlungsmöglichkeiten heraus, die der Stadtrat entwickelt. 2. Beurteilt die Bedeutung der Konfessionalisierung für den frühmodernen Staat (S. 108-110).":
        return

    ext = file.get("typ")
    buffer = b""
    if ext == "handschriftl Notiz":
        # not yet implemented
        pass
    elif ext == "tabellenkalkulation":
        # not yet implemented
        pass
    elif ext == "lnk":
        ext = ".url"
        buffer = b"[{000214A0-0000-0000-C000-000000000046}]\nProp3=19,11\n[InternetShortcut]\nIDList=\nURL="
    elif ext == "ytb":
        ext = ".url"
        buffer = b"[{000214A0-0000-0000-C000-000000000046}]\nProp3=19,11\n[InternetShortcut]\nIDList=\nURL=https://www.youtube.com/watch?v="
    elif ext == "img":
        ext = ".jpg"
    elif ext == "aud":
        ext = ".mp3"
    elif ext == "vid":
        ext = ".mp4"
    elif ext == "download":
        ext = ""
    elif ext == "Test":
        # not yet implemented
        pass
    elif ext == "PhET simulation":
        # not yet implemented
        pass
    else:
        ext = "." + ext

    if sync_only_new.get() and os.path.exists(dir_string + "/" + file.get("name") + ext):
        return

    global error_log
    s_file = None
    print("[Info] Downloading File", file.get("name"), "to", dir_string + "/" + file.get("name") + ext)
    # noinspection PyBroadException
    try:
        resp = s.get(url + "/edu/edufile.php?id=" + file.get("id") + "&download=1")
        s_file = open(dir_string + "/" + file.get("name") + ext, "wb+")
        s_file.write(buffer)
        s_file.write(resp.content)
    except Exception as ex:
        error_log.append("[Error] Beim speichern der folgenden Datei ist ein Fehler aufgetreten: ", ex, file)
    try:
        s_file.close()
    except AttributeError:
        pass


def get_material_list(href):
    if show_debug_messages == 1:
        print("[Debug] Getting Material list")
    resp = s.get(href).text
    resp = resp[resp.find("window.materialListe = ") + 23:]
    resp = resp[:resp.find("</script>") - 1]
    return json.loads(resp)


def syncLU(destroy=False):
    global error_log
    error_log = []

    settings_btn.config(state=DISABLED)
    sync_btn.config(state=DISABLED)
    delete_cb.config(state=DISABLED)
    sync_new_cb.config(state=DISABLED)

    if delete_before_sync.get() and messagebox.askyesno("Ordner löschen?", 'Soll der Ordner "Lernumgebung OfflineSync" wirklich gelöscht werden?'):
        try:
            info_label.config(text="lösche alten Ordner")
            root.update()
            shutil.rmtree(LU_dir)
        except FileNotFoundError:
            pass

    # noinspection PyBroadException
    try:
        # get groups
        if show_debug_messages == 1:
            print("[Debug] Getting user groups")
        resp = s.get(url + "/edu/edumain.php").text
        groupList = list()
        groupmanager = resp[resp.find("class='flist'"):resp.find("class='mlist'")]
        groupmanager = groupmanager.replace("class='flist' ", "")
        while groupmanager.find("gruppe") != -1:
            groupList.append(groupmanager[groupmanager.find("title='") + 7:groupmanager.find("class='felem'") - 7])
            groupmanager = groupmanager.replace("title=", "", 1).replace("class='felem'", "", 1)
            groupList.append(groupmanager[groupmanager.find("gruppe=") + 7:groupmanager.find("&section")])
            groupmanager = groupmanager.replace("gruppe=", "", 1).replace("&section", "", 1)

        # get each group's file directory
        if show_debug_messages == 1:
            print("[Debug] Getting file directory for each group")
        i = 0
        dir_stack = LifoQueue()
        mk_dir(LU_dir)

        while i < len(groupList):
            for sect, dir_sa in [("publ", "Öffentlich"), ("priv", "Privat")]:
                print("[Info] " + groupList[i], groupList[i + 1], dir_sa)
                progress_label.config(text=groupList[i] + " (" + str(int(i / 2)) + "/" + str(int(len(groupList) / 2)) + ")")
                root.update_idletasks()

                # access main directory, create folder
                current_material_list = get_material_list(url + "/edu/edumain.php?gruppe=" + groupList[i + 1] + "&section=" + sect)
                dir_string = LU_dir + "/" + groupList[i]
                mk_dir(dir_string)
                dir_string += "/" + dir_sa
                mk_dir(dir_string)

                n = 0
                while True:
                    try:
                        # update current_file
                        dir_stack.put((current_material_list, n))
                        current_file = current_material_list[n]

                        # parsing key "name" to conform w10 path decoding
                        file_name = current_file.get("name").replace("/", " ").replace("\\", "").replace(
                            ":", " ").replace("*", " ").replace("?", " ").replace('"', " ").replace("<", " ").replace(
                            ">", "").replace("|", "").replace("&amp;", "&").replace("&quot;", ' ').replace(
                            "&apos;", "'").replace("&lt;", "").replace("&gt;", " ")
                        while file_name[len(file_name) - 1] == " ":
                            file_name = file_name[:-1]
                        current_file.update({"name": file_name})
                        print("[Info] " + current_file.get("name"))

                        if current_file.get("typ") == "dir":
                            # directory
                            dir_string += "/" + current_file.get("name")
                            mk_dir(dir_string)
                            current_material_list = get_material_list(url + "/edu/edumain.php?gruppe=" + groupList[i + 1] + "&section=" + sect + "&dir=" + current_file.get("id"))
                            n = 0
                            print("[Info] changed dir to", current_file.get("name"))
                            info_label.config(text=current_file.get("name"))
                            root.update_idletasks()
                        elif current_file.get("typ") == "diropen":
                            pass
                        else:
                            # file
                            dir_stack.get()
                            info_label.config(text=current_file.get("name"))
                            root.update_idletasks()
                            download_file(current_file, dir_string)
                    except IndexError:
                        # end of current materialList
                        dir_stack.get()

                        # return to prev directory
                        if not dir_stack.empty():
                            dir_string = dir_string[:-(dir_string[::-1].find("/") + 1)]
                            current_material_list, n = dir_stack.get()
                        # end of main directory
                        else:
                            break
                    n += 1

            i += 2
    except Exception as ex:
        error_log.append(("[Error] Es ist ein unbekannter Fehler aufgetreten: ", ex, str(ex.__traceback__)))

    print("[Info] Finished with", len(error_log), "errors")
    error_log_file = open(LU_dir + "/ErrorLog.txt", "w+")
    for error in error_log:
        print(error)
        error_log_file.write(str(error) + "\n")
    error_log_file.close()

    progress_label.config(text="Fertig!")
    if len(error_log) < 0:
      e_msg = "Die Synchronisation wurde erfolgreich abgeschlossen!"
    if len(error_log) > 0:
      e_msg = "Die Synchronisation wurde mit " + str(len(error_log)) + " Fehlermeldung(en) abgeschlossen. Siehe ErrorLog.txt für weitere Informationen."
    info_label.config(text=e_msg)
    settings_btn.config(state=NORMAL)
    sync_btn.config(state=NORMAL)
    delete_cb.config(state=NORMAL)
    sync_new_cb.config(state=NORMAL)

    if destroy:
        root.quit()
        sys.exit(0)


# check for available internet connection
v = None
try:
    v = requests.get("https://raw.githubusercontent.com/alexditi/RamaPortalClientsided-Projects/master/Lernumgebung%20Sync/updateLog.json", timeout=5)
except (requests.ConnectionError, requests.Timeout):
    print("[Error] Du bist nicht mit dem Internet verbunden!")
    messagebox.showwarning("Keine Internetverbindung!", "Stelle sicher dass du mit dem Internet verbunden ist und starte die App erneut.")
    try:
        v = requests.get("https://raw.githubusercontent.com/alexditi/RamaPortalClientsided-Projects/master/Lernumgebung%20Sync/updateLog.json", timeout=5)
    except (requests.ConnectionError, requests.Timeout):
        sys.exit(0)

root.deiconify()

# main Frame
main_frame = Frame(root, bg=bg_color)
settings_btn = Button(main_frame, bg=rama_color, activebackground=rama_color_active, fg=font_color, activeforeground=font_color, text="Einstellungen", font="Helvetia 16 bold", command=show_settings, relief=FLAT)
settings_btn.pack(anchor=S, fill=X, pady=10, padx=8)
sync_btn = Button(main_frame, bg=rama_color, activebackground=rama_color_active, fg=font_color, activeforeground=font_color, text="Starte Synchronisation", font="Helvetia 16 bold", command=lambda: Thread(target=syncLU).start(), relief=FLAT)
sync_btn.pack(anchor=S, fill=X, pady=10, padx=8)
cb_frame = Frame(main_frame)
delete_cb = Checkbutton(cb_frame, bg=bg_color, activebackground=bg_color, v=delete_before_sync)
delete_cb.pack(side=LEFT)
Label(cb_frame, text="Ordner vor Update löschen", font="Helvetia 12", fg=font_color, bg=bg_color).pack(side=RIGHT, fill=Y)
cb_frame.pack(pady=5, padx=8, anchor=W, side=TOP)
cb_frame1 = Frame(main_frame)
sync_new_cb = Checkbutton(cb_frame1, bg=bg_color, activebackground=bg_color, v=sync_only_new)
sync_new_cb.pack(side=LEFT, anchor=S)
Label(cb_frame1, text="Nur neue Dateien synchronisieren", font="Helvetia 12", fg=font_color, bg=bg_color).pack(side=RIGHT, fill=Y)
cb_frame1.pack(pady=5, padx=8, anchor=W, side=TOP)
sync_frame = Frame(main_frame, bg=rama_color, width=250, height=150)
sync_frame.pack_propagate(0)
progress_label = Label(sync_frame, bg=bg_color, fg=font_color, font="Helvetia 14 bold", text="")
progress_label.pack(fill=X)
info_label = Message(sync_frame, bg=bg_color, fg=font_color, font="Helvetia 10", text="", aspect=400)
info_label.pack(fill=BOTH, expand=True)
sync_frame.pack(side=TOP, pady=5)

# userdata Frame
userdata_frame = Frame(root, bg=bg_color)
Label(userdata_frame, bg=bg_color, fg=font_color, text="Benutzername", font="Helvetia 16 bold").pack(fill=X, anchor=N, pady=5)
username_entry = Entry(userdata_frame, bg=bg_color, fg=font_color, font="Helvetia 16", relief=FLAT, highlightthickness=2, highlightcolor="black", highlightbackground="black")
username_entry.pack(fill=X, anchor=N, padx=8)
Label(userdata_frame, bg=bg_color, fg=font_color, text="Passwort", font="Helvetia 16 bold").pack(fill=X, anchor=N, pady=5)
password_frame = Frame(userdata_frame, bg=bg_color)
password_entry = Entry(password_frame, bg=bg_color, fg=font_color, font="Helvetia 16", show="*", relief=FLAT, highlightthickness=2, highlightcolor="black", highlightbackground="black")
show_password_btn = Button(password_frame, text="O", font="Helveita 16 bold", bg=bg_color, activebackground=bg_color, fg=rama_color, activeforeground=rama_color_active, relief=FLAT, width=2, command=toggle_show_password)
ToolTip(show_password_btn, "Passwort anzeigen")
show_password_btn.pack(side=RIGHT)
password_entry.pack(fill=X, side=LEFT)
password_frame.pack(fill=X, anchor=N, padx=8)
Label(userdata_frame, bg=bg_color, fg=font_color, text="Synchronisationspfad", font="Helvetia 16 bold").pack(fill=X, anchor=N, pady=5)
dir_frame = Frame(userdata_frame, bg=bg_color)
dir_entry = Entry(dir_frame, bg=bg_color, fg=font_color, font="Helvetia 16", relief=FLAT, highlightthickness=2, highlightcolor="black", highlightbackground="black")
browse_btn = Button(dir_frame, fg=rama_color, activeforeground=rama_color_active, bg=bg_color, activebackground=bg_color, text="||", font="Helvetia 16 bold", relief=FLAT, command=insert_dir)
ToolTip(browse_btn, "Ordner auswählen")
browse_btn.pack(side=RIGHT)
dir_entry.pack(fill=X, side=LEFT)
dir_frame.pack(fill=X, anchor=N, padx=8)
Button(userdata_frame, fg=font_color, activeforeground=font_color, bg=rama_color, activebackground=rama_color_active, text="Speichern", font="Helvetia 16 bold", relief=FLAT, command=submit_userdata).pack(fill=X, anchor=N, padx=30, pady=10)
username_entry.bind("<Return>", submit_userdata)
password_entry.bind("<Return>", submit_userdata)
dir_entry.bind("Return", submit_userdata)
browse_btn.bind("<Return>", submit_userdata)


# try parsing userdata from existing userdata file
# existing userdata file
if show_debug_messages == 1:
    print("[Debug] look for existing userdata file")
try:
    userdata_reader = open(tmpdir + "/userdata_LU.json", "r")
    userdata = json.load(userdata_reader)
    userdata_reader.close()
    del userdata_reader
    LU_dir = userdata.get("dir") + "/Lernumgebung OfflineSync"

    # check for wrong login data
    if not check_login():
        dir_entry.insert(0, userdata.get("dir"))
        userdata_frame.pack(expand=True, fill=BOTH)
    else:
        main_frame.pack(expand=True, fill=BOTH)

# non existing dir or file, incorrect userdata file
except (FileNotFoundError, json.decoder.JSONDecodeError):
    if show_debug_messages == 1:
        print("[Debug] userdata file doesnt exists or is incorrect")
    try:
        # create dir
        if show_debug_messages == 1:
            print("[Debug] creating new userdata file")
        os.mkdir(tmpdir)
    except FileExistsError:
        pass
    # show enter userdata screen
    userdata_frame.pack(expand=True, fill=BOTH)

if len(sys.argv) > 1 and sys.argv[1] == "-startup":
    Thread(target=lambda: syncLU(True)).start()
else:
    updateLog = json.loads(v.text)
    if updateLog.get("version") != version and messagebox.askyesno("Update verfügbar", "Die Version " + updateLog.get("version") + " ist nun verfügbar. Jetzt herunterladen?"):
        # update application
        if show_debug_messages == 1:
            print("[Debug] updating application")
        up_app = open(os.environ["userprofile"] + "/Downloads/LernumgebungSynchronisation.exe", "wb+")
        up_app.write(requests.get("https://github.com/alexditi/RamaPortalClientsided-Projects/raw/" + updateLog.get("version") + "/Lernumgebung Sync/LernumgebungSynchronisation.exe").content)
        up_app.close()
        if show_debug_messages == 1:
            print("[Debug] successfully updated application")
        messagebox.showinfo("Download abgeschlossen!", "Die neue Datei ist im Downloads Ordner zu finden und kann verwendet werden.")
        exit(1)

# root closing action
root.protocol("WM_DELETE_WINDOW", on_closing)
root.bind("<Alt-F4>", on_closing)

root.mainloop()
