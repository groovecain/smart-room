from flask import Flask, render_template, request, jsonify
import threading
import sqlite3
from sqlite3 import Error
from datetime import datetime
import datetime
import time 
import paho.mqtt.publish  as mqttp 
import paho.mqtt.client as mqttc 
app = Flask(__name__)


#define variable dengan default value
#variable juga digunakan untuk menampung setting selama server berjalan
ls = True

#default on start ac setting
ac_state = "off"
ac_state_temp = ""
ac_temp = 16
ac_fan = 1 
ac_swing = 1
#variable untuk menampung timer ac off
ac_timer_off = "0:0"
#variable untuk menampung status timer ac off
ac_timer_off_state = 0
#variable untuk menampung timer off ac yg dipecah 
#digunakan untuk conditional
hours_ac_off = 0
minutes_ac_off = 0

#variable untuk menampung status lampu
#Checked == nyala; Unchecked == tidak menyala
main_lamp = "Checked"
env_lamp = "Checked"

#variable untuk menampung configurasi timer off dari main lamp
lamp1_off_state = 0
lamp1_off = "0:0"
hours_lamp1_off = 0
minutes_lamp1_off = 0

#variable untuk menampung configurasi timer on dari main lamp
lamp1_on_state = 0
lamp1_on = "0:0"
hours_lamp1_on = 0
minutes_lamp1_on = 0

#variable untuk menampung configurasi timer off dari ambient light lamp
lamp2_off_state = 0
lamp2_off = "0:0"
hours_lamp2_off = 0
minutes_lamp2_off = 0

#variable untuk menampung configurasi timer on dari ambient light lamp
lamp2_on_state = 0
lamp2_on = "0:0"
hours_lamp2_on = 0
minutes_lamp2_on = 0

#timer trigger variable
#menentukan apakah timer sudah di trigger
lamp1_on_trigger = 0
lamp1_off_trigger = 0
lamp2_on_trigger = 0
lamp2_off_trigger = 0
ac_off_trigger = 0

DB_NAME = "config"

#function untuk melakukan koneksi ke file database
def create_connection(db_file):
    """ create a database connection to a SQLite database """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except Error as e:
        print(e)

    return conn

#function untuk mengambil configurasi dari table didatabase
def get_config():    
    conn = create_connection("iot_db")
    cur = conn.cursor()
    cur.execute("SELECT * FROM config")

    rows = cur.fetchall()

    return rows
    
#function untuk mengupdate configurasi di table database    
def set_config(conf_name, conf_value):
    conn = create_connection("iot_db")
    cur = conn.cursor()
    cur.execute("update config set conf_value = '" + str(conf_value) + "' where conf_name = '"  + str(conf_name) + "'")
    conn.commit() 

#fungsi untuk menarik configurasi dari database dan menampungnya pada variable
def init_config():
    #inisialisasi variable global pada fungsi ini
    global ac_state, ac_temp, ac_fan, ac_swing, main_lamp, env_lamp, ac_timer_off, ac_timer_off_state, hours_ac_off, minutes_ac_off, lamp1_off_state, lamp1_off, hours_lamp1_off, minutes_lamp1_off, lamp1_on_state, lamp1_on, hours_lamp1_on, minutes_lamp1_on, lamp2_off_state, lamp2_off, hours_lamp2_off, minutes_lamp2_off, lamp2_on_state, lamp2_on, hours_lamp2_on, minutes_lamp2_on
    print(' * Start init config')
    
    #memanggil fungsi get_config dan menampung config object / array pada variable config
    config = get_config()

    #jika variable config ada isi
    if config :    
        #looping untuk setiap row pada variable config
        for conf in config:
            #if untuk memastikan sedang melooping config apa dan 
            #di masukan ke variable yang sudah ditentukan
            if str(conf[1]) == "lamp1_state" :
                main_lamp = str(conf[2])
                #centak configurasi pada console agar dapat melihat value dari terminal
                print(' * main_lamp : ' + str(main_lamp))
            elif str(conf[1]) == "lamp2_state" :
                env_lamp = str(conf[2])
                print(' * env_lamp : ' + str(env_lamp))
            elif str(conf[1]) == "ac_state" :
                ac_state = str(conf[2])
                print(' * ac_state : ' + str(ac_state))
            elif str(conf[1]) == "ac_temp" :
                ac_temp = int(conf[2])
                print(' * ac_temp : ' + str(ac_temp))
            elif str(conf[1]) == "ac_fan" :
                ac_fan = int(conf[2])
                print(' * ac_fan : ' + str(ac_fan))
            elif str(conf[1]) == "ac_swing" :
                ac_swing = int(conf[2])
                print(' * ac_swing : ' + str(ac_swing))
            elif str(conf[1]) == "ac_timer_off" :
                ac_timer_off = str(conf[2])
                #jika status timer off tidak disable
                if ac_timer_off != 0 :
                    #lakukan split value timer menjadi 2 bagian
                    ac_off_temp = ac_timer_off.split(':')
                    hours_ac_off = int(ac_off_temp[0])
                    minutes_ac_off = int(ac_off_temp[1])
                print(' * ac_timer_off : ' + str(ac_timer_off))
            elif str(conf[1]) == "ac_timer_off_state" :
                ac_timer_off_state = int(conf[2])
                print(' * ac_timer_off_state : ' + str(ac_timer_off_state))

            elif str(conf[1]) == "lamp1_off_state" :
                lamp1_off_state = int(conf[2])
                print(' * lamp1_off_state : ' + str(lamp1_off_state))
            elif str(conf[1]) == "lamp1_off" :
                lamp1_off = str(conf[2])
                if lamp1_off != 0 :
                    lamp1_off_temp = lamp1_off.split(':')
                    hours_lamp1_off = int(lamp1_off_temp[0])
                    minutes_lamp1_off = int(lamp1_off_temp[1])
                print(' * lamp1_off : ' + str(lamp1_off))

            elif str(conf[1]) == "lamp1_on_state" :
                lamp1_on_state = int(conf[2])
                print(' * lamp1_on_state : ' + str(lamp1_on_state))
            elif str(conf[1]) == "lamp1_on" :
                lamp1_on = str(conf[2])
                if lamp1_on != 0 :
                    lamp1_on_temp = lamp1_on.split(':')
                    hours_lamp1_on = int(lamp1_on_temp[0])
                    minutes_lamp1_on = int(lamp1_on_temp[1])
                print(' * lamp1_on : ' + str(lamp1_on))

            elif str(conf[1]) == "lamp2_off_state" :
                lamp2_off_state = int(conf[2])
                print(' * lamp2_off_state : ' + str(lamp2_off_state))
            elif str(conf[1]) == "lamp2_off" :
                lamp2_off = str(conf[2])
                if lamp2_off != 0 :
                    lamp2_off_temp = lamp2_off.split(':')
                    hours_lamp2_off = int(lamp2_off_temp[0])
                    minutes_lamp2_off = int(lamp2_off_temp[1])
                print(' * lamp2_off : ' + str(lamp2_off))

            elif str(conf[1]) == "lamp2_on_state" :
                lamp2_on_state = int(conf[2])
                print(' * lamp2_on_state : ' + str(lamp2_on_state))
            elif str(conf[1]) == "lamp2_on" :
                lamp2_on = str(conf[2])
                if lamp2_on != 0 :
                    lamp2_on_temp = lamp2_on.split(':')
                    hours_lamp2_on = int(lamp2_on_temp[0])
                    minutes_lamp2_on = int(lamp2_on_temp[1])
                print(' * lamp2_on : ' + str(lamp2_on))

#memanggil fungsi init_config()                
init_config()

#mendefinisikan fungsi sebelum ada request yang masuk 
@app.before_first_request
#mendefinisikan parent function untuk menampung fungsi multi threading
def light_thread():
    #fungsi multithreading untuk masing-masing timer
    #ac_off
    def run1():
        #definisikan variable global untuk ac_off
        global hours_ac_off, minutes_ac_off, ac_timer_off_state, ac_state, ac_off_trigger
        #looping 
        while ls:
            #ambil jam sekarang
            now = datetime.datetime.now()
            #jika timer off ac aktif dan status ac sedang 'on'
            if ac_timer_off_state == 1 and ac_state == "on" :    
                #jika jam sekarang sama dengan jam timer off ac DAN jika menit sekarang sama dengan menit timer ac off DAN detik sekarang sama dengan 0  
                if now.hour == hours_ac_off and now.minute == minutes_ac_off and now.second == 0 :
                    #ubah variable ac off triger menjadi 1
                    ac_off_trigger = 1
            #looping selama ac_off_trigger masin diatas 0
            while ac_off_trigger > 0:
                #kirim message mqtt ke nodemcu ke channel subscription yang sudah ditentukan
                mqttp.single("/node1/ir/ac","ac_off", hostname="localhost")
                #delay 1 detik untuk aksi mengirim message mqtt
                time.sleep(1)     
                #pesan akan dikirimkan terus ke nodemcu selama trigger belum diset 0 kan
                #raspi akan menerima feedback dari nodemcu apakah on / off sudah berhasil, ketika sudah baru trigger akan diset 0
                #penerimaan feedback ada di bagian bawah
                #pengencekan 2 arah ini harus dilakukan agar raspberry tidak gagal mengexecute action pada timer
                #ada case dimana nodemcu idle dan mqtt terputus dan trigger gagal, makanya harus menunggu feedback dari nodemcu apakah sudah berhasil
            #delay 1 detik untuk pengecekan timer          
            time.sleep(1)       
    #definisikan fungsi multithreading     
    thread = threading.Thread(target=run1)
    #jalankan multithreading
    thread.start()

    #lamp1_off
    def run2():
        global main_lamp, lamp1_off_state, lamp1_off, hours_lamp1_off, minutes_lamp1_off, lamp1_off_trigger
        while ls:        
            now = datetime.datetime.now()
            if lamp1_off_state == 1 and main_lamp == "Checked" :   
                if now.hour == hours_lamp1_off and now.minute == minutes_lamp1_off and now.second == 0 :
                    lamp1_off_trigger = 1
            while lamp1_off_trigger > 0:
                mqttp.single("/node2/relay/lamp","OFF", hostname="localhost")
                time.sleep(1)
            time.sleep(1)
    thread = threading.Thread(target=run2)
    thread.start()
    
    #lamp1_on
    def run3():
        global main_lamp, lamp1_on_state, lamp1_on, hours_lamp1_on, minutes_lamp1_on, lamp1_on_trigger
        while ls:        
            now = datetime.datetime.now()
            if lamp1_on_state == 1 and main_lamp == "Unchecked" :   
                if now.hour == hours_lamp1_on and now.minute == minutes_lamp1_on and now.second == 0 :
                    lamp1_on_trigger = 1
            while lamp1_on_trigger > 0:
                mqttp.single("/node2/relay/lamp","ON", hostname="localhost")
                time.sleep(1)
            time.sleep(1)
    thread = threading.Thread(target=run3)
    thread.start()

    #lamp2_off
    def run4():
        global env_lamp, lamp2_off_state, lamp2_off, hours_lamp2_off, minutes_lamp2_off, lamp2_off_trigger
        while ls:        
            now = datetime.datetime.now()
            if lamp2_off_state == 1 and env_lamp == "Checked" :   
                if now.hour == hours_lamp2_off and now.minute == minutes_lamp2_off and now.second == 0 :
                    lamp2_off_trigger = 1
            while lamp2_off_trigger > 0:
                mqttp.single("/node4/relay/lamp2","OFF", hostname="localhost")
                time.sleep(1)
            time.sleep(1)
    thread = threading.Thread(target=run4)
    thread.start()
    
    #lamp2_on
    def run5():
        global env_lamp, lamp2_on_state, lamp2_on, hours_lamp2_on, minutes_lamp2_on, lamp2_on_trigger
        while ls:        
            now = datetime.datetime.now()
            if lamp2_on_state == 1 and env_lamp == "Unchecked" :   
                if now.hour == hours_lamp2_on and now.minute == minutes_lamp2_on and now.second == 0 :
                    lamp2_on_trigger = 1
            while lamp2_on_trigger > 0:
                mqttp.single("/node4/relay/lamp2","ON", hostname="localhost")
                time.sleep(1)
            time.sleep(1)
    thread = threading.Thread(target=run5)
    thread.start()

#fungsi ketika route '/' atau root di panggil (request)
@app.route("/")
def index():   
    #definisikan variable global  
    global ac_state, ac_temp, ac_fan, ac_swing, main_lamp, env_lamp, ac_timer_off, ac_timer_off_state, hours_ac_off, minutes_ac_off
    #masukan data-data konfigurasi dari variable global ke array Data
    Data = {
      'ac_state' : ac_state,
      'ac_temp' : ac_temp,
      'ac_fan' : ac_fan,
      'ac_swing' : ac_swing,
      'main_lamp' : main_lamp,
      'env_lamp' : env_lamp,
      'type' : 'full'
    }
    #return view dengan fungsi render_template untuk file index_mobile.html dan juga kirimkan variable Data ke view tsb.
    return render_template('index_mobile.html', **Data)

#fungsi ketika route '/lite' di panggil
#pada lite, background particleJS pada view akan dimatikan, cocok untuk device dengan processing power atau ram yang rendah
@app.route("/lite")
def indexMobile():     
    global ac_state, ac_temp, ac_fan, ac_swing, main_lamp, env_lamp, ac_timer_off, ac_timer_off_state, hours_ac_off, minutes_ac_off
    Data = {
      'ac_state' : ac_state,
      'ac_temp' : ac_temp,
      'ac_fan' : ac_fan,
      'ac_swing' : ac_swing,
      'main_lamp' : main_lamp,
      'env_lamp' : env_lamp,
      'type' : 'lite'
    }
    return render_template('index_mobile.html', **Data)

#fungsi ketika route '/' dipanggil dengan request POST
#route ini diutamakan untuk dipanggil oleh web interface menggunakan Ajax
@app.route("/", methods=['POST'])
def index2():
    #definisikan variable global
    global ac_state, ac_temp, ac_fan, ac_swing, main_lamp, env_lamp, ac_timer_off, ac_timer_off_state, hours_ac_off, minutes_ac_off, lamp1_off_state, lamp1_off, hours_lamp1_off, minutes_lamp1_off, lamp1_on_state, lamp1_on, hours_lamp1_on, minutes_lamp1_on, lamp2_off_state, lamp2_off, hours_lamp2_off, minutes_lamp2_off, lamp2_on_state, lamp2_on, hours_lamp2_on, minutes_lamp2_on
    return_data = ""
    
    #ambil data-data yang dikirim menggunakan request POST
    #dnode untuk menentukan device NodeMCU yang akan di panggil
    #dfun untuk fungsi utama
    #dmc untuk device yang akan dikontrol
    #dcm adalah command yang di panggil
    dnode = request.form['node']
    dfun = request.form['fun']
    dmc = request.form['mc']
    dcm = request.form['cm']
    print(dcm)
    return_data = '{"node":"'+dnode+'"}'

    #lakukan kondisional untuk mengecek data yang di masukan
    #juga mengatur value pada variable penampungan dan memasukan status/konfigurasi ke database
    if dnode:   
        if str(dmc) == "ac" :
            if str(dcm) == "ac_on" : 

                if ac_state == "on" :
                    ac_state = "off"
                    dcm = "ac_off"
                    print("ac off")
                elif ac_state == "off" :
                    ac_state = "on"
                    dcm = "ac_on"
                    print("ac on")
                set_config('ac_state', ac_state)

            elif str(dcm) == "fan_minus" :

                if ac_fan > 1 :
                    ac_fan = ac_fan - 1
                else :
                    ac_fan = 4                
                set_config('ac_fan', ac_fan)

            elif str(dcm) == "fan_plus" :

                if ac_fan < 4 :
                    ac_fan = ac_fan + 1    
                else :
                    ac_fan = 1
                set_config('ac_fan', ac_fan)

            elif str(dcm) == "swing_down" :

                if ac_swing > 1 :
                    ac_swing = ac_swing - 1
                else :
                    ac_swing = 6
                set_config('ac_swing', ac_swing)

            elif str(dcm) == "swing_up" :

                if ac_swing < 6 :
                    ac_swing = ac_swing + 1 
                else :
                    ac_swing = 1
                set_config('ac_swing', ac_swing)

            elif str(dcm) == "temp_down" :

                if ac_temp > 16 :
                    ac_temp = ac_temp - 1
                    set_config('ac_temp', ac_temp)

            elif str(dcm) == "temp_up" :

                if ac_temp < 30 :
                    ac_temp = ac_temp + 1
                    set_config('ac_temp', ac_temp)

            if dcm == "fan_plus" or dcm == "fan_minus" :
                if ac_fan == 1 :
                    dcm = "fan_min"
                elif ac_fan == 2 : 
                    dcm = "fan_med"
                elif ac_fan == 3 :                 
                    dcm = "fan_max"
                elif ac_fan == 4 : 
                    dcm = "fan_auto"    
   
            if dcm == "swing_up" or dcm == "swing_down" :
                if ac_swing == 1 : 
                    dcm = "swing_1"
                elif ac_swing == 2 : 
                    dcm = "swing_2"
                elif ac_swing == 3 : 
                    dcm = "swing_3"
                elif ac_swing == 4 : 
                    dcm = "swing_4"  
                elif ac_swing == 5 : 
                    dcm = "swing_5"  
                elif ac_swing == 6 : 
                    dcm = "swing_auto"  

            if dcm == "temp_down" or dcm == "temp_up" :
                dcm = ac_temp

            ac = '{ "ac_state":"'+ac_state+'", "ac_temp":'+str(ac_temp)+', "ac_fan":'+str(ac_fan)+', "ac_swing":'+str(ac_swing)+'}'
            print(ac)
            print(dcm)
            return_data = ac

            mqttp.single("/" + str(dnode) + "/" + str(dfun) + "/" + str(dmc),str(dcm), hostname="localhost")

        elif str(dfun) == "ac_timer_off" :

            ac_timer_off_state = int(dmc)
            set_config('ac_timer_off_state', str(ac_timer_off_state))

            ac_timer_off = str(dcm)
            set_config('ac_timer_off', str(ac_timer_off))

            ac_off_temp = ac_timer_off.split(':')
            hours_ac_off = int(ac_off_temp[0])
            minutes_ac_off = int(ac_off_temp[1])

        elif str(dfun) == "lamp1_timer_off" :

            lamp1_off_state = int(dmc)
            set_config('lamp1_off_state', str(lamp1_off_state))

            lamp1_off = str(dcm)
            set_config('lamp1_off', str(lamp1_off))

            lamp1_off_temp = lamp1_off.split(':')
            hours_lamp1_off = int(lamp1_off_temp[0])
            minutes_lamp1_off = int(lamp1_off_temp[1])

        elif str(dfun) == "lamp1_timer_on" :
            print('lamp on timer')
            lamp1_on_state = int(dmc)
            set_config('lamp1_on_state', str(lamp1_on_state))

            lamp1_on = str(dcm)
            set_config('lamp1_on', str(lamp1_on))

            lamp1_on_temp = lamp1_on.split(':')
            hours_lamp1_on = int(lamp1_on_temp[0])
            minutes_lamp1_on = int(lamp1_on_temp[1])

        elif str(dfun) == "lamp2_timer_off" :

            lamp2_off_state = int(dmc)
            set_config('lamp2_off_state', str(lamp2_off_state))

            lamp2_off = str(dcm)
            set_config('lamp2_off', str(lamp2_off))

            lamp2_off_temp = lamp2_off.split(':')
            hours_lamp2_off = int(lamp2_off_temp[0])
            minutes_lamp2_off = int(lamp2_off_temp[1])

        elif str(dfun) == "lamp2_timer_on" :
            print('lamp on timer')
            lamp2_on_state = int(dmc)
            set_config('lamp2_on_state', str(lamp2_on_state))

            lamp2_on = str(dcm)
            set_config('lamp2_on', str(lamp2_on))

            lamp2_on_temp = lamp2_on.split(':')
            hours_lamp2_on = int(lamp2_on_temp[0])
            minutes_lamp2_on = int(lamp2_on_temp[1])

        else:        
            if dmc == "lamp" :            
                if dcm == 'ON' : 
                    #main_lamp = 'Checked' 
                    print("main lamp on")
                    #set_config('lamp1_state', main_lamp)
                elif  dcm == 'OFF' :
                    #main_lamp = 'Unchecked' 
                    print("main lamp off")
                    #set_config('lamp1_state', main_lamp)
            elif dmc == "lamp2" :            
                if dcm == 'ON' : 
                    #env_lamp = 'Checked' 
                    print("env lamp on")
                    #set_config('lamp1_state', env_lamp)
                elif  dcm == 'OFF' :
                    #env_lamp = 'Unchecked' 
                    print("env lamp off")
                    #set_config('lamp1_state', env_lamp)

            mqttp.single("/" + str(dnode) + "/" + str(dfun) + "/" + str(dmc),str(dcm), hostname="localhost")
    
    return return_data

#fungsi ketika route '/get-state' dipanggil dengan request POST
#route ini diutamakan untuk dipanggil oleh web interface menggunakan Ajax
#fungsi ini untuk mengambil semua status / configurasi dari variable dan di lempar ke front-end
@app.route("/get-state", methods=['POST'])
def getState():
    init_config()
    global ac_state, ac_temp, ac_fan, ac_swing, main_lamp, env_lamp, ac_timer_off, ac_timer_off_state, hours_ac_off, minutes_ac_off, lamp1_off_state, lamp1_off, hours_lamp1_off, minutes_lamp1_off, lamp1_on_state, lamp1_on, hours_lamp1_on, minutes_lamp1_on, lamp2_off_state, lamp2_off, hours_lamp2_off, minutes_lamp2_off, lamp2_on_state, lamp2_on, hours_lamp2_on, minutes_lamp2_on
    

    ac = '{ "ac_state":"'+ac_state+'", "ac_temp":'+str(ac_temp)+', "ac_fan":'+str(ac_fan)+', "ac_swing":'+str(ac_swing)+', "ac_timer_off_state":'+str(ac_timer_off_state)+', "ac_timer_off":"'+str(ac_timer_off)+'", "main_lamp":"'+str(main_lamp)+'", "lamp1_off_state":'+str(lamp1_off_state)+', "lamp1_off":"'+str(lamp1_off)+'", "lamp1_on_state":'+str(lamp1_on_state)+', "lamp1_on":"'+str(lamp1_on)+'", "env_lamp":"'+str(env_lamp)+'", "lamp2_off_state":'+str(lamp2_off_state)+', "lamp2_off":"'+str(lamp2_off)+'", "lamp2_on_state":'+str(lamp2_on_state)+', "lamp2_on":"'+str(lamp2_on)+'"}'
    print(ac)
    return_data = ac
    
    return return_data

#fungsi ketika route '/force-state' dipanggil dengan request POST
#route ini diutamakan untuk dipanggil oleh web interface menggunakan Ajax
#fungsi ini memaksa status ac on-off pada variable
#fungsi ini tidak digunakan lagi
@app.route("/force-state", methods=['POST'])
def forceState():
    global ac_state, ac_temp, ac_fan, ac_swing 

    fun = request.form['fun']
    if fun == 'AC' : 
        if ac_state == 'on' : 
            ac_state = 'off' 
            cmd = 'state_off'
        elif  ac_state == 'off' :
            ac_state = 'on'
            cmd = 'state_on'
        
        mqttp.single("/node1/ir/ac",cmd, hostname="localhost")
        ac = '{ "ac_state":"'+ac_state+'", "ac_temp":'+str(ac_temp)+', "ac_fan":'+str(ac_fan)+', "ac_swing":'+str(ac_swing)+'}'
        print(ac)
        return_data = ac
    
    return return_data

#fungsi ketika route '/json' dipanggil dengan request POST
#route ini diutamakan untuk dipanggil oleh web socket dengan data json
@app.route("/json", methods=['POST'])
def index3():      
    global ac_state, ac_temp, ac_fan, ac_swing, main_lamp, env_lamp
    req_data = request.json

    if req_data:
        dnode = req_data['node']
        dfun = req_data['fun']
        dmc = req_data['mc']
        dcm = req_data['cm']

        if str(dcm.lower()) == "spk_aux one": dcm = "spk_aux1"
        if str(dcm.lower()) == "spk_aux two": dcm = "spk_aux2"       
            
        if str(dcm.lower()) == "ac_on": 
            if ac_state == 'on' : 
                dcm = 'ac_off'
                ac_state = 'off' 
            elif  ac_state == 'off' :
                dcm = 'ac_on'
                ac_state = 'on'
        
        if dmc == "lamp" :            
            if dcm == 'ON' : 
                #main_lamp = 'Checked' 
                print("main lamp on")
            elif  dcm == 'OFF' :
                #main_lamp = 'Unchecked' 
                print("main lamp off")    
        elif dmc == "lamp2" :            
            if dcm == 'ON' : 
                #env_lamp = 'Checked' 
                print("env lamp on")
            elif  dcm == 'OFF' :
                #env_lamp = 'Unchecked' 
                print("env lamp off")      

        mqttp.single("/" + str(dnode) + "/" + str(dfun) + "/" + str(dmc),str(dcm), hostname="localhost")
        print(str(dcm))

    return dnode

now = datetime.datetime.now()

#fungsi untuk membuka channel subscript '/raspi/feedback' untuk menerima mqtt dari nodemcu
def on_connect(client, userdata, flags, rc): 
    print("Connected with result code " + str(rc)) 
    # Subscribing in on_connect() means that if we lose the connection and 
    # reconnect then subscriptions will be renewed. 
    client.subscribe("/raspi/feedback")

#fungsi ketika channel '/raspi/feedback' mendapatkan mqtt 
def on_message(client, userdata, msg): 
    #definisikan variable global
    global main_lamp, lamp1_on_state, lamp1_on, hours_lamp1_on, minutes_lamp1_on, lamp1_on_trigger, lamp1_off_trigger, env_lamp, lamp2_on_state, lamp2_on, hours_lamp2_on, minutes_lamp2_on, lamp2_on_trigger, lamp2_off_trigger, ac_off_trigger
    print(msg.topic+" => "+str(msg.payload)) 
    #cek apakah message benar jalurna
    if msg.topic == '/raspi/feedback': 
        #cek isi pesan mqtt untuk menentukan action
        #fungsinya untuk menerima feedback dari mqtt apakah lampu sudah dimatikan atau dinyalakan

        #jika message berupa 'LAMP_ON' berarti nodemcu sukses menyalakan main lamp
        if msg.payload == b'LAMP_ON': 
            #ubah variable ke Checked == nyala
            main_lamp = "Checked"
            #simpan status ke database
            set_config('lamp1_state', main_lamp)
            #matikan tirgger timer
            lamp1_on_trigger = 0
            #karena trigger timer sudah dimatikan,maka looping timer akan stop, raspi tidak akan mencoba untuk mengirim mqtt untuk aksi timer
        elif msg.payload == b'LAMP_OFF': 
            main_lamp = "Unchecked"
            set_config('lamp1_state', main_lamp)
            lamp1_off_trigger = 0
        elif msg.payload == b'LAMP2_ON': 
            env_lamp = "Checked"
            set_config('lamp2_state', env_lamp)
            lamp2_on_trigger = 0
        elif msg.payload == b'LAMP2_OFF': 
            env_lamp = "Unchecked"
            set_config('lamp2_state', env_lamp)
            lamp2_off_trigger = 0
        elif msg.payload == b'AC_OFF': 
            ac_state = "off"
            set_config('ac_state', ac_state)
            ac_off_trigger = 0

#aktifkan fungsi MQTT CLient untuk menerima feedback
mqttc_client = mqttc.Client()
mqttc_client.on_connect = on_connect 
mqttc_client.on_message = on_message 
mqttc_client.connect('localhost', 1883, 60) 
mqttc_client.loop_start() 


#fungsi untuk mendefine FLASK SERVER 
if __name__ == "__main__":
    create_connection(r"iot_db")
    app.run(host='0.0.0.0', port=80, debug=True, threaded=True)




