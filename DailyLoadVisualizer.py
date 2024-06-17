#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 12 12:53:45 2024

@author: ryanweightman
"""
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar 13 11:50:02 2024

@author: ryanweightman
"""
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
dfAE=pd.read_csv("data/AELoadDaily.csv")
dfJC=pd.read_csv("data/JCLoadDaily.csv")
dfPSEG=pd.read_csv("data/PSEGLoadDaily.csv")
dfReco=pd.read_csv("data/RecoLoadDaily.csv")

print(dfAE['mw'].sum()+dfJC['mw'].sum()+dfPSEG['mw'].sum()+dfReco['mw'].sum())

plt.plot(dfAE['date'], dfAE['mw'], linestyle = 'solid', label='AE')
#plt.title('Time Series Plot')
#plt.xlabel('Time')
#plt.ylabel('Value')
matplotlib.pyplot.locator_params(axis='x', nbins=10)
plt.xticks(range(1,366,20),rotation=45)

plt.plot(dfJC['date'], dfJC['mw'], linestyle = 'solid', label='JC')
#plt.title('Time Series Plot')
#plt.xlabel('Time')
#plt.ylabel('Value')
matplotlib.pyplot.locator_params(axis='x', nbins=10)
plt.xticks(range(1,366,20),rotation=45)

plt.plot(dfPSEG['date'], dfPSEG['mw'], linestyle = 'solid', label='PSEG')
#plt.title('Time Series Plot')
#plt.xlabel('Time')
#plt.ylabel('Value')
matplotlib.pyplot.locator_params(axis='x', nbins=10)
plt.xticks(range(1,366,20),rotation=45)

plt.plot(dfReco['date'], dfReco['mw'], linestyle = 'solid', label='Reco')
plt.title('Load Over Time')
plt.xlabel('Time')
plt.ylabel('MWh')
matplotlib.pyplot.locator_params(axis='x', nbins=10)
plt.xticks(range(1,366,30),rotation=45)
plt.legend(loc="upper right")



dfSUM = pd.DataFrame()
dfSUM['date']=dfJC['date']
dfSUM['load'] = dfAE['mw'] + dfJC['mw']+dfPSEG['mw'] + dfReco['mw']


dfSUM.to_csv('data/TotalNJLoadDaily.csv', index=False)