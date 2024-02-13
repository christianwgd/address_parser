import json

from deepparse.pre_processing import address_cleaner
from fastapi import FastAPI, HTTPException, Security, Request, status
from deepparse.parser import AddressParser
from fastapi.exceptions import RequestValidationError
from fastapi.security import APIKeyHeader
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

app = FastAPI()


routes_with_custom_exception = ['/']

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    if request.url.path in routes_with_custom_exception:
        # check whether the error relates to the `some_custom_header` parameter
        for err in exc.errors():
            if err['loc'][0] == 'header' and err['loc'][1] == 'some-custom-header':
                return JSONResponse(content={'401': 'Unauthorized'}, status_code=401)

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder({'detail': exc.errors(), 'body': exc.body}),
    )


api_keys = [
    "my_api_key"
]


api_key_header = APIKeyHeader(name="X-API-Key")


def get_api_key(api_key_header: str = Security(api_key_header)) -> str:
    if api_key_header in api_keys:
        return api_key_header
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or missing API Key",
    )


@app.get("/parse-address/")
async def say_hello(address: str, api_key: str = Security(get_api_key)):
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
