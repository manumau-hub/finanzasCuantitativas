from fastapi import FastAPI, Depends
from enum import Enum
from typing import Optional
from pydantic import BaseModel

from app.Codigo.opcion_europea_bs import opcion_europea_bs
from app.Codigo.opcion_europea_bin import opcion_europea_bin
from app.Codigo.opcion_europea_mc import opcion_europea_mc

app = FastAPI()

class Model(str, Enum):
    BS = 'BS'
    BIN = 'BIN'
    MC = 'MC'

class OptionParameters(BaseModel):
    tipo: str = 'C'
    S: float = 100.0
    K: float = 100.0
    T: float = 1.0
    r: Optional[float] = 0.01
    sigma: Optional[float] = 0.1
    div: Optional[float] = 0.0
    model: Model = Model.BS

@app.get("/price/options/bs")
async def root(params: OptionParameters = Depends()):

    if params.model == Model.BS:
        price = opcion_europea_bs(tipo=params.tipo,
                                  S=params.S,
                                  K=params.K,
                                  T=params.T,
                                  r=params.r,
                                  sigma=params.sigma,
                                  div=params.div)
    elif params.model == Model.BIN:
         price = opcion_europea_bin(tipo=params.tipo,
                                  S=params.S,
                                  K=params.K,
                                  T=params.T,
                                  r=params.r,
                                  sigma=params.sigma,
                                  div=params.div,
                                  pasos=1000)
    elif params.model == Model.MC:
         price = opcion_europea_mc(tipo=params.tipo,
                                  S=params.S,
                                  K=params.K,
                                  T=params.T,
                                  r=params.r,
                                  sigma=params.sigma,
                                  div=params.div,
                                  pasos=1000000)

    return {'price': price, 'modelo': params.model}
