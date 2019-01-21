from FirebaseManager import connect_to_firebase
import pandas as pd

db = connect_to_firebase("briskless_firebase_auth.json")


user_id = u'GALLAGHER_NICK'

docs = db.collection(user_id).get()

dfs = []
for doc in docs:
    data = db.collection(user_id).document(doc.id).collection('data').get()
    data_array = [{'temp': entry._data['temp'], 'time': entry._data['time']} for entry in data]

    temp_df = pd.DataFrame(data_array)
    temp_df['user'] = user_id
    temp_df['grill_type'] = doc.to_dict()['smoker']
    temp_df['meat_type'] = doc.to_dict()['Meat']

    dfs.append(temp_df)

df = pd.concat(dfs)
print(df)