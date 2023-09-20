import gspread
import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials

scope = ["https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive.file",
        "https://www.googleapis.com/auth/drive"]

creds = ServiceAccountCredentials.from_json_keyfile_name("private-key.json", scope)

client = gspread.authorize(creds)

# Open the spreadhseet
sheet = client.open("radioactivité_puy_de_la_poix").sheet1
data = sheet.get_all_records()
data1 = sheet.get_all_records() 

headers = data1.pop(0)

df = pd.DataFrame(data, columns=headers)
print(df)

# Compute linear regression : 
x_data = df['dist.(metres)']
y_data = df['moyenne(mS/cm)']
x_mean = sum(x_data) / len(x_data)
y_mean = sum(y_data) / len(y_data)
covar = sum((xi - x_mean) * (yi - y_mean) for xi, yi in zip(x_data, y_data))
x_var = sum((xi - x_mean)**2 for xi in x_data)
beta = covar / x_var
alpha = y_mean - beta * x_mean
y_hat = [alpha + beta * xi for xi in x_data]

plt.scatter(
    df['dist.(metres)'], 
    df['moyenne(mS/cm)'],
    color='black',
    label='Moyenne de radioactivité'
)
plt.plot(
    df['dist.(metres)'], 
    df['moyenne(mS/cm)'],
    color='darkblue',
    linewidth=0.3,
)

# Plot linear regression
plt.plot(
    x_data, 
    y_data, 
    x_data, 
    y_hat,
    label='Courbe de tendance',
    color='black',
    linewidth=0.2,
)

plt.errorbar(
    df['dist.(metres)'], 
    df['moyenne(mS/cm)'],
    yerr=df['std_dev'],
    capsize = 4,
    ecolor='darkred',
    label='Écart-type'
)

# Add annotations for rad. values: 
x = df['dist.(metres)'].values.tolist()
y = df['moyenne(mS/cm)'].values.tolist()
 
for i in range(0, len(y)):
    plt.annotate(' ' + str(y[i]) + 'mS/cm', (x[i], y[i]), fontsize=9)



plt.xticks(df['dist.(metres)'], color='black')
plt.xlabel ('Distance du centre en mètres')
plt.ylabel ('Radioactivité en mS/cm')
plt.title('Figure 4 : Mesures de radioactivité sur transect 1')

handles, labels = plt.gca().get_legend_handles_labels()
by_label = dict(zip(labels, handles))
plt.legend(by_label.values(), by_label.keys())


plt.show()