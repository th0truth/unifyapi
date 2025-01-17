import requests

# token = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMTY4MDYwMCIsImV4cCI6MTczNzEwNDk3MywiaWF0IjoxNzM3MTAzNzczfQ.MknCCLEqOqJidss5I9TF59d-JRpo3Zgax-1XRa93_SxzLpgLD2U4o1jekWqvtDVJlhULl9DrTUoL2vNBv42WgJj_HoM74cs9scnSKEIN5wN2nXPOXgaiSHitK5cjP-bVuwawX0DVU0JzmgBOMsFgX8I0tweoW0gLmVqgjuTzJI3l6AFy0wDlsPjaddhxEhWDXDkhomjlPOKsQQjnQlNPXw-AvOJuKxNADsSBzLNedVcCIzdIto6KgQ_lp6ApSEK3eUppoBgOdfEuXTH1e_-tjW-DBUJGaG2i5ZUtWpL5NMn4CHiNlJwCEGR6NiQRCH5aNLwdT00WB_8fl7f1vc5iPg"

token = input(": ")

r = requests.get("http://0.0.0.0:10000/api/v1/students/me/", headers={"Authorization": token})
print(r.headers)

print(r.text)