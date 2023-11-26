import pandas as pd
from rymscraper import rymscraper, RymUrl
import sys



arg = sys.argv

genre = arg[1]
filename_out = arg[2] 
print(genre)
print(filename_out)

network = rymscraper.RymNetwork()
network = rymscraper.RymNetwork()
rym_url = RymUrl.RymUrl(genres=genre) 

chart_infos = network.get_chart_infos(rym_url,max_page=126)
df = pd.DataFrame(chart_infos)
df[['Rank', 'Artist', 'Album', 'RYM Rating', 'Ratings']]

network.browser.close()
network.browser.quit()

df.to_csv(filename_out, sep=';', encoding='utf-8')
