from fastapi import FastAPI
from market.market import market_router
from accounts.accounts import account_router
from warehouse.warehouse import warehouse_router

app = FastAPI()
app.include_router(market_router, prefix="/market")
app.include_router(account_router, prefix="/accounts")
app.include_router(warehouse_router, prefix='/warehouse')


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}
