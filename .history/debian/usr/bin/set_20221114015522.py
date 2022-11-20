# search information of password, update, ufw, backup, and alarm
import subprocess
from gi.repository import Gtk
from datetime import date
import os

## search and set password info ##
def set_password():
    # search for date the password was last changed
    pw_date = subprocess.check_output("sudo passwd -S $PCCHECKER_USER | awk '{print $3}'", shell=True).decode().split(
        '/')
    # if the password is changed today, pw_date = 0
    if date.today() == date(int(pw_date[2]), int(pw_date[0]), int(pw_date[1])):
        pw_date = 0
    # else, calculate the difference in date
    else:
        pw_date = int(str(date.today() - date(int(pw_date[2]), int(pw_date[0]), int(pw_date[1]))).split(' day')[0])

    # state according to the difference in date
    if 30 >= pw_date:
        pw_status = "<span background='green' font='15' color='white'><b>" +_("Safety")+ "</b></span>"
        pw_past = _("It has been")+" <span color='green'><b> " + str(pw_date) + "</b></span>"+_("days since you changed your password.")
    elif 90 >= pw_date:
        pw_status = "<span background='orange' font='15' color='white'><b>"+_("Caution")+" </b></span>"
        pw_past = _("It has been")+"<span color='orange'><b> " + str(pw_date) + "</b></span>"+_("days since you changed your password.")
    else:
        pw_status = "<span background='red' font='15' color='white'><b> "+_("Danger")+" </b></span>"
        pw_past = _("It has been")+"<span color='red'><b> " + str(pw_date) + "</b></span>"+_("days since you changed your password.")
    return (pw_status, pw_past)

## search and set update info ##
def set_update(osname):
    # for Hamonikr users
    if osname == "Hamonikr":
        # search for the number of upgradeable packages
        update_list = subprocess.check_output("mintupdate-cli list | wc -l", shell=True).decode().strip()
        update_list = int(str(update_list))
    # for GooroomOS and TmaxOS users
    else:
        # search for the number of upgradeable packages
        update_list = subprocess.check_output("apt list --upgradable | wc -l", shell=True).decode().strip()
        update_list = int(str(update_list)) - 1  # doesn't count a info line

    # state according to the number of upgradable packages
    if 5 >= update_list:
        update_status = "<span background='green' font='15' color='white'><b> " +_("New")+ " </b></span>"
        update_info = _("There are")+"<span color='green'><b>" + str(update_list) + "</b></span>"+_("upgradeable packages.")
    else:
        update_status = "<span background='orange' font='15' color='white'><b> "+_("Caution")+" </b></span>"
        update_info = _("There are")+"<span color='orange'><b>" + str(update_list) + "</b></span>"+_("upgradeable packages.")
    return (update_status,update_info)

## search and set ufw info ##
def set_ufw():
    lbl_ufw_info = Gtk.Label()
    lbl_ufw_status = Gtk.Label()
    switch_ufw = Gtk.Switch()

    # search for the active/inactive status of ufw
    ufw_val = subprocess.check_output("sudo ufw status | awk '{print $2}' | head -1", shell=True).decode().strip()
    # set the info if ufw is inactive
    if ufw_val == "비활성" or ufw_val == "inactive":
        ufw_status = "<span background='red' font='15' color='white'><b> "+_("Inactive")+" </b></span>"
        ufw_info=_("Firewall is disabled.")
        lbl_ufw_info.set_markup(ufw_info)
        switch_ufw.set_active(0)
    # set the info if ufw is active
    elif ufw_val == "활성" or ufw_val == "active":
        ufw_status = "<span background='green' font='15' color='white'><b> "+_("Active")+" </b></span>"
        ufw_info=_("Firewall is enabled.")
        lbl_ufw_info.set_markup(ufw_info)
        switch_ufw.set_active(1)
    # set the info if ufw is indeterminate
    else:
        ufw_status = "<span background='orange' font='15' color='white'><b> "+_("Error")+" </b></span>"
        ufw_info=_("Unable to check firewall status.")
        lbl_ufw_info.set_markup(ufw_info)
        switch_ufw.set_active(0)
    lbl_ufw_status.set_markup(ufw_status)
    return (lbl_ufw_status,lbl_ufw_info, switch_ufw, ufw_status, ufw_info)

## search and set backup info ##
def set_backup():
    lbl_ts_status = Gtk.Label()
    lbl_ts_info = Gtk.Label()

    # search for the number of backup snapshots
    backup_list_len = int(str(subprocess.check_output("sudo timeshift --list | grep '>' | wc -l", shell=True).decode()))
    # state according to the recent backup date
    if backup_list_len >= 1 :
        bk_date = str(subprocess.check_output("sudo timeshift --list | grep '>' | awk '{print $3}'|tail -1", shell=True).decode()).split('_')[0].split('-')
        bk_date = date(int(bk_date[0]), int(bk_date[1]), int(bk_date[2]))
        diff_day = str(date.today() - bk_date)
        if "0:00:00" == diff_day:
            diff_day = 0
        else:
            diff_day = int(str(date.today() - bk_date).split(' day')[0])

        if 30 > diff_day:
            ts_status = "<span background='green' font='15' color='white'><b>"+_("Safety")+ "</b></span>"
        elif 60 > diff_day:
            ts_status = "<span background='orange' font='15' color='white'><b> "+_("Caution")+" </b></span>"
        else:
            ts_status = "<span background='red' font='15' color='white'><b> "+_("Danger")+" </b></span>"
        # set the date of recent backup
        ts_info = (str(backup_list_len) + " 개의 백업이 있습니다.\n마지막 백업은 <b>" + str(bk_date.year) + "년" + str(bk_date.month) + "월" +
                   str(bk_date.day) + "일</b> 입니다.")
        ts_info = _("There are"+str(backup_list_len)+"backups. The last backup was on"+str(bk_date.month)+" "+str(bk_date.day)+", "+str(bk_date.year)+".")
    # set the info if snapshot doesn't exists
    else:
        ts_status = "<span background='red' font='15' color='white'><b>"+_("Danger")+"</b></span>"
        ts_info = _("For system safety, proceed with a backup.")

    lbl_ts_info.set_markup(ts_info)
    lbl_ts_status.set_markup(ts_status)
    return (lbl_ts_status, lbl_ts_info, ts_status, ts_info)

## search and set alarm info ##
def set_alarm():
    lbl_alarm_info = Gtk.Label()
    switch_alarm = Gtk.Switch()
    switch_alarm.set_tooltip_text(_("It checks the security status of the PC and periodically displays a notification if it is in a 'dangerous' state."))
    # set info if timer (for alarm) is inactive
    try:
        subprocess.check_output("systemctl status pcchecker_alarm.timer | grep inactive", shell=True, stderr=subprocess.STDOUT).decode().strip()
        alarm_info=_("Alarm is off.")
        lbl_alarm_info.set_markup(alarm_info)
        switch_alarm.set_active(0)
    # set info if timer (for alarm) is active
    except subprocess.CalledProcessError as e:
        alarm_info = _("Alarm is on.")
        lbl_alarm_info.set_markup(alarm_info)
        switch_alarm.set_active(1)
    return (lbl_alarm_info, switch_alarm, alarm_info)