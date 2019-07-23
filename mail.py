import conf, json, time, math, statistics
from boltiot import Email, Bolt

def compute_bounds(history_data, frame_size, factor):
    if len(history_data)<frame_size:
    return None

    if len(history_data)>frame_size:
    del history_data[0:len(history_data)-frame_size]
        Mn = statistics.mean(history_data)
        Varriance = 0
        for data in history_data:
    Varriance += math.pow((data-Mn), 2)
        Zn = factor * math.sqrt(Varriance/frame_size)
        High_bound = history_data[frame_size-1]+ Zn
        Low_bound = history_data[frame_size-1] - Zn
        return [High_bound, Low_bound]
mybolt = Bolt(conf.API_KEY, conf.DEVICE_ID)
mailer = Email(conf.MAILGUN_API_KEY, conf.SANDBOX_URL, conf.SENDER_EMAIL, conf.RECIPIENT_EMAIL)
history_data = []

while True:
    response = mybolt.analogRead('A0')
    data = json.loads(response)
    if data['success'] != 1:
      print("There was ana error while retreiving the data.")
      print("This is the error: "+data['value'])
      time.sleep(10)
       continue
    print("This is the value "+data['value'])   
    sensor_value=0
    try:
      sensor_value = int(data['value'])
    except e:
      print("There was an error while parsing the response: ", e)
      continue
    bound = compute_bounds(history_data, conf.FRAME_SIZE, conf.MUL_FACTOR)
    if not bound:
      required_data_count = conf.FRAME_SIZE - len(history_data)
      print("Not enough data to compute Z-score. Need ", required_data_count, " more data points")
      history_data.append(int(data['value']))
      time.sleep(10)
      continue
    try:
      if sensor_value>bound[0]:
        response = mailer.send_email("Alert","The temperature increased suddenl, someone open the fridge door. Sending an E-mail.")
        response_text=json.loads(response.text)
      elif sensor_value<bound[1]:
        response = mailer.send_email("Alert", "The temperature decrease suddenly. Sending an E-mail.")
        response_text=json.loads(response.text)
      except Exception as e:
        print("Error occured: Bellow are the details")
        print(e)
        time.sleep(10)
