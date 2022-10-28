"""
****** Important! *******
If you run this app locally, un-comment line 113 to add the ThemeChangerAIO component to the layout
"""

from dash import Dash, dcc, html, dash_table, Input, Output, callback
import plotly.express as px
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import ThemeChangerAIO, template_from_url
from dash import Dash, html ,dcc
import pandas as pd
from datetime import datetime
import MetaTrader5 as mt5
import pandas as pd
import pytz
import plotly.graph_objects as go
from keras.models import load_model
from sklearn.preprocessing import MinMaxScaler
import plotly.offline as pyo
import numpy as np
from sklearn.preprocessing import MinMaxScaler

if not mt5.initialize():
    print("initialize() failed, error code =",mt5.last_error())
    quit()
# mise a jour du time zone gmt+1 (tunisia time )
timezone = pytz.timezone("Etc/GMT-5")
#utc_from = datetime(2022, 1, 3,0, tzinfo=timezone)
#Date debut
date_start = datetime(2021,12, 31, tzinfo=timezone)
#Date fin
date_end = datetime.now()
# obtenir des donnÃƒÂ©es , EURUSD , TIMEFRAME_M15 =>(chaque 15 min) ÃƒÂ  partir du 31.12.2021 jusqu'ÃƒÂ  1.4.2022 dans le fuseau horaire GMT+1
rates = mt5.copy_rates_range("EURUSD", mt5.TIMEFRAME_M15,date_start, date_end)
# creation du dataframe
rates_frame = pd.DataFrame(rates)
rates_frame['time']=pd.to_datetime(rates_frame['time'], unit='s')
rates_frame.set_index('time')
rates_frame=rates_frame.drop(columns=['tick_volume','real_volume','spread','open','high','low'])


rates_frame['close_HV'] = rates_frame['close'].pct_change().rolling(
            window=60,  # 60 points * 15

              # half the window size
        ).std()



df = rates_frame


# stylesheet with the .dbc class

dbc_css = "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates/dbc.min.css"
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP, dbc_css])

header = html.H4(
    "Historical Volatility", className="bg-primary text-white p-2 mb-2 text-center"
)

table = dash_table.DataTable(
    id="table",
    columns=[{"name": i, "id": i, "deletable": True} for i in df.columns],
    data=df.to_dict("records"),
    page_size=10,
    editable=True,
    cell_selectable=True,
    filter_action="native",
    sort_action="native",
    style_table={"overflowX": "auto"},
    row_selectable="multi",
)



MODEL_PATH = 'histo_model_f.h5'
model = load_model(MODEL_PATH)
training_set = rates_frame.iloc[:, 1:2].values

sc = MinMaxScaler(feature_range = (0, 1))
training_set_scaled = sc.fit_transform(training_set)


X_test = []
for i in range(700 , 1251):
 X_test.append(training_set_scaled[i-60:i, 0])
X_test = np.array(X_test)
X_test = np.reshape(X_test, (X_test.shape[0], X_test.shape[1], 1))
pred=model.predict(X_test)

data=rates_frame[700:1251]
data['train']=training_set_scaled[700:1251]
data['pred']=pred






tab1 = dbc.Tab([dcc.Graph(id="line-chart" , figure={'data':[ {'x':df.time,'y':df.close}]}   ) , ], label="Close Volatility"  )
tab2 = dbc.Tab([dcc.Graph(id="line-chart2" , figure={'data':[ {'x':data.time,'y':data.pred}, {'x':data.time,'y':data.train}   ]}   ) , ], label="Predict Close Volatility ( LSTM)")
tab3 = dbc.Tab([table], label="Table", className="p-4")
tabs = dbc.Card(dbc.Tabs([tab1, tab2, tab3]))



app.layout = dbc.Container(
    [
        header,
        dbc.Row(
            [
                dbc.Col(
                    [

                        # When running this app locally, un-comment this line:
                         ThemeChangerAIO(aio_id="theme")
                    ],
                    width=1,
                ),
                dbc.Col([tabs], width=8),
            ]
        ),
    ],
    fluid=True,
    className="dbc dbc-row-selectable",
)






if __name__ == "__main__":
    app.run_server(debug=True)