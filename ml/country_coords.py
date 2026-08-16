"""
Capital-city coordinates for each country in the dataset, used as a
representative point for querying NASA POWER's climate API. This is a
simplification -- real climate varies across a country -- disclosed as
such in methodology.json rather than hidden. Coordinates are real capital
city locations (lat, lon).
"""

CAPITAL_COORDS = {
    "DZA": (36.7538, 3.0588),    # Algiers
    "AGO": (-8.8390, 13.2894),   # Luanda
    "BEN": (6.4969, 2.6289),     # Porto-Novo
    "BWA": (-24.6282, 25.9231),  # Gaborone
    "BFA": (12.3714, -1.5197),   # Ouagadougou
    "BDI": (-3.3822, 29.3644),   # Bujumbura
    "CPV": (14.9330, -23.5133),  # Praia
    "CMR": (3.8480, 11.5021),    # Yaounde
    "CAF": (4.3947, 18.5582),    # Bangui
    "TCD": (12.1348, 15.0557),   # N'Djamena
    "COM": (-11.7042, 43.2402),  # Moroni
    "COD": (-4.4419, 15.2663),   # Kinshasa
    "COG": (-4.2634, 15.2429),   # Brazzaville
    "CIV": (6.8276, -5.2893),    # Yamoussoukro
    "GNQ": (3.7523, 8.7742),     # Malabo
    "ERI": (15.3229, 38.9251),   # Asmara
    "SWZ": (-26.3054, 31.1367),  # Mbabane
    "ETH": (9.0320, 38.7469),    # Addis Ababa
    "GAB": (0.4162, 9.4673),     # Libreville
    "GMB": (13.4549, -16.5790),  # Banjul
    "GHA": (5.6037, -0.1870),    # Accra
    "GIN": (9.6412, -13.5784),   # Conakry
    "GNB": (11.8636, -15.5977),  # Bissau
    "KEN": (-1.2921, 36.8219),   # Nairobi
    "LBR": (6.3005, -10.7969),   # Monrovia
    "MDG": (-18.8792, 47.5079),  # Antananarivo
    "MWI": (-13.9626, 33.7741),  # Lilongwe
    "MLI": (12.6392, -8.0029),   # Bamako
    "MRT": (18.0735, -15.9582),  # Nouakchott
    "MUS": (-20.1609, 57.5012),  # Port Louis
    "MOZ": (-25.9692, 32.5732),  # Maputo
    "NAM": (-22.5609, 17.0658),  # Windhoek
    "NER": (13.5127, 2.1128),    # Niamey
    "NGA": (9.0765, 7.3986),     # Abuja
    "RWA": (-1.9403, 29.8739),   # Kigali
    "STP": (0.3365, 6.7273),     # Sao Tome
    "SEN": (14.7167, -17.4677),  # Dakar
    "SLE": (8.4657, -13.2317),   # Freetown
    "ZAF": (-25.7479, 28.2293),  # Pretoria
    "SSD": (4.8517, 31.5825),    # Juba
    "TZA": (-6.1630, 35.7516),   # Dodoma
    "TGO": (6.1256, 1.2254),     # Lome
    "UGA": (0.3476, 32.5825),    # Kampala
    "ZMB": (-15.3875, 28.3228),  # Lusaka
    "ZWE": (-17.8252, 31.0335),  # Harare
}
