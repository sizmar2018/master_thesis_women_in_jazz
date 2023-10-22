import pandas as pd
from rymscraper import rymscraper, RymUrl

network = rymscraper.RymNetwork()
network = rymscraper.RymNetwork()
rym_url = RymUrl.RymUrl(genres="Jazz")
chart_infos = network.get_chart_infos(url=rym_url, max_page=126)
df = pd.DataFrame(chart_infos)
df[['Rank', 'Artist', 'Album', 'RYM Rating', 'Ratings']]

album_infos = network.get_album_infos(name="Mingus - The Black Saint and the Sinner Lady")
df = pd.DataFrame([album_infos])

network.browser.close()
network.browser.quit()

df.to_csv("rym_charts.csv", sep=';', encoding='utf-8')