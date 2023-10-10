import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

pd.set_option("display.max_rows", None, "display.max_columns", None)

df = pd.read_csv("so4.txt", sep=",")

data = df.to_dict('dict')
reformatted = {}

for values in data.items():
    temp = []
    for v_sub in values[1].values():
        temp.append(v_sub)
    reformatted[values[0]] = temp

fig, ax = plt.subplots()

print(reformatted)

for key, vector in reformatted.items():
    if key != 'annee':
        coefficients = np.polyfit(reformatted['annee'],vector,2)
        fit = np.poly1d(coefficients)
        plt.plot(reformatted['annee'], vector,label=key) #'--k'=black dashed line, 'yo' = yellow circle marker
        plt.plot(reformatted['annee'], fit(reformatted['annee']), linewidth=0.6)
        # plt.plot(reformatted['annee'], vector, label=key)
        plt.scatter(reformatted['annee'], vector)

# Set final plot params
plt.legend(loc='upper right', numpoints = 1 )
plt.xlabel ('Année', fontsize=16)
plt.ylabel ('Émissions en millier de tonnes', fontsize=16)
plt.title('Émissions de SO$_2$ en France', fontsize=16)  
plt.grid()
plt.show()