from FirebaseManager import connect_to_firebase
import pandas as pd


def add_time_cooking(x, start_time):
    return (x-start_time).total_seconds()

def get_data_from_firebase(db, user_id):

    dfs = []

    docs = db.collection(user_id).get()

    for doc in docs:
        data = db.collection(user_id).document(doc.id).collection('data').order_by(u'timestamp').get()
        data_array = [{'temp': entry._data['temp'], 'timestamp': entry._data['timestamp']} for entry in data]

        temp_df = pd.DataFrame(data_array)
        temp_df['cook_id'] = doc.id
        temp_df['user'] = user_id
        temp_df['grill_type'] = doc.to_dict()['smoker']
        temp_df['meat_type'] = doc.to_dict()['meat']

        start_time = temp_df['timestamp'].iloc[0]
        temp_df['time_cooking'] = temp_df['timestamp'].apply(lambda x: add_time_cooking(x, start_time))

        dfs.append(temp_df)

    df = pd.concat(dfs)

    return df

if __name__ == "__main__":
    db = connect_to_firebase("briskless_firebase_auth.json")

    dfs = []
    for user_id in [u'GALLAGHER_NICK', u'LINDLEY_DAVE']:
        df = get_data_from_firebase(db, user_id)
        dfs.append(df)

    df = pd.concat(dfs)
    df.to_csv('test.csv', index=False)
