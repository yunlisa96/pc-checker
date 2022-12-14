#!/usr/bin/python3
import gi
import getpass
import subprocess
import os
import set
import count
import gettext
import locale

gi.require_version("Gtk", "3.0")
gi.require_version('AppIndicator3', '0.1')
from gi.repository import Gtk, Gio
from datetime import date, datetime


# i18n
APP = 'hamonikr-pcchecker'
LOCALE_DIR = "/usr/share/locale"
locale.bindtextdomain(APP, LOCALE_DIR)
gettext.bindtextdomain(APP, LOCALE_DIR)
gettext.textdomain(APP)
_ = gettext.gettext

class DialogExample(Gtk.Dialog):
    def __init__(self, parent):
        super().__init__(title=_("Alarm settings"), flags=0)
        self.add_buttons(
            Gtk.STOCK_CLOSE, Gtk.ResponseType.CLOSE
        )
        
        self.set_default_size(250, 200)
        (self.lbl_alarm_info, switch_alarm, alarm_info) = set.set_alarm()       # search alarm info
        self.lbl_alarm = Gtk.Label()
        self.lbl_alarm.set_markup("<span font='13'>"+_("When the alarm is turned on, an alarm is\n displayed in a pop-up window for the item\n whose security status is 'dangerous'.")+"</span>")
        self.lbl_alarm.set_margin_top(15)
        self.lbl_alarm.set_margin_left(15)
        self.lbl_alarm.set_margin_right(15)
        box = self.get_content_area()
        # box.add(label)
        
        switch_alarm.connect("notify::active", self.on_switch_activated)
        self.lbl_alarm_info.set_margin_right(50)
        switch_alarm.set_margin_right(15)
        box_alarm_info = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        box_alarm = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=2)
        box_alarm_info.pack_start(self.lbl_alarm, False, False, 0)
        box_alarm.pack_start(self.lbl_alarm_info, True, False, 0)
        box_alarm.pack_start(switch_alarm, False, False, 0)
        box_alarm_info.add(box_alarm)
        box.add(box_alarm_info)
        
        self.show_all()
        
    def on_switch_activated(self, switch_alarm, gparam):
        if switch_alarm.get_active():
            subprocess.call("systemctl daemon-reload", shell=True)
            subprocess.call("systemctl restart pcchecker_alarm.timer", shell=True)
            (lbl_alarm_info, switch_alarm, alarm_info) = set.set_alarm()        # search alarm info
            # set alarm gui
            self.lbl_alarm_info.set_markup(alarm_info)
        else:
            subprocess.call("systemctl stop pcchecker_alarm.timer", shell=True)
            (lbl_alarm_info, switch_alarm, alarm_info) = set.set_alarm()        # search alarm info
            # set alarm gui
            self.lbl_alarm_info.set_markup(alarm_info)
        print("Switch was turned", switch_alarm.get_active())


class Application:
        
    def __init__(self):
        self.builder = Gtk.Builder()
        self.builder.set_translation_domain(APP)
        self.builder.add_from_file("/usr/share/hamonikr/pcchecker/pcchecker.glade")
        self.builder.connect_signals(self)

        self.window = self.builder.get_object("window")
        self.window.set_title("hamonikr-pcchecker")
        
        self.window.show_all()
        
        os_name = self.fnt_command_return_word("lsb_release -i", 'ID:\t', '\n')
        os_ver = self.fnt_command_return_word("lsb_release -r", 'Release:\t', '\n')
        os_info = os_name + " " + os_ver
        kernel_ver = self.fnt_command_return_word("uname -r", False, '\n')
        cpu_name = self.fnt_command_return_word("lscpu | grep 'Model name:'", 'Model name:', '\n')
        cpu_cnt = subprocess.check_output("nproc", shell=True).decode().strip()
        memory_name = subprocess.check_output("free -h | grep 'Mem:'", shell=True).decode()
        memory_name = memory_name.split('Mem:')[1].strip().split(' ')[0]
        disk_val = self.fnt_command_return_word(
            "df -P | grep -v ^Filesystem | awk '{sum += $2} END { print sum/1024/1024 }'", False, '\n')
        disk_val = str(round(float(disk_val), 1))
        graphic_val = self.fnt_command_return_word("lspci | grep -i VGA", 'controller: ', '\n')
        uuid_val = self.fnt_command_return_word("sudo blkid | grep UUID", 'UUID="', '"')
        
        self.builder.get_object("label7").set_markup("<span font='13'><b>"+_("Product no")+"</b></span> : <span>"+uuid_val+"</span>")
        self.builder.get_object("label2").set_markup("<span font='13'><b>"+_("Operating system")+"</b></span> : <span>"+os_info+"</span>")
        self.builder.get_object("label3").set_markup("<span font='13'><b>"+_("Memory")+"</b></span> : <span>"+memory_name+"</span>")
        self.builder.get_object("label4").set_markup("<span font='13'><b>"+_("Hard drive")+"</b></span> : <span>"+disk_val+"GB</span>")

        (pw_status, pw_past) = set.set_password()
        osname = self.fnt_command_return_word("lsb_release -i", 'ID:\t', '\n')
        (update_status, update_info) = set.set_update(osname)
        (self.lbl_ufw_status, self.lbl_ufw_info, self.switch_ufw, ufw_status, ufw_info) = set.set_ufw()
        (self.lbl_ts_status, self.lbl_ts_info, ts_status, ts_info) = set.set_backup()
        total_score_val = count.set_score()
        self.builder.get_object("exlabel1").set_markup("<b>"+_("Password")+"</b>")
        self.builder.get_object("exlabel12").set_markup(pw_status)
        self.builder.get_object("exlabel2").set_markup("<b>"+_("Upgrade")+"</b>")
        self.builder.get_object("exlabel23").set_markup(update_status)
        self.builder.get_object("exlabel3").set_markup("<b>"+_("Firewall")+"</b>")
        self.builder.get_object("exlabel32").set_markup(ufw_status)
        self.builder.get_object("exlabel4").set_markup("<b>"+_("Back up")+"</b>")
        self.builder.get_object("exlabel42").set_markup(ts_status)
        self.builder.get_object("exlabel11").set_markup(pw_past)
        self.builder.get_object("exlabel22").set_markup(update_info)
        self.builder.get_object("exlabel33").set_markup(ufw_info)
        self.builder.get_object("exlabel44").set_markup(ts_info)
        if 100 == total_score_val:
            total_score_text = "<span color='green' font='40'><b>" + str(total_score_val) + "</b></span><span><b>/100</b></span>"
            total_status_text = "<span color='green' font='80'><b>"+_("Safety")+"</b></span>"
            total_info_text = "<span>"+_("Your system is safe.")+"</span>"
        elif 70 < total_score_val:
            total_score_text = "<span color='orange' font='40'><b>" + str(total_score_val) + "</b></span><span><b>/100</b></span>"
            total_status_text = "<span color='orange' font='80'><b>"+_("Caution")+"</b></span>"
            total_info_text = "<span>"+_("System administration needs attention.")+"</span>"
        else:
            total_score_text = "<span color='red' font='40'><b>" + str(total_score_val) + "</b></span><span><b>/100</b></span>"
            total_status_text = "<span color='red' font='80'><b>"+_("Danger")+"</b></span>"
            total_info_text = "<span>"+_("Please manage the system.")+"</span>"
        self.builder.get_object("label31").set_markup(total_status_text)
        self.builder.get_object("label41").set_markup(total_info_text)
        self.builder.get_object("label42").set_markup(total_score_text)
        
        
        self.builder.get_object("button1").connect("clicked", self.fnt_set_score)
        self.builder.get_object("button3").connect("clicked",self.open_cinnamon_info)
        self.builder.get_object("button4").connect("clicked",self.fnt_open_user)
        self.builder.get_object("button4").connect("released",self.fnt_close_user)
        self.builder.get_object("button5").connect("clicked",self.fnt_open_updatemanager)
        self.builder.get_object("button5").connect("released",self.fnt_close_updatemanager)
        self.builder.get_object("button6").connect("clicked",self.fnt_open_ufw)
        self.builder.get_object("button6").connect("released",self.fnt_close_ufw)
        self.builder.get_object("button7").connect("clicked",self.fnt_open_timeshift)
        self.builder.get_object("button7").connect("released",self.fnt_close_timeshift)
        self.builder.get_object("button8").connect("clicked",self.open_chrome)
        self.builder.get_object("button2").connect("clicked",self.on_button_clicked)
        
    # change subprocess.call result to split words
    def fnt_command_return_word(self, command, split1, split2):
        if False == split1:
            result = subprocess.check_output(command, shell=True).decode().split(split2)[0]
        elif False == split2:
            result = subprocess.check_output(command, shell=True).decode().split(split1)[1]
        else:
            result = subprocess.check_output(command, shell=True).decode().split(split1)[1].split(split2)[0]
        return result.strip()
    
    def fnt_set_score(self, widget):
        total_score_val = count.set_score()      # count score
        # set the total score and status
        if 100 == total_score_val:
            total_score_text = "<span color='green' font='40'><b>" + str(total_score_val) + "</b></span><span><b>/100</b></span>"
            total_status_text = "<span color='green' font='80'><b>"+_("Safety")+"</b></span>"
            total_info_text = "<span>"+_("Your system is safe.")+"</span>"
        elif 70 < total_score_val:
            total_score_text = "<span color='orange' font='40'><b>" + str(total_score_val) + "</b></span><span><b>/100</b></span>"
            total_status_text = "<span color='orange' font='80'><b>"+_("Caution")+"</b></span>"
            total_info_text = "<span>"+_("System administration needs attention.")+"</span>"
        else:
            total_score_text = "<span color='red' font='40'><b>" + str(total_score_val) + "</b></span><span><b>/100</b></span>"
            total_status_text = "<span color='red' font='80'><b>"+_("Danger")+"</b></span>"
            total_info_text = "<span>"+_("Please manage the system.")+"</span>"
        self.builder.get_object("label31").set_markup(total_status_text)
        self.builder.get_object("label41").set_markup(total_info_text)
        self.builder.get_object("label42").set_markup(total_score_text)
        
    def open_cinnamon_info(self,widget):
        subprocess.call('cinnamon-settings info', shell=True)
        
    def open_chrome(self,widget):
        subprocess.call('/usr/bin/naver-whale-stable %U --password-store=basic --user-data-dir --test-type --no-sandbox https://docs.hamonikr.org/hamonikr-6.0', shell=True)

        
    # open cinnamon-settings/user-accounts window when password setting button clicked
    def fnt_open_user(self, widget):
        # self.logger("Open user - pw")
        osname = self.fnt_command_return_word("lsb_release -i", 'ID:\t', '\n')
        # for Hamonikr users
        if osname == "Hamonikr":
            subprocess.call('su $PCCHECKER_USER -c "cinnamon-settings user"', shell=True)
        # for GooroomOS and TmaxOS users
        else :
            subprocess.call('XDG_CURRENT_DESKTOP=GNOME gnome-control-center user-accounts', shell=True)
            
    def fnt_close_user(self,widget):
        # self.logger("Close user - pw")
        (pw_status, pw_past) = set.set_password()       # search password info
        self.builder.get_object("exlabel1").set_markup("<b>"+_("Password")+"</b>")
        self.builder.get_object("exlabel12").set_markup(pw_status)
        self.builder.get_object("exlabel11").set_markup(_(pw_past))
    
    # open minupdate/gooroom-update-launcher/gnome-control-center window when update setting button clicked
    def fnt_open_updatemanager(self, widget):
        # self.logger("Open update manager")
        osname = self.fnt_command_return_word("lsb_release -i", 'ID:\t', '\n')
        if osname == "Hamonikr":
            subprocess.call('mintupdate', shell=True)
        elif osname == "Gooroom":
            subprocess.call('gooroom-update-launcher', shell=True)
        elif osname == "Tmaxos":
            subprocess.call('XDG_CURRENT_DESKTOP=GNOME gnome-control-center info-overview', shell=True)
        
    def fnt_close_updatemanager(self, widget):
        # self.logger("Close user - pw")
        osname = self.fnt_command_return_word("lsb_release -i", 'ID:\t', '\n')
        (update_status, update_info) = set.set_update(osname)       # search password info
        self.builder.get_object("exlabel2").set_markup("<b>"+_("Upgrade")+"</b>")
        self.builder.get_object("exlabel23").set_markup(update_status)
        self.builder.get_object("exlabel22").set_markup(_(update_info))
        
    # open gufw window when ufw setting button is clicked
    def fnt_open_ufw(self, widget):
        # self.logger("Open ufw")
        subprocess.call('sudo gufw', shell=True)
        
    # reload ufw info when ufw setting window is closed
    def fnt_close_ufw(self, widget):
        # self.logger("Close ufw")
        (lbl_ufw_status,lbl_ufw_info, switch_ufw, ufw_status, ufw_info) = set.set_ufw()     # search ufw info
        # set ufw gui
        self.builder.get_object("exlabel3").set_markup("<b>"+_("Firewall")+"</b>")
        self.builder.get_object("exlabel32").set_markup(ufw_status)
        self.builder.get_object("exlabel33").set_markup(_(ufw_info))
        self.fnt_set_score
        
    # open timeshift-gtk window when backup setting button is clicked
    def fnt_open_timeshift(self, widget):
        # self.logger("Open timeshft")
        subprocess.call('sudo timeshift-gtk', shell=True)
        
    # reload backup info when backup setting window is closedq
    def fnt_close_timeshift(self,widget):
        # self.logger("Close timeshft")
        (lbl_ts_status, lbl_ts_info, ts_status, ts_info) = set.set_backup()     # search backup info
        # set backup gui
        self.builder.get_object("exlabel4").set_markup("<b>"+_("Back up")+"</b>")
        self.builder.get_object("exlabel42").set_markup(ts_status)
        self.builder.get_object("exlabel44").set_markup(_(ts_info))
        
    def on_button_clicked(self, widget):
        dialog = DialogExample(self)
        response = dialog.run()

        if response == Gtk.ResponseType.CLOSE:
            print("The OK button was clicked")
        elif response == Gtk.ResponseType.CANCEL:
            print("The Cancel button was clicked")

        dialog.destroy()
    
    # run the application
    def run(self):
        
        Gtk.main()
# ensure that user has manager access
if 'root' != getpass.getuser():
    subprocess.call(
        'zenity --error --no-wrap --height=150 --width=250 --title "Execute permission error" --text="Please run it with administrator privileges."',
        shell=True)
else:
    Application().run()