from state import TradingState

import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import cauchy 

class CauchyStrategy(): 

    def __init__(self, 
                 state: TradingState) -> None:
        self.state = state

        # SPX bounds
        self.UPPER = 4100
        self.LOWER = 4050

        # inventory limit
        self.POSITION_LIMIT = 40

        # TODO: not sure why this is static?
        self.SCALE = 10000

        # using the data from the previous day to fit the cauchy distribution
        df = pd.read_csv("../data/apr-10-spx.csv")

        # perform fit calculations
        df["returns"]=(df["SPX"]-df["SPX"].shift(1))/(df["SPX"].shift(1))
        df=df.drop(0)
        params = cauchy.fit(df["returns"])
        x0,gamma=params
        df["x0"]=x0*(27513-df["Index"])
        df["gamma"]=gamma*(27513-df["Index"])**(2/3)

        # df["mean"]=np.mean(df["returns"])*(27513-df["Index"])
        # df["std"]=np.std(df["returns"])*(27513-df["Index"])**(1/2)

        df["probability"] = cauchy.cdf((self.UPPER-df["SPX"])/df["SPX"],df["x0"], df["gamma"]) - cauchy.cdf((self.LOWER-df["SPX"])/df["SPX"],df["x0"], df["gamma"])
        # df["probability_norm"] = norm.cdf((self.UPPER-df["SPX"])/df["SPX"], df["mean"], df["std"]) - norm.cdf((self.LOWER-df["SPX"])/df["SPX"],  df["mean"], df["std"])

        self.df_ = df

        print("Strategy setup complete...")
        
    def kalshiUpdate(self) -> None: 
        orderbook = self.state.getOrderbook()
        if len(orderbook["bids"]) == 0 or len(orderbook["asks"]) == 0: 
            print("no orders")
            return

        mid = self.df_["probability"]

        bid_vol = min(10, self.POSITION_LIMIT - self.state.position)
        ask_vol = min(10, self.POSITION_LIMIT + self.state.position)

        bid_price = mid- self.df_["gamma"] * self.SCALE
        ask_price = mid + self.df_["gamma"] * self.SCALE
        
        if self.state.position >=0:
            bid_price -= self.df_["gamma"] * self.state.position
            ask_price -= min(self.df_["gamma"] * self.state.position, self.df_["gamma"] * self.SCALE)
        else:
            bid_price -= max(self.df_["gamma"] * self.state.position, -self.df_["gamma"] * self.SCALE)
            ask_price -= self.df_["gamma"] * self.state.position

        self.state.insertOrder("B", bid_price, bid_vol)
        self.state.insertOrder("A", ask_price, ask_vol)
       
    def spUpdate(self) -> None: 
        pass