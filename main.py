import json

from deepparse.pre_processing import address_cleaner
from fastapi import FastAPI
from deepparse.parser import AddressParser


app = FastAPI()


@app.get("/parse-address/{address}")
async def say_hello(address: str):
    address_parser = AddressParser(model_type="lightest", device="cpu")
    address = address_cleaner.coma_cleaning(address)
    address = address_cleaner.lower_cleaning(address)
    address = address_cleaner.trailing_whitespace_cleaning(address)
    address = address_cleaner.double_whitespaces_cleaning(address)
    address = address_cleaner.hyphen_cleaning(address)
    adr_dict = address_parser(address).to_dict()

    title_parts = ['StreetName', 'Municipality', 'Province']
    for part in title_parts:
        adr_dict[part] = adr_dict[part].title() if adr_dict[part] is not None else "None"
    upper_case_parts = ['Province']
    for part in upper_case_parts:
        adr_dict[part] = adr_dict[part].upper() if adr_dict[part] is not None else "None"
    json_adr = json.dumps(adr_dict)
    return {"address": json_adr}
