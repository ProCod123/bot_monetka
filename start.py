import time



while True:
    try:

        x = 8/0
        

    except Exception as e:
        print(e)

        if time.gmtime().tm_min in (0,10,20,30,40,50) and time.gmtime().tm_sec < 31:
            print(time.gmtime().tm_min, time.gmtime().tm_sec)

        time.sleep(15)
